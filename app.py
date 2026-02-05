import streamlit as st
import ustrade as ut
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plots
from datetime import timedelta
import time

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(1200px 600px at 10% 0%, rgba(255,255,255,0.10), transparent 60%),
            radial-gradient(900px 500px at 90% 10%, rgba(255,255,255,0.08), transparent 55%),
            radial-gradient(700px 420px at 50% 90%, rgba(255,255,255,0.06), transparent 60%),
            #151a21;
        color: rgba(255,255,255,0.92);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(layout="wide")

if "requested" not in st.session_state:
    st.session_state.requested = False

if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.df_sub = None

c = ut.CensusClient(timeout=60)


@st.cache_data(show_spinner=False)
def get_exp(cty, prod, beg_date, end_date):
    return c.get_exports_on_period(cty, prod, beg_date, end_date)

@st.cache_data(show_spinner=False)
def get_imp(cty, prod, beg_date, end_date):
    return c.get_imports_on_period(cty, prod, beg_date, end_date)

def fetch_with_retries(fn, *args, attempts=10, sleep_s=0.5):
    last_err = None
    warned = st.session_state.get("census_slow_msg_shown", False)
    placeholder = st.markdown("Fetching your data...")

    for _ in range(attempts):
        try:
            out = fn(*args)
            placeholder.empty()
            return out
        except Exception as e:
            last_err = e
            if not warned:
                placeholder.markdown("This request is taking longer than expected. "
                                    "This may be due to high traffic on the Census Bureau API or the size of the request. "
                                    "Waiting a little longer usually resolves the issue, or you can try again later.")
                st.session_state["census_slow_msg_shown"] = True
                warned = True
            time.sleep(sleep_s)

    placeholder.empty()
    raise RuntimeError(f"Request failed after {attempts} attempts") from last_err


st.title("U.S. Trade Analytics")


flow = st.sidebar.selectbox("Flow", ("Imports", "Exports"))
cty = st.sidebar.text_input("Country", "Mexico")
prod = st.sidebar.text_input("Product", "08")


try : c.get_product(prod)
except : st.error(f"HS Code {prod} could not be found. ")


try : 
    c_obj = c.get_country_by_name(cty)
except:        
    try :
        c_obj = c.get_country_by_code(cty)
    except:
        try :
            c_obj = c.get_country_by_iso2(cty)
        except: st.error(f"{cty} could not be found as a country name, code or ISO2.")

cty_name = c_obj.name

beg_date = (st.sidebar.date_input("Beginning date", value = "2021-01-01", format = "YYYY/MM/DD"))
beg_date_minus1 = beg_date -timedelta(days=365)
beg_date_str = str(beg_date)[:-3]
beg_date_minus1_str = str(beg_date_minus1)[:-3]

end_date = (st.sidebar.date_input("End date", value = "2026-01-01", format = "YYYY/MM/DD"))
end_date_str = str(end_date)[:-3]

mapper = {"import_value" : "value", "export_value" : "value"}
if len(prod) < 6: 
    ch_code_desc = (ut.get_children_codes(prod))
    ch_code = list(ch_code_desc.keys())
else : ch_code = False

if st.sidebar.button("Request", shortcut = "Cmd+Enter"):
    st.session_state.requested = True

if st.session_state.requested:
    if flow == "Imports":
        df = fetch_with_retries(get_imp, cty, prod, beg_date_minus1_str, end_date_str)
        if ch_code: df_sub = fetch_with_retries(get_imp, cty, ch_code, beg_date_str, end_date_str)

    if flow == "Exports":
        df = fetch_with_retries(get_exp, cty, prod, beg_date_minus1_str, end_date_str)
        if ch_code: df_sub = fetch_with_retries(get_exp, cty, ch_code, beg_date_str, end_date_str)


    df = df.rename(mapper, axis = 1)
    if ch_code : df_sub = df_sub.rename(mapper, axis = 1)

    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.set_index("date")

    df_yoy = round((df["value"] / df["value"].shift(12)).dropna()*100 -100, 2)
    df = df[df.index >= beg_date]
    if ch_code : df_sub.groupby("product_name")["value"].sum()


    st.markdown(f"#### :blue[**{flow}**] of :green[**{ut.get_desc_from_code(prod).lower()}**] {"from" if flow == "Imports" else "to"} :orange[**{cty_name}**]")
    
    
    st.divider()
    with st.container(border=True):

        title = (f"Monthly {flow.lower()} of {ut.get_desc_from_code(prod).lower()} {"from" if flow == "Imports" else "to"} {cty_name}")
        x = df.index
        y = df["value"]
        st.plotly_chart(plots.bar_chart(x, y, title))

    with st.container(border=True):
        title = f"YoY % evolution of {flow.lower()} {"from" if flow == "Imports" else "to"} {cty_name} ({beg_date_str} to {end_date_str})"
        st.plotly_chart(plots.line_chart(df_yoy.index, df_yoy, title))
        
        

    with st.container(border=True) : 
        title = f"Subcategories of HS code {prod}"
        if ch_code : 
            pie_chart = plots.pie_chart(df_sub, title)
            st.plotly_chart(pie_chart)
        else: st.text(f"HS Code {prod} is a subheading code and does not have subcategories.")

    if ch_code : df_desc_code = pd.DataFrame(ch_code_desc.items(), columns=["Children codes", "description"])

    with st.container(border = True):
        col1, col2= st.columns(2)
        with col1:
            df_disp = df["value"]
            st.dataframe(df_disp)
        with col2:
            if ch_code: st.dataframe(df_desc_code)
            
    st.session_state.requested = False
        
with st.container(border=True):    
    st.subheader("HS Code Lookup")
    st.markdown(
        f"""
        The **Harmonized Commodity Description and Coding System** (HS) is the international standard for classifying traded products.
        It is structured hierarchically into **chapters** (2 digits), **headings** (4 digits), and **subheadings** (6 digits).
        When a digit is less than 10, a leading zero must be added (e.g. '8' → '08').
        """
    )
    st.divider()
    st.markdown("#### Search the description of a code & subcodes")
    check_code = st.text_input("HS Code", width = 200, value = "08")
    try:
        prod_code = ut.get_product(check_code)
        st.text(f"Description : {prod_code.description}")
        child_check_codes = ut.get_children_codes(check_code)
        if len(child_check_codes)>0:
            df_child_code =pd.DataFrame(child_check_codes.items(), columns=["Associated codes", "description"])
            
            st.dataframe(df_child_code)
    except : 
        st.text(f"HS code {check_code} could not be found.")

    st.divider()
    st.markdown("#### Search a code with keyword")
    col1, col2 = st.columns(2)
    with col1:
        check_desc = st.text_input("Keywords", width = 200, value = "oil")
    with col2:
        in_codes = st.text_input("In headings/subheadings", width = 200, value = "").strip()
        if len(in_codes) == 0: in_codes = None
        else :
            try :
                ut.get_product(in_codes)
            except:
                st.markdown(f":red[HS Code {in_codes} could not be found. Returning all results.]")
                in_codes = None
    df_search = ut.search_for_code(check_desc, mode = "AND", in_codes = in_codes)
    if df_search.empty:
        st.markdown("The research did not return any results")
    else : st.dataframe(df_search)
    

with st.container(border = True):
    st.markdown("##### Credits")
    st.markdown("This application relies on the API of the United States Census Bureau accessed through the [ustrade](https://github.com/fantinsib/ustrade) module. For more details, go to https://www.census.gov/data/developers.html. ")
    st.markdown("Contributions to this project are welcome. Feel free to open an issue on [GitHub](https://github.com/fantinsib/ustrade_dashboard) or submit a pull request for any bugs or improvement suggestions.")


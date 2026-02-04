import streamlit as st
import ustrade as ut
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import timedelta
import time

st.set_page_config(layout="wide")

if st.sidebar.button("Clear cache"): 
    st.cache_data.clear()
    st.session_state.clear()
    st.rerun()

if "requested" not in st.session_state:
    st.session_state.requested = False

if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.df_sub = None

c = ut.CensusClient(timeout=600)


@st.cache_data(show_spinner = False)
def get_exp(cty, prod, beg_date, end_date):
    for _ in range(5):
        try:
            return c.get_exports_on_period(cty, prod, beg_date, end_date)
        except Exception as e:
            last_err = e
            time.sleep(0.5)
    raise RuntimeError("Exports request failed after 5 attempts") from last_err

@st.cache_data(show_spinner = False)
def get_imp(cty, prod, beg_date, end_date):
    for _ in range(5):
        try:
            return c.get_imports_on_period(cty, prod, beg_date, end_date)
        except Exception as e:
            last_err = e
            time.sleep(0.5)
    raise RuntimeError("Imports request failed after 5 attempts") from last_err

st.title("U.S. Trade Analytics")

flow = st.sidebar.selectbox("Flow", ("Imports", "Exports"))
cty = st.sidebar.text_input("Country", "Mexico")
prod = st.sidebar.text_input("Product", "08")


try : c.get_product(prod)
except : st.error(f"HS Code {prod} could not be found. ")


try : 
    c.get_country_by_name(cty)
except:        
    try :
        c.get_country_by_code(cty)
    except:
        try :
            c.get_country_by_iso2(cty)
        except: st.error(f"{cty} could not be found as a country name, code or ISO2.")

beg_date = (st.sidebar.date_input("Beginning date", value = "2021-01-01", format = "YYYY/MM/DD"))
beg_date_minus1 = beg_date -timedelta(days=365)
beg_date_str = str(beg_date)[:-3]
beg_date_minus1_str = str(beg_date_minus1)[:-3]

end_date = (st.sidebar.date_input("End date", value = "2025-01-01", format = "YYYY/MM/DD"))
end_date_str = str(end_date)[:-3]

mapper = {"import_value" : "value", "export_value" : "value"}
if len(prod) < 6: 
    ch_code_desc = (ut.get_children_codes(prod))
    ch_code = list(ch_code_desc.keys())
else : ch_code = False

if st.sidebar.button("Call"):
    st.session_state.requested = True

if st.session_state.requested:
    if flow == "Imports":
        df = get_imp(cty, prod, beg_date_minus1_str, end_date_str)
        if ch_code:
            df_sub = get_imp(cty, ch_code, beg_date_str, end_date_str)

    if flow == "Exports":
        df = get_exp(cty, prod, beg_date_minus1_str, end_date_str)
        if ch_code: df_sub = get_exp(cty, ch_code, beg_date_str, end_date_str)


    df = df.rename(mapper, axis = 1)
    df_sub = df_sub.rename(mapper, axis = 1)

    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.set_index("date")

    df_yoy = round((df["value"] / df["value"].shift(12)).dropna()*100 -100, 2)
    df = df[df.index >= beg_date]
    df_sub.groupby("product_name").sum("value")

    fig = px.pie(df_sub, values = "value", names = "product_name")

    st.text(f"{flow} of '{ut.get_desc_from_code(prod)}' {"from" if flow == "Imports" else "to"} {cty}")
    with st.container(border=True):
        col1, col2= st.columns(2)
        with col1:
            df_disp = df["value"]
            st.bar_chart(df_disp, x_label = "Date", y_label = "Value")
        with col2:
            st.line_chart(data= df_yoy, x_label = "Date", y_label = "% YoY Growth", color = (255,0,0))

            


    with st.container(border=True) : st.plotly_chart(fig)

    if ch_code : df_desc_code = pd.DataFrame(ch_code_desc.items(), columns=["Children codes", "description"])

    with st.container(border = True):
        col1, col2= st.columns(2)
        with col1:
            st.dataframe(df_disp)
        with col2:
            if ch_code: st.dataframe(df_desc_code)
            
    st.session_state.requested = False
        
with st.container(border=True):    
    st.subheader("HS Code Lookup")
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



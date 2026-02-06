import plotly.graph_objects as go


def pie_chart(df, title = None):
    """
    Constructs the pie chart graph 
    """
    pie_chart = go.Figure( data = [
    go.Pie(labels = df["product_name"], values = df["value"])
    ]


    )
    pie_chart.update_layout(
    title = dict(text = title,x=0.5,xanchor="center"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.92)"),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)"
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)"
    ),
    )
    return pie_chart


def bar_chart(x, y, title = None):
    bar_chart = go.Figure(
        data = go.Bar(
            x = x,
            y = y,
            marker = dict(color='rgba(255, 190, 110, 0.7)',
            line = dict(color = "rgba(255, 190, 110, 1)", width =1.5)
        )
        )
    )

    bar_chart.update_layout(
    title = dict(text = title,x=0.5,xanchor="center"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.92)"),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)"
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)"
    ),
    )


    return bar_chart



def line_chart(x,y, title):
    bar_chart = go.Figure(
        data = go.Bar(
            x = x,
            y = y,
            marker = dict(color='rgba(183, 216, 197, 0.7)',
                          line = dict(color = "rgba(183, 216, 197, 1.0)", width =1.5)
        ),
    
    ))

    bar_chart.update_layout(
    title = dict(text = title,x=0.5,xanchor="center"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.92)"),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)"
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)"
    ),
    )


    return bar_chart



"""
def line_chart(x, y):

    line_chart = go.Figure(
        data = go.Scatter(
            x = x, 
            y= y,
            mode = "lines+markers",
            line = dict(dash = "dash", color = "rgba(255,255, 255, 1)"),
            marker= dict(size = 8, symbol = "circle", color = "rgba(255, 0,0,1)",line=dict(width=1,color="rgba(0,0,0,0.5)"))
    )
)

    line_chart.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.92)"),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)"
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)"
    ),
    )

    return line_chart

"""
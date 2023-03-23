import dash
from dash import html, dcc
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output, ClientsideFunction
import plotly.express as px
import numpy as np
import pandas as pd
import altair as alt

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(
    __name__, external_stylesheets=external_stylesheets)

FACTOR_1 = 'population'
FACTOR_2 = 'violent_crime_rate'
server = app.server
app.config.suppress_callback_exceptions = True

#Tab Style
tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'navy',
    'padding': '6px'
}

# Read data
df = pd.read_csv("../data/processed_communities.csv")


state_list = df["state"].unique()
state_list = np.append('All', state_list,)

column_list = {'population': 'Population',
               'PopDens': 'Population Density',
               'racepctblack': 'Black Race Percentage',
               'racePctWhite': 'White Race  Density',
               'racePctAsian': 'Asian Race  Density',
               'agePct12t29': 'Age Percentage (12-29)',
               'agePct65up': 'Age Percentage (65+)',
               'medIncome': 'Median Income',
               'violent_crime_rate': 'Violent Crime Rate',
               'NumStreet': 'Number of Streets',
               'PctUnemployed': 'Number of Unemployed'
               }


app.layout = html.Div(
    id="app-container",
    children=[
        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[html.Div(
        id="description-card",
        children=[
            html.H3("Crime Rate Dashboard"),
            html.Div(
                id="intro",
                children="This is a dashboard for visualization of crime rate in US States in 1995. In the first tab, you will find an interactive map and in the second tab, you will find an interactive scatter plot. Play around with the dropdown menu and enjoy!"
            )
        ],
    )]
        ),
# Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                html.Div(
                    id="us-map-section",
                    children=[
                        dcc.Tabs(id='tabs', value='tab-1', children=[
                            dcc.Tab(label='Interactive Map', value='tab-1', style=tab_style, selected_style=tab_selected_style, children=[
                                html.Div([
                                    html.B("Interactive Map of Factors in Communities of United States"),
                                    dcc.Graph(id='map', figure={}),
                                    html.P("Select Factor for Map:"),
                                    dcc.Dropdown(id="factor-select-map",
                                                 options=[{"label": column_list[i], "value": i} for i in column_list],
                                                 value='population',),
                                ])
                            ]),
                            dcc.Tab(label='Scatter Plots', value='tab-2', style=tab_style, selected_style=tab_selected_style, children=[
                                html.Div([
                                    html.B("Scatter Plots of Factors by State"),
                                    html.Iframe(id='scatter',
                                                style={'border-width': '0', 'width': '100%', 'height': '400px'}),
                                    html.P("Select State:"),
                                     dcc.Dropdown(
                                         id="state-select",
                                         options=[{"label": i, "value": i} for i in state_list],
                                         value='All'),
                                    html.P("Select Factor 1:"),
                                    dcc.Dropdown(
                                        id="factor-select",
                                        options=[{"label": column_list[i], "value": i} for i in column_list],
                                        value='population'),
                                    html.P("Select Factor 2:"),
                                    dcc.Dropdown(
                                        id="factor-select-2",
                                        options=[{"label": column_list[i], "value": i} for i in column_list],
                                        value='violent_crime_rate')
                                    ])
                                ])
                            ], style=tabs_styles),
                        ])

                    ],
                ),
            ], style={
                    'backgroundColor': 'navy',
                    'padding': 20,
                    'color': 'navy',
                    'margin-top': 20,
                    'margin-bottom': 20,
                    'text-align': 'center',
                    'font-size': '20px',
                    'border-radius': 3}
        )


# Define the app callback
@app.callback(
    Output('map', 'figure'),
    [
        Input('state-select', 'value'),
        Input('factor-select-map', 'value')
    ],
)
    
def update_figure(state, column):
    global FACTOR_1
    # Define the map figure
    filtered_df = df
    
    if state != 'All' and state is not None:
        filtered_df = df[
            (df["state"] == state)
        ]
        
    if column is None:
        column = FACTOR_1
    else:
        FACTOR_1 = column

    fig = px.scatter_mapbox(df, 
                        lat="latitude", 
                        lon="longitude", 
                        hover_name="state", 
                        hover_data=["state", "area"],
                        color=column,
                        color_continuous_scale=[(0, 'darkblue'), (1,'lightblue')],
                        size=column,
                        zoom=3,
                        center={"lat": 44, "lon": -95},
                        height=800,
                        width=800,
                            labels={
                                 column: column_list[column]
                            },)

    # Update the layout of the figure
    fig.update_layout(mapbox_style="open-street-map",
                      margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


@app.callback(
    Output("scatter", "srcDoc"),
    [
        Input("state-select", "value"),
        Input("factor-select", "value"),
        Input("factor-select-2", "value"),
    ],
)
def plot_altair(state, column, column_2):
    global FACTOR_1, FACTOR_2
    filtered_df = df
    if state != 'All' and state is not None:
        filtered_df = df[
            (df["state"] == state)
            ]

    if column is None:
        column = FACTOR_1
    else:
        FACTOR_1 = column

    if column_2 is None:
        column_2 = FACTOR_2
    else:
        FACTOR_2 = column_2
        
    chart = alt.Chart(filtered_df).mark_point().encode(
        x=alt.X(column, title=column_list[column]),
        y=alt.Y(column_2, title=column_list[column_2]),
        tooltip=[column, column_2]).configure_mark(opacity=0.2, color='blue').interactive()
    
    return chart.to_html()


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
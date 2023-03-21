import altair as alt
from dash import dash, html
from vega_datasets import data
import dash_bootstrap_components as dbc
import dash_core_components as dcc


cars = data.cars()
chart = alt.Chart(cars).mark_point().encode(
    x='Horsepower',
    y='Displacement')

app = dash.Dash(__name__)
app.layout = html.Div([
        html.Iframe(srcDoc=chart.to_html())])

if __name__ == '__main__':
    app.run_server(debug=True) 
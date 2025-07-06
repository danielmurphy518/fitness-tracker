import dash
from dash import Dash, html, dcc, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import datetime
import os

CSV_PATH = 'data.csv'
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
else:
    df = pd.DataFrame(columns=['Date', 'Distance'])

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# Modal component for data entry
modal = html.Div([
    dbc.Button("Add New Entry", id="open", n_clicks=0),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Add New Data")),
            dbc.ModalBody([
                dbc.Label("Date (YYYY-MM-DD)"),
                dbc.Input(id="input-date", type="text", placeholder="2025-07-06"),
                dbc.Label("Distance (km)"),
                dbc.Input(id="input-distance", type="number", step=0.1, placeholder="e.g. 5.0"),
            ]),
            dbc.ModalFooter([
                dbc.Button("Submit", id="submit", n_clicks=0, className="ms-auto"),
                dbc.Button("Close", id="close", n_clicks=0, className="ms-2"),
            ]),
        ],
        id="modal",
        is_open=False,
    ),
])
# App layout
app.layout = html.Div([
    html.H4(f"Current Time: {datetime.datetime.now()}"),
    modal,
    html.Br(),
    dash_table.DataTable(id='table', data=df.to_dict('records'), page_size=10),
    dcc.Graph(id='graph', figure=px.histogram(df, x='Date', y='Distance', histfunc='avg'))
])
# Toggle modal open/close
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks"), Input("submit", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(open_clicks, close_clicks, submit_clicks, is_open):
    if open_clicks or close_clicks or submit_clicks:
        return not is_open
    return is_open
# Submit new data and update table + graph
@app.callback(
    [Output("table", "data"),
     Output("graph", "figure")],
    [Input("submit", "n_clicks")],
    [State("input-date", "value"),
     State("input-distance", "value")],
    prevent_initial_call=True
)
def add_entry(n_clicks, date_value, distance_value):
    print("add entry called?")
    if date_value and distance_value:
        new_row = pd.DataFrame([{"Date": date_value, "Distance": float(distance_value)}])
        # Append to CSV
        new_row.to_csv(CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH), index=False)
        # Reload DataFrame
        updated_df = pd.read_csv(CSV_PATH)
        # Return updated table and graph
        return updated_df.to_dict('records'), px.histogram(updated_df, x='Date', y='Distance', histfunc='avg')
    raise dash.exceptions.PreventUpdate
# Run the app
if __name__ == '__main__':
    app.run(debug=True)
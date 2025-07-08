import dash
from dash import Dash, html, dcc, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import datetime
import os
import random

CSV_PATH = 'data.csv'
COLUMNS = [
    'Date', 'Workout Time', 'Elapsed Time', 'Distance', 'Active KJ',
    'Total KJ', 'Altitude Gain', 'Average Heart Rate', 'Effort', 'Pace', 'Type'
]


def append_sample_activities(n=10):
    new_data = generate_sample_data().head(n)
    if os.path.exists(CSV_PATH):
        new_data.to_csv(CSV_PATH, mode='a', header=False, index=False)
    else:
        new_data.to_csv(CSV_PATH, index=False)
        append_sample_activities(10)

# Sample activity generator
def generate_sample_data():
    types = ['Run', 'Ride', 'Walk']
    sample_dates = pd.date_range(end=datetime.date.today(), periods=10)
    data = []
    for date in sample_dates:
        type_ = random.choice(types)
        distance = round(random.uniform(3, 12), 1)
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Workout Time': f"{random.randint(20, 90)}:00",
            'Elapsed Time': f"{random.randint(25, 100)}:00",
            'Distance': distance,
            'Active KJ': random.randint(200, 800),
            'Total KJ': random.randint(250, 900),
            'Altitude Gain': random.randint(0, 300),
            'Average Heart Rate': random.randint(100, 160),
            'Effort': random.randint(1, 10),
            'Pace': f"{random.randint(4, 6)}:{random.randint(0,59):02d}",
            'Type': type_
        })
    return pd.DataFrame(data)

# Load or seed data
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
else:
    df = generate_sample_data()
    df.to_csv(CSV_PATH, index=False)

# Input group builder
def input_group(label, id_, type_, placeholder='', step=None):
    return html.Div([
        dbc.Label(label),
        dbc.Input(id=id_, type=type_, placeholder=placeholder, step=step)
    ])

# Modal
modal = html.Div([
    dbc.Button("Add New Entry", id="open", n_clicks=0),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Add New Data")),
            dbc.ModalBody([
                input_group("Date (YYYY-MM-DD)", "input-date", "text", "2025-07-06"),
                input_group("Workout Time", "input-workout", "text"),
                input_group("Elapsed Time", "input-elapsed", "text"),
                input_group("Distance (km)", "input-distance", "number", "e.g. 5.0", step=0.1),
                input_group("Active KJ", "input-active", "number", step=1),
                input_group("Total KJ", "input-total", "number", step=1),
                input_group("Altitude Gain", "input-altitude", "number", step=1),
                input_group("Average Heart Rate", "input-hr", "number", step=1),
                input_group("Effort", "input-effort", "number", step=1),
                input_group("Pace", "input-pace", "text"),
                input_group("Type", "input-type", "text"),
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

# App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([
    html.H4(f"Current Time: {datetime.datetime.now()}"),
    modal,
    html.Br(),
    dash_table.DataTable(id='table', data=df.to_dict('records'), page_size=10),
    html.Br(),
    html.H5("Activity Scatter Plot"),
    dcc.Graph(id='scatter', figure=px.scatter(
        df, x='Date', y='Distance', color='Type', size='Effort',
        hover_name='Type', title='Workouts by Date'
    ))
])

# Modal toggle callback
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks"), Input("submit", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(open_clicks, close_clicks, submit_clicks, is_open):
    if open_clicks or close_clicks or submit_clicks:
        return not is_open
    return is_open

# Submit callback
@app.callback(
    [Output("table", "data"),
     Output("scatter", "figure")],
    [Input("submit", "n_clicks")],
    [
        State("input-date", "value"),
        State("input-workout", "value"),
        State("input-elapsed", "value"),
        State("input-distance", "value"),
        State("input-active", "value"),
        State("input-total", "value"),
        State("input-altitude", "value"),
        State("input-hr", "value"),
        State("input-effort", "value"),
        State("input-pace", "value"),
        State("input-type", "value"),
    ],
    prevent_initial_call=True
)
def add_entry(n_clicks, date, workout, elapsed, distance, active, total, altitude, hr, effort, pace, type_):
    if date and distance is not None:
        new_row = pd.DataFrame([{
            "Date": date,
            "Workout Time": workout,
            "Elapsed Time": elapsed,
            "Distance": float(distance),
            "Active KJ": active,
            "Total KJ": total,
            "Altitude Gain": altitude,
            "Average Heart Rate": hr,
            "Effort": effort,
            "Pace": pace,
            "Type": type_
        }])
        new_row.to_csv(CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH), index=False)
        updated_df = pd.read_csv(CSV_PATH)
        return (
            updated_df.to_dict('records'),
            px.scatter(updated_df, x='Date', y='Distance', color='Type', size='Effort',
                       hover_name='Type', title='Workouts by Date')
        )
    raise dash.exceptions.PreventUpdate

# Run
if __name__ == '__main__':
    append_sample_activities(10)
    app.run(debug=True)

import dash
import pandas as pd
from dash import dcc, html, callback, dash_table, no_update, State
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import dash_mantine_components as dmc
from flask_login import current_user


dash.register_page(__name__, path='/all-stats')


def load_dataframe():
    data = pd.read_csv("./data/new_data.csv")
    # data = data.drop(columns=['mark.1', 'id'])
    data = data.drop_duplicates(['regnum', 'module'], keep='last')
    data['gender'] = data['gender'].replace(
        {'female': 'Female', 'male': 'Male', "MALE": "Male", "FEMALE": "Female", "M": "Male", "F": "Female"})
    return data


data = load_dataframe()
style = {
    "border": f"1px solid {dmc.theme.DEFAULT_COLORS['indigo'][4]}",
    "textAlign": "center",
}


def faculty_chart():
    data_grouped = data.groupby(by="faculty")[
        'regnum'].nunique().sort_values(ascending=True).reset_index(
        name="Students")
    return {
        'data': [
            go.Bar(
                x=data_grouped.faculty,
                y=data_grouped['Students'],
                name="Faculty Distribution",
                marker=dict(
                    color="orange",
                ),
                hoverinfo="text",
                hovertext="<b> Faculty: " + data_grouped.faculty +
                "</b>" + "<br>" + "<b> Students: </b>" +
                data_grouped["Students"].astype(str)
            )
        ],
        "layout": go.Layout(
            hovermode='closest',
            title={
                "text": "Faculty Distribution ",
                "y": 0.93,
                "x": 0.5,
                "xanchor": 'center',
                "yanchor": 'top',

            },
            titlefont={
                "color": "black",
                "size": 16
            },
            legend={
                "orientation": 'h',
                "xanchor": 'left',
                "x": 0.7,
                "y": -0.97
            },
            font=dict(
                family="sans-serif",
                size=12,
                color='black'
            ),
            xaxis=dict(
                tickangle=45
            ),
            height=350,
            width=350
        )
    }


def hieghst_enrolling_programmes():
    data_grouped = data.groupby(by="programmecode")[
        'regnum'].nunique().sort_values(ascending=True).reset_index(
        name="Students")
    return {
        'data': [
            go.Bar(
                x=data_grouped.programmecode.tail(30),
                y=data_grouped['Students'].tail(30),
                name="Programme Distribution",
                marker=dict(
                    color="orange",
                ),
                hoverinfo="text",
                hovertext="<b> Programme Code: " + data_grouped.programmecode.tail(30) +
                "</b>" + "<br>" + "<b> Students: </b>" +
                data_grouped["Students"].tail(30).astype(str)
            )
        ],
        "layout": go.Layout(
            hovermode='closest',
            title={
                "text": "Programme Distribution ",
                "y": 0.93,
                "x": 0.5,
                "xanchor": 'center',
                "yanchor": 'top',

            },
            titlefont={
                "color": "black",
                "size": 16
            },
            legend={
                "orientation": 'h',
                "xanchor": 'left',
                "x": 0.7,
                "y": -0.97
            },
            font=dict(
                family="sans-serif",
                size=12,
                color='black'
            ),
            xaxis=dict(
                tickangle=45
            ),
        )
    }


def gender_chart():
    data_grouped = data.groupby(by="gender")[
        'regnum'].nunique().reset_index(
        name="Students")
    return {
        'data': [
            go.Pie(
                labels=data_grouped.gender,
                values=data_grouped["Students"],
                hoverinfo="label+value+percent",
                textinfo="label+value",
                textfont=dict(size=12),
                hole=.7,
                rotation=45
            )
        ],
        "layout": go.Layout(
            hovermode='closest',
            title={
                "text": "Gender Distribution ",
                "y": 0.93,
                "x": 0.5,
                "xanchor": 'center',
                "yanchor": 'top',

            },
            titlefont={
                "color": "black",
                "size": 16
            },
            legend={
                "orientation": 'h',
                "xanchor": 'left',
                "x": 0.5,
                "y": -100
            },
            font=dict(
                family="sans-serif",
                size=12,
                color='black'
            ),
            width=350,
            height=350
        )
    }


def layout(**kwargs):
    if not current_user.is_authenticated:
        return dmc.Paper(
            children=[
                html.Div(["Please ", dcc.Link(
                    "login", href="/login"), " to continue"])
            ],
            shadow="xs",
            style={"width": "400px", "margin": "20px auto", "padding": "20px"}
        )
    layout = html.Div([
        dmc.Grid(
            children=[
                dmc.Col(dmc.Paper(
                    children=[
                        dmc.Text(f"Total Programmes", weight=500),
                        dmc.Text(
                            f"{data.programme.nunique()} programmes", size="xs")
                    ],
                    shadow="xs",
                    style={
                        "padding": "10px"
                    }
                ), span="auto"),
                dmc.Col(dmc.Paper(
                    children=[
                        dmc.Text(f"Total Modules", weight=500),
                        dmc.Text(f"{data.module.nunique()} modules", size="xs")
                    ],
                    shadow="xs",
                    style={
                        "padding": "10px"
                    }
                ), span="auto"),
                dmc.Col(dmc.Paper(
                    children=[
                        dmc.Text(f"Total Students", weight=500),
                        dmc.Text(
                            f"{data.regnum.nunique()} Students", size="xs")
                    ],
                    shadow="xs",
                    style={
                        "padding": "10px"
                    }
                ), span="auto"),
            ],
            gutter="xl",
            style={"marginBottom": "20px"}
        ),
        dmc.Grid(
            children=[
                dmc.Col([
                    dmc.Paper(
                        children=[dcc.Graph(id="gender-distribution-stats",
                                            figure=gender_chart())],
                        shadow="xs",
                    )

                ], span="auto"),
                dmc.Col([
                    dmc.Paper(
                        children=[
                            dmc.Button("🡠", id='back_button', variant="subtle",
                                       style={'display': 'none'}),
                            dcc.Graph(id="academicyear-stats")
                        ],
                        shadow="xs",
                    )

                ], span="auto"),
                dmc.Col([
                    dmc.Paper(
                        children=[
                            dcc.Graph(id="faculty-chart",
                                      figure=faculty_chart())
                        ],
                        shadow="xs",
                    )

                ], span="auto"),
            ],
            gutter="xl",
        ),

        dmc.Grid(
            children=[
                dmc.Col([
                    dmc.Paper(
                        children=[
                            dmc.Select(
                                label="Select Count",
                                id="count-selection",
                                value="30",
                                data=["10", "20", "30", "40", "50",
                                      "60", "70", "80", "90", "100"],
                                style={"width": 200, "marginBottom": 10},
                            ),
                            dcc.Graph(id="hieghst-enrolling-programmes",
                                      figure=hieghst_enrolling_programmes())
                        ],
                        shadow="xs",
                        style={"padding": "10px"}
                    ),

                ], span="auto")
            ],
            gutter="xl",
            style={"marginTop": "20px", "marginBottom": "80px"}
        )
    ], style={"width": "90%", "margin": "20px auto"})
    return layout

# callbacks
# update programme


@callback(
    Output("hieghst-enrolling-programmes", "figure"),
    Input('count-selection', 'value'))
def update_programmes(count):
    data_grouped = data.groupby(by="programmecode")[
        'regnum'].nunique().sort_values(ascending=True).reset_index(
        name="Students")
    return {
        'data': [
            go.Bar(
                x=data_grouped.programmecode.tail(int(count)),
                y=data_grouped['Students'].tail(int(count)),
                name="Programme Distribution",
                marker=dict(
                    color="orange",
                ),
                hoverinfo="text",
                hovertext="<b> Programme Code: " + data_grouped.programmecode.tail(int(count)) +
                "</b>" + "<br>" + "<b> Students: </b>" +
                data_grouped["Students"].tail(int(count)).astype(str)
            )
        ],
        "layout": go.Layout(
            hovermode='closest',
            title={
                "text": "Programme Distribution: Top " + count,
                "y": 0.93,
                "x": 0.5,
                "xanchor": 'center',
                "yanchor": 'top',

            },
            titlefont={
                "color": "black",
                "size": 16
            },
            legend={
                "orientation": 'h',
                "xanchor": 'left',
                "x": 0.7,
                "y": -0.97
            },
            font=dict(
                family="sans-serif",
                size=12,
                color='black'
            ),
            xaxis=dict(
                tickangle=45
            ),
        )
    }


@callback(
    Output("academicyear-stats", "figure"),
    Output('back_button', 'style'),
    [Input('academicyear-stats', 'clickData'),
     Input('back_button', 'n_clicks')])
def academicyear_drilldown(click_data, n_clicks):

    # using callback context to check which input was fired
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == 'academicyear-stats':

        # get vendor name from clickData
        if click_data is not None:
            academicyear = click_data['points'][0]['label'].split(' ')[1]
            # print(academicyear.split('.'))
            if int(academicyear) in data['academicyear'].unique().tolist():

                data_grouped = data[data['academicyear'] == int(academicyear)].groupby(
                    by='semester')['regnum'].nunique().reset_index(name="Students")

                # returning the fig and unhiding the back button
                return {
                    'data': [
                        go.Pie(
                            labels=[
                                f'Part {academicyear}.{semester}' for semester in data_grouped.semester],
                            values=data_grouped["Students"],
                            hoverinfo="label+value+percent",
                            textinfo="label+value",
                            textfont=dict(size=12),
                            hole=.7,
                            rotation=45
                        )
                    ],
                    "layout": go.Layout(
                        width=350,
                        height=350,
                        hovermode='closest',
                        title={
                            "text": "Semester Students Distribution",
                            "y": 0.93,
                            "x": 0.5,
                            "xanchor": 'center',
                            "yanchor": 'top',

                        },
                        titlefont={
                            "color": "black",
                            "size": 16
                        },
                        legend={
                            "orientation": 'h',
                            "xanchor": 'left',
                            "x": 0.5,
                            "y": -0.9
                        },
                        font=dict(
                            family="sans-serif",
                            size=12,
                            color='black'
                        )
                    )
                }, {"display": "block"}

            else:
                data_grouped = data.groupby(by="academicyear")[
                    'regnum'].nunique()
                data_grouped = data_grouped.reset_index(
                    name="Students")
                return {
                    'data': [
                        go.Pie(
                            labels=[
                                f'Part {academicyear}' for academicyear in data_grouped.academicyear],
                            values=data_grouped["Students"],
                            hoverinfo="label+value+percent",
                            textinfo="label+value",
                            textfont=dict(size=12),
                            hole=.7,
                            rotation=45
                        )
                    ],
                    "layout": go.Layout(
                        width=300,
                        height=300,
                        hovermode='closest',
                        title={
                            "text": "Academic Year Students Distribution",
                            "y": 0.93,
                            "x": 0.5,
                            "xanchor": 'center',
                            "yanchor": 'top',

                        },
                        titlefont={
                            "color": "black",
                            "size": 16
                        },
                        legend={
                            "orientation": 'h',
                            "xanchor": 'center',
                            "x": 0.5,
                            "y": -0.9
                        },
                        font=dict(
                            family="sans-serif",
                            size=12,
                            color='black'
                        )
                    )
                }, {"display": "none"}

    else:
        data_grouped = data.groupby(by="academicyear")['regnum'].nunique().reset_index(
            name="Students")
        return {
            'data': [
                go.Pie(
                    labels=[
                        f'Part {academicyear}' for academicyear in data_grouped.academicyear],
                    values=data_grouped["Students"],
                    hoverinfo="label+value+percent",
                    textinfo="label+value",
                    textfont=dict(size=12),
                    hole=.7,
                    rotation=45
                )
            ],
            "layout": go.Layout(
                width=350,
                height=350,
                hovermode='closest',
                title={
                    "text": "Academic Year Students Distribution",
                            "y": 0.93,
                            "x": 0.5,
                            "xanchor": 'center',
                            "yanchor": 'top',

                },
                titlefont={
                    "color": "black",
                    "size": 16
                },
                legend={
                    "orientation": 'h',
                    "xanchor": 'center',
                    "x": 0.5,
                    "y": -0.9
                },
                font=dict(
                    family="sans-serif",
                    size=12,
                    color='black'
                )
            )
        }, {"display": "none"}

import dash
import pandas as pd
from dash import dcc, html, callback, dash_table, no_update, State
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import dash_mantine_components as dmc
import dash_ag_grid as dag
from flask_login import current_user


dash.register_page(__name__, path='/graduants')


def load_dataframe():
    data = pd.read_csv("./data/new_data.csv")
    data = data.drop(columns=['mark.1', 'id'])
    data = data.drop_duplicates(['regnum', 'module'], keep='last')
    data['gender'] = data['gender'].replace(
        {'female': 'Female', 'male': 'Male', "MALE": "Male", "FEMALE": "Female", "M": "Male", "F": "Female"})
    data = data[data['decision'] == "PASS"]
    return data


data = load_dataframe()


def go_chart():
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
            height=350,
            width=350
        )
    }


def programmetype_chart():
    data_grouped = data.groupby(by="programmetype")[
        'regnum'].nunique()
    data_grouped = data_grouped.reset_index(
        name="Students")
    return {
        'data': [
            go.Pie(
                labels=data_grouped.programmetype,
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
                "text": "Programmetype Distribution ",
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


def gender_chart():
    data_grouped = data.groupby(by="gender")[
        'regnum'].nunique()
    data_grouped = data_grouped.reset_index(
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

                dmc.Col([
                    dmc.Paper(
                        children=[
                            dmc.Button("🡠", id='back-btn', variant="subtle",
                                       style={'display': 'none'}),
                            dcc.Graph(id="programmetype_distribution",
                                      config={"displayModeBar": "hover"}),
                        ],
                        shadow="xs",
                    )

                ], span="auto"),
                dmc.Col([
                    dmc.Paper(
                        children=[dcc.Graph(id="gender_distribution",
                                            config={"displayModeBar": "hover"},
                                            figure=gender_chart())],
                        shadow="xs",
                    )

                ], span="auto"),
                dmc.Col([
                    dmc.Paper(
                        children=[
                            dmc.Button("🡠", id='back-bttn', variant="subtle",
                                       style={'display': 'none'}),
                            dcc.Graph(id="faculty_distribution",
                                      config={"displayModeBar": "hover"}),
                        ],
                        shadow="xs",
                    )

                ], span="auto"),

            ], style={"marginTop": "10px", "marginBottom": "20px"}
        ),
        dmc.Grid(
            children=[
                dmc.Col([
                    dmc.Paper(
                        id="programmetype-table",
                        children=[],
                        shadow="xs",
                        style={"padding": "10px"}
                    ),
                ], span="auto"),
            ],
            gutter="xl",
        ),
        html.Div(id="programmetype_selected_rows", children=[
            dmc.Modal(
                title="Student Information",
                size="80%",
                id="programmetype-modal",
                zIndex=10000,
                children=[dmc.Text("This is a vertically centered modal.")],
            ),
        ], style={'marginBottom': "80px"}),
    ], style={"width": "90%", "margin": "20px auto"})
    return layout
# callbacks
# programmetype table


@callback(
    Output('programmetype-table', "children"),
    Input('programmetype_distribution', "clickData"),
)
def programmetype_table(click_data):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    programmetypes = data['programmetype'].unique().tolist()
    if trigger_id == 'programmetype_distribution':

        # get vendor name from clickData
        if click_data is not None:
            programmetype = click_data['points'][0]['label']
            # print(academicyear.split('.'))
            if programmetype in programmetypes:

                new_df = data[data['programmetype'] == programmetype]
                # print("You clicked", new_df)
                ag_table = html.Div([dmc.Text(f"{programmetype}", weight=500),
                                    dag.AgGrid(
                    id="programmetype_table",
                    rowData=new_df.to_dict('records'),
                    columnDefs=[
                        {'field': 'regnum'},
                        {'field': 'firstnames'},
                        {'field': 'surname'},
                        {'field': 'programmecode'}
                    ],
                    columnSize="sizeToFit",
                    defaultColDef={"filter": True},
                    dashGridOptions={
                        "rowSelection": "single", "animateRows": False},
                )])
                return ag_table

        else:
            new_df = data[data["programmetype"] == programmetypes[0]]
            ag_table = html.Div([dmc.Text(f"{programmetypes[0]}", weight=500),
                                dag.AgGrid(
                id="programmetype_table",
                rowData=new_df.to_dict('records'),
                columnDefs=[
                    {'field': 'regnum'},
                    {'field': 'firstnames'},
                    {'field': 'surname'},
                    {'field': 'programmecode'}
                ],
                columnSize="sizeToFit",
                defaultColDef={"filter": True},
                dashGridOptions={
                    "rowSelection": "single", "animateRows": False},
            )]),
            return ag_table
    else:
        new_df = data[data["programmetype"] == programmetypes[0]]
        ag_table = html.Div([dmc.Text(f"{programmetypes[0]}", weight=500),
                            dag.AgGrid(
            id="programmetype_table",
            rowData=new_df.to_dict('records'),
            columnDefs=[
                {'field': 'regnum'},
                {'field': 'firstnames'},
                {'field': 'surname'},
                {'field': 'programmecode'}
            ],
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "single", "animateRows": False},
        )])
        return ag_table

# output selected rows


@ callback(
    Output("programmetype-modal", "opened"),
    Output("programmetype-modal", "children"),
    Input("programmetype_table", "n_clicks"),
    Input("programmetype_table", "selectedRows"),
    State("programmetype-modal", "opened"),
    prevent_initial_call=True,
)
def programmetype_selected_rows(n_clicks, selected_rows, opened):
    ctx = dash.callback_context
    # print(ctx.triggered[0]['prop_id'])
    children = []
    if ctx.triggered[0]['prop_id'] == "programmetype_table.selectedRows":
        if selected_rows:
            regnum = selected_rows[0]["regnum"]
            student_info = data[data['regnum'] == regnum]
            info = html.Div([
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Registration Number"), span=6),
                        dmc.Col(
                            dmc.Text(f"{student_info['regnum'].iloc[0]}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("First names"), span=6),
                        dmc.Col(
                            dmc.Text(f"{student_info['firstnames'].iloc[0]}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Surname"), span=6),
                        dmc.Col(
                            dmc.Text(f"{student_info['surname'].iloc[0]}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Decision"), span=6),
                        dmc.Col(
                            dmc.Highlight(
                                f"{student_info['decision'].iloc[0]}", highlight=f"{student_info['decision'].iloc[0]}",
                                highlightColor="red" if student_info['decision'].iloc[0] == "RETAKE" else "lime"
                            ), span=6
                        )
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Programme"), span=6),
                        dmc.Col(
                            dmc.Text(f"{student_info['programme'].iloc[0]}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Text("Modules", weight=500),
                dag.AgGrid(
                    id="row-selection-popup-popup",
                    rowData=student_info.to_dict("records"),
                    columnDefs=[
                        {'field': 'module'},
                        {'field': 'mark'},
                        {'field': 'grade'}],
                    columnSize="sizeToFit",
                    defaultColDef={"filter": True},
                    dashGridOptions={
                        "rowSelection": "single", "animateRows": False},
                ),

            ])
            children.append(info)
            return not opened, children
        else:
            return dash.no_update, dash.no_update
    else:
        return dash.no_update, dash.no_update

# faculty distribution drill through


@callback(
    Output('faculty_distribution', "figure"),
    Output('back-bttn', "style"),
    [Input('faculty_distribution', "clickData"),
     Input('back-bttn', 'n_clicks')]
)
def faculty_distribution(click_data, n_clicks):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == 'faculty_distribution':

        # get vendor name from clickData
        if click_data is not None:
            faculty = click_data['points'][0]['label']
            print(faculty)
            if faculty in data['faculty'].unique().tolist():
                grouped_data = data[data["faculty"] == faculty].groupby(by="programme")[
                    'regnum'].nunique().sort_values(ascending=True).reset_index(name="Students")
                return {
                    'data': [
                        go.Bar(
                            x=grouped_data.programme,
                            y=grouped_data['Students'],
                            name="Programme Distribution",
                            marker=dict(
                                color="green",
                            ),
                            hoverinfo="text",
                            hovertext="<b> Programme: " + grouped_data.programme +
                            "</b>" + "<br>" + "<b> Students: </b>" +
                            grouped_data["Students"].astype(str)
                        )
                    ],
                    "layout": go.Layout(
                        hovermode='closest',
                        title={
                            "text": "Programme Distribution: " + "<b>" + faculty+"</b>",
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
                        height=350,
                        width=350
                    )
                }, {"display": "block"}
            else:
                return go_chart(), {"display": "none"}
    else:
        return go_chart(), {"display": "none"}

# grades distribution drill through


@callback(
    Output('programmetype_distribution', "figure"),
    Output('back-btn', "style"),
    Input('programmetype_distribution', "clickData"),
    Input('back-btn', 'n_clicks'),
)
def grade_distribution(click_data, n_clicks):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == 'programmetype_distribution':

        # get vendor name from clickData
        if click_data is not None:
            programmetype = click_data['points'][0]['label']
            # print(academicyear.split('.'))
            if programmetype in data['programmetype'].unique().tolist():

                grouped_data = data[data["programmetype"] == programmetype].groupby(by="grade")[
                    'regnum'].nunique()
                grouped_data = grouped_data.reset_index(
                    name="Students")
                fig = px.bar(
                    grouped_data,
                    x="grade",
                    y="Students",
                    # orientation='h',
                    title=f"Student Distribution: {programmetype}",
                    color="grade",
                    template="plotly_white"

                )
                fig.update_layout(showlegend=False,
                                  width=350,
                                  height=350,
                                  template='simple_white')
                fig.update_xaxes(tickangle=45)
                return fig, {"display": "block"}

            else:

                return programmetype_chart(), {"display": "none"}

    else:
        return programmetype_chart(), {"display": "none"}

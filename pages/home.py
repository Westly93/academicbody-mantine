import dash
import pandas as pd
import dash_ag_grid as dag
import plotly.graph_objs as go
from dash import dcc, html, callback, dash_table, no_update, State, ctx
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from flask_login import current_user


def load_dataframe():
    data = pd.read_csv("./data/new_data.csv")
    # data = data.drop(columns=['mark.1', 'id'])
    data = data.drop_duplicates(['regnum', 'module'], keep='last')
    data['gender'] = data['gender'].replace(
        {'female': 'Female', 'male': 'Male', "MALE": "Male", "FEMALE": "Female", "M": "Male", "F": "Female"})
    return data


""" def create_table(df):
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
    table = [html.Thead(header), html.Tbody(rows)]
    return table """


def create_ag_grid_table(df, columnDefs):
    grid = dag.AgGrid(
        id="ag_tbl",
        rowData=df.to_dict("records"),
        columnDefs=columnDefs,
        columnSize="sizeToFit",
        defaultColDef={"filter": True},
        dashGridOptions={"rowSelection": "single", "animateRows": False},
    ),
    return grid


data = load_dataframe()
faculties = data.faculty.unique().tolist()
faculty_selection = dmc.Select(
    label="Select Faculty",
    id="faculty_selection",
    searchable=True,
    data=faculties,
    value=faculties[0],

)

dash.register_page(__name__,
                   path='/',  # '/' is home page and it represents the url
                   name='Home',  # name of page, commonly used as name of link
                   title='Academicbody',  # title that appears on browser's tab
                   image='logo.png',  # image in the assets folder
                   description='Histograms are the new bar charts.'
                   )


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

    layout = html.Div(children=[
        faculty_selection,
        dmc.Grid(
            children=[
                dmc.Col(
                    id="total_programmes",
                    span="auto"),
                dmc.Col(
                    id="total_modules",
                    span="auto"),
                dmc.Col(
                    id="total_students",
                    span="auto"),
            ],
            gutter="xl",
            style={"marginBottom": "20px", "marginTop": "20px"}
        ),
        dmc.Grid(
            children=[
                dmc.Col(
                    dmc.Paper(
                        children=[dcc.Graph(id="decision_distribution")],
                        shadow="xs",
                    ), span="auto"),
                dmc.Col([
                    dmc.Paper(
                        children=[
                            dmc.Button("🡠", id='back-button', variant="subtle",
                                       style={'display': 'none'}),
                            dcc.Graph(
                                id="academicyear_chart"
                            )
                        ],
                        shadow="xs",
                    )
                ], span="auto"),
                dmc.Col(
                    dmc.Paper(
                        children=[
                            dcc.Graph(
                                id="gender_chart", config={"displayModeBar": "hover"}
                            )
                        ],
                        shadow="xs",
                    ), span="auto"),
            ],
            justify="center",
            align="center",
            gutter="md", style={"marginTop": "10px", "marginBottom": "10px"}
        ),
        dmc.Grid(
            children=[

                dmc.Col(
                    dmc.Paper(
                        id="tbl",
                        children=[],
                        shadow="xs",
                        style={"padding": "10px"}
                    ), span="auto"),

            ], style={"marginTop": "10px", "marginBottom": "20px"}
        ),
        html.Div(id="selected_rows", children=[
            dmc.Modal(
                title="Student Information",
                size="80%",
                id="modal",
                zIndex=10000,
                children=[dmc.Text("This is a vertically centered modal.")],
            ),
        ], style={'marginBottom': "20px"}),
        dmc.Select(
            label="Select Programme",
            searchable=True,
            id="programme_selection",

        ),
        dmc.Paper(
            children=[dcc.Graph(id="module_performance")],
            shadow="xs",
            style={"marginTop": "20px", "padding": "10px"}
        ),
        dmc.Grid(
            children=[
                dmc.Col([
                    dmc.Select(
                        label="Select Attendance Type",
                        searchable=True,
                        id="attendancetype_selection",

                    ),

                ], span="auto"),
                dmc.Col([
                    dmc.Select(
                        label="Select Academic Year",
                        searchable=True,
                        id="academicyear_selection",
                    ),

                ], span="auto"),
                dmc.Col([
                    dmc.Select(
                        label="Select Semester",
                        searchable=True,
                        id="semester_selection",

                    )

                ], span="auto"),

            ], style={"marginTop": "10px", "marginBottom": "20px"}
        ),
        dmc.Grid(
            children=[

                dmc.Col([
                    dmc.Paper(
                        children=[dcc.Graph(id="programme_decisions")],
                        shadow="xs",
                        style={"padding": "10px"}
                    )
                ], span="auto"),
                dmc.Col(

                    dmc.Paper(
                        id="programme-decision-table",
                        children=[],
                        shadow="xs",
                        style={"padding": "10px"}
                    ), span="auto"),

            ], style={"marginTop": "10px", "marginBottom": "20px"}
        ),
        html.Div(id="programme_selected_rows", children=[
            dmc.Modal(
                title="Student Information",
                size="80%",
                id="modal2",
                zIndex=10000,
                children=[dmc.Text("This is a vertically centered modal.")],
            ),
        ], style={'marginBottom': "20px"}),

    ], style={"width": "90%", "margin": "40px auto"}),
    return layout


# Callbacks
# Total programmes
@callback(
    Output("total_programmes", "children"),
    Input("faculty_selection", "value")
)
def update_total_programmes(faculty):
    df = data[data['faculty'] == faculty]
    return dmc.Paper(
        children=[
            dmc.Text(f"Total Programmes", weight=500),
            dmc.Text(
                f"{df.programme.nunique()} programmes", size="xs")
        ],
        shadow="xs",
        style={
            "padding": "10px"
        }
    )

# update total modules


@callback(
    Output("total_modules", "children"),
    Input("faculty_selection", "value")
)
def update_total_programmes(faculty):
    df = data[data['faculty'] == faculty]
    return dmc.Paper(

        children=[
            dmc.Text(f"Total Modules", weight=500),
            dmc.Text(f"{df.module.nunique()} modules", size="xs")
        ],
        shadow="xs",
        style={
            "padding": "10px"
        }
    )

# update total students


@callback(
    Output("total_students", "children"),
    Input("faculty_selection", "value")
)
def update_total_programmes(faculty):
    df = data[data['faculty'] == faculty]
    return dmc.Paper(

        children=[
            dmc.Text(f"Total Students", weight=500),
            dmc.Text(f"{df.regnum.nunique()} Students", size="xs")
        ],
        shadow="xs",
        style={
            "padding": "10px"
        }
    )
# module performances


@callback(
    Output("module_performance", "figure"),
    [Input("faculty_selection", "value"),
     Input("programme_selection", "value")]
)
def module_pass_rate(faculty, programme):
    df = data[(data['faculty'] == faculty) & (data['programme'] == programme)]
    module_pass_rate = df.groupby(
        'module')['mark'].apply(lambda x: (x >= 50).mean() * 100).reset_index(
        name="Pass Rate")
    grouped_data = df.groupby(by="module")[
        'regnum'].nunique().reset_index(name="Students")
    return {
        "data": [
            go.Bar(
                x=module_pass_rate['module'],
                y=module_pass_rate['Pass Rate'],
                name="Module Pass Rates",
                marker=dict(
                    color="orange",
                ),
                hoverinfo="text",
                hovertext="<b> Module </b>" +
                module_pass_rate['module'] + "<br>" + "<b> Pass Rate </b>" +
                module_pass_rate["Pass Rate"].astype(str)
            ),
            go.Scatter(
                x=grouped_data['module'],
                y=grouped_data["Students"],
                mode="lines",
                name="Module population",
                line=dict(
                    width=3,
                    color="#FF00FF"
                ),
                hoverinfo="text",
                hovertext="<b> Module </b>" +
                grouped_data['module'] + "<br>" + "<b> Students </b>" +
                grouped_data["Students"].astype(str)
            )
        ],
        "layout": go.Layout(
            barmode="stack",
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            title={
                "text": "Students Performance Across Modules",
                "y": 0.93,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",

            },
            titlefont={
                "color": "black",
                "size": 20
            },
            hovermode="x",
            xaxis=dict(
                title="<b>Module</b>",
                color="black",
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor="black",
                linewidth=2,
                ticks="outside",
                tickfont=dict(
                    family="Arial",
                    size=12,
                    color="black"
                )
            ),
            yaxis=dict(
                title="<b> Pass Rate </b>",
                color="black",
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor="black",
                linewidth=2,
                ticks="outside",
                tickfont=dict(
                    family="Arial",
                    size=12,
                    color="black"
                )
            ),
            legend={
                "orientation": "h",
                "bgcolor": "#ffffff",
                "xanchor": "center",
                "x": 0.5,
                "y": -0.6,

            },
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            )

        )
    }

# programme decision distribution


@callback(
    Output('programme_decisions', "figure"),
    [Input("faculty_selection", "value"),
     Input("programme_selection", "value"),
     Input("attendancetype_selection", "value"),
     Input("academicyear_selection", "value"),
     Input("semester_selection", "value")]
)
def programme_decision_distribution(faculty, programme, attendancetype, academicyear, semester):
    data_grouped = data[(data['faculty'] == faculty) & (data['attendancetype'] == attendancetype) & (data['programme'] == programme) & (data['academicyear'] == int(academicyear)) & (data['semester'] == int(semester))].groupby(by="decision")[
        'regnum'].nunique().reset_index(
        name="Students")
    # print(data_grouped)
    return {
        'data': [
            go.Pie(
                labels=data_grouped.decision,
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
                "text": "Decision Distribution",
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
                "xanchor": 'right',
                "x": 0.5,
                "y": -0.9
            },
            font=dict(
                family="sans-serif",
                size=12,
                color='black'
            )
        )
    }
# semester selection


@callback(
    Output("semester_selection", 'data'),
    Output("semester_selection", "value"),
    [Input("faculty_selection", "value"),
     Input("programme_selection", "value"),
     Input("attendancetype_selection", "value")]
)
def update_semester(faculty, programme, attendancetype):
    options = data[(data['faculty'] == faculty) & (data['programme'] == programme) & (data['attendancetype'] == attendancetype)
                   ].semester.unique().tolist()
    options = [str(x) for x in options]
    value = options[0]
    return options, value
# academicyear selection


@callback(
    Output('academicyear_selection', "data"),
    Output("academicyear_selection", "value"),
    [Input("faculty_selection", "value"),
     Input("programme_selection", "value"),
     Input("attendancetype_selection", "value")]
)
def update_academicyear(faculty, programme, attendancetype):
    options = data[(data['faculty'] == faculty) & (data['programme'] == programme) & (data['attendancetype'] == attendancetype)
                   ].academicyear.unique().tolist()
    options = [str(x) for x in options]
    value = options[0]
    return options, value
# attendancetype selection


@callback(
    Output("attendancetype_selection", 'data'),
    Output("attendancetype_selection", "value"),
    Input("faculty_selection", "value"),
    Input("programme_selection", "value")
)
def update_attendancetype(faculty, programme):
    options = data[(data['faculty'] == faculty) & (data['programme'] == programme)
                   ].attendancetype.unique().tolist()
    value = options[0]
    return options, value
# programme selection


@callback(
    Output("programme_selection", 'data'),
    Output("programme_selection", "value"),
    Input("faculty_selection", "value")
)
def update_programme(faculty):
    options = data[(data['faculty'] == faculty)
                   ].programme.unique().tolist()
    value = options[0]
    return options, value
# Gender Distribution


@callback(
    Output('gender_chart', "figure"),
    Input("faculty_selection", "value")
)
def gender_chart(faculty):
    data_grouped = data[(data['faculty'] == faculty)].groupby(by="gender")[
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
            width=300,
            height=300,
            hovermode='closest',
            title={
                "text": "Gender Distribution",
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
                "xanchor": 'right',
                "x": 0.5,
                "y": -0.9
            },
            font=dict(
                family="sans-serif",
                size=12,
                color='black'
            )
        )
    }
# decision distribution


@callback(
    Output('decision_distribution', "figure"),
    Input("faculty_selection", "value")
)
def go_chart(faculty):
    data_grouped = data[(data['faculty'] == faculty)].groupby(by="decision")[
        'regnum'].nunique()
    data_grouped = data_grouped.reset_index(
        name="Students")
    return {
        'data': [
            go.Pie(
                labels=data_grouped.decision,
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
                "text": "Decision Distribution ",
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
    }
# academicyear drill through


@callback(
    Output("academicyear_chart", "figure"),
    Output('back-button', 'style'),
    [Input('academicyear_chart', 'clickData'),
     Input('back-button', 'n_clicks'),
     Input('faculty_selection', 'value')])
def academicyear_drilldown(click_data, n_clicks, faculty):

    # using callback context to check which input was fired
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    df = data[data['faculty'] == faculty]

    if trigger_id == 'academicyear_chart':

        # get vendor name from clickData
        if click_data is not None:
            academicyear = click_data['points'][0]['label'].split(' ')[1]
            # print(academicyear.split('.'))
            if int(academicyear) in df['academicyear'].unique().tolist():

                data_grouped = df[df['academicyear'] == int(academicyear)].groupby(
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
                        width=300,
                        height=300,
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
                data_grouped = df.groupby(by="academicyear")[
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
        data_grouped = df.groupby(by="academicyear")['regnum'].nunique()
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
# programme decision table


@callback(
    Output('programme-decision-table', "children"),
    [Input("programme_decisions", "clickData"),
     Input("faculty_selection", "value"),
     Input("programme_selection", "value"),
     Input("attendancetype_selection", "value"),
     Input("academicyear_selection", "value"),
     Input("semester_selection", "value")]
)
def programme_decision_table(click_data, faculty, programme, attendancetype, academicyear, semester):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    df = data[(data['faculty'] == faculty) & (data['programme'] == programme) & (data['attendancetype']
                                                                                 == attendancetype) & (data['academicyear'] == int(academicyear)) & (data['semester'] == int(semester))].drop_duplicates(['regnum'], keep='last')
    decisions = df['decision'].unique().tolist()
    if trigger_id == 'programme_decisions':

        # get vendor name from clickData
        if click_data is not None:
            decision = click_data['points'][0]['label']
            # print(academicyear.split('.'))
            if decision in decisions:

                new_df = df[df['decision'] == decision]
                # print("You clicked", new_df)
                ag_table = html.Div([dmc.Text(f"{decision}", weight=500),
                                    dag.AgGrid(
                    id="programme_decision_table",
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
            new_df = df[df["decision"] == decisions[0]]
            ag_table = html.Div([dmc.Text(f"{decisions[0]}", weight=500),
                                dag.AgGrid(
                id="programme_decision_table",
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
        if len(decisions) > 0:
            new_df = df[df["decision"] == decisions[0]]
            ag_table = html.Div([dmc.Text(f"{decisions[0]}", weight=500),
                                dag.AgGrid(
                id="programme_decision_table",
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
            return dmc.Alert(
                "Based on the selection you have made there is no data to display",
                title="No data to display",
            )

# decisions


@callback(
    Output('tbl', "children"),
    [Input("decision_distribution", "clickData"),
     Input("faculty_selection", "value")]
)
def decision_table(click_data, faculty):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    df = data[data['faculty'] == faculty].drop_duplicates(
        ['regnum'], keep='last')
    decisions = df['decision'].unique().tolist()
    if trigger_id == 'decision_distribution':

        # get vendor name from clickData
        if click_data is not None:
            decision = click_data['points'][0]['label']
            # print(academicyear.split('.'))
            if decision in decisions:
                new_df = df[df['decision'] == decision]
                ag_table = html.Div([
                    dmc.Text(f"{decision}", weight=500),
                    dag.AgGrid(
                        id="ag_tbl",
                        rowData=new_df.to_dict("records"),
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
                    )
                ])
                return ag_table

        else:
            new_df = df[df["decision"] == decisions[0]]
            ag_table = html.Div([
                dmc.Text(f"{decisions[0]}", weight=500),
                dag.AgGrid(
                    id="ag_tbl",
                    rowData=new_df.to_dict("records"),
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
                )

            ])
            return ag_table
    else:
        if len(decisions) > 0:
            new_df = df[df["decision"] == decisions[0]]
            ag_table = html.Div([
                dmc.Text(f"{decisions[0]}", weight=500),
                dag.AgGrid(
                    id="ag_tbl",
                    rowData=new_df.to_dict("records"),
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
                )

            ])
            return ag_table
        return dmc.Alert(
            "Something happened! You made a mistake and there is no going back, your data was lost forever!",
            title="No data to display",
        )

# Output programme decision selected rows


@ callback(
    Output("modal2", "opened"),
    Output("modal2", "children"),
    Input("programme_decision_table", "n_clicks"),
    Input("programme_decision_table", "selectedRows"),
    State("modal2", "opened"),
    prevent_initial_call=True,
)
def output_programme_selected_rows(n_clicks, selected_rows, opened):
    ctx = dash.callback_context
    # print(ctx.triggered[0]['prop_id'])
    children = []
    if ctx.triggered[0]['prop_id'] == "programme_decision_table.selectedRows":
        if selected_rows:
            print(" The row is selected")
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
        row = dmc.Text("Extra small text", size="xs")
        children.append(row)
        return dash.no_update, dash.no_update

# Open modal on row selection callback


""" @callback(
    Output("row-selection-modal", "is_open"),
    Output("row-selection-modal-content", "children"),
    Input("row-selection-popup-popup", "selectedRows"),
    Input("row-selection-modal-close", "n_clicks"),
)
def open_modal(selection, _):
    if ctx.triggered_id == "row-selection-modal-close":
        return False, no_update
    children = []
    if selection:
        regnum = selection[0]["regnum"]
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
            create_ag_grid_table(student_info,  [
                {'field': 'module'},
                {'field': 'mark'},
                {'field': 'grade'},

            ])

        ])
        children.append(info)
        return True, children

    return no_update, no_update """


@ callback(
    Output("modal", "opened"),
    Output("modal", "children"),
    Input("ag_tbl", "n_clicks"),
    Input("ag_tbl", "selectedRows"),
    State("modal", "opened"),
    prevent_initial_call=True,
)
def output_selected_rows(n_clicks, selected_rows, opened):
    ctx = dash.callback_context
    # print(ctx.triggered[0]['prop_id'])
    children = []
    if ctx.triggered[0]['prop_id'] == "ag_tbl.selectedRows":
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
        row = dmc.Text("Extra small text", size="xs")
        children.append(row)
        return dash.no_update, dash.no_update

import os
import dash
import numpy as np
import pandas as pd
import dash_ag_grid as dag
import plotly.graph_objs as go
from dash import dcc, html, callback, dash_table, no_update, State, ctx
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from flask_login import current_user
from dash_iconify import DashIconify


def apply_grading_rule(grading_rule, mark):
    for x in grading_rule.split('##'):
        upper = int(x.split("#+")[0])
        lower = int(x.split("#+")[1])
        if mark >= lower and mark <= upper:
            grade = x.split('#+')[2]
    return grade


def determine_decision(group):
    if 'F' in group['grade'].values or 'Fail' in group['grade'].values or "T" in group['grade'].values or "EX" in group['grade'].values:
        if 'F' in group['grade'].values or 'Fail' in group['grade'].values:
            return 'FAILED AT LEAST ONE MODULE'
        elif 'T' in group['grade'].values:
            return 'TO WRITE AS FIRST ATTEMPT'
        elif "EX" in group['grade'].values:
            return 'EXCEMPTED ON AT LEAST ONE MODULE'
    else:
        return 'PASSED ALL MODULES'


parent_dir = os.path.dirname(__file__)
grad_parent = os .path.dirname(parent_dir)
file_path = os.path.join(grad_parent, 'data/period220.csv')
# print(file_path)


def load_dataframe():
    data = pd.read_csv('./data/period220.csv')
    # data = data.drop(columns=['mark.1', 'id'])
    # data = data.drop_duplicates(['regnum', 'module'], keep='last')
    data['grade'] = data.apply(lambda row: apply_grading_rule(
        row['gradingrule'], row['mark']), axis=1)

    # Create the 'decision' column based on grades
    df = data.groupby('regnum').apply(
        determine_decision).reset_index(name='decision')
    new_df = data.merge(df, on='regnum', how='left')
    new_df['decision'] = np.where(new_df['grade'].isin(
        ['F', 'Fail']), 'FAILED AT LEAST ONE MODULE', new_df['decision'])
    new_df['decision'] = np.where(
        new_df['grade'] == "EX", 'EXCEMPTED ON AT LEAST ONE MODULE', new_df['decision'])
    new_df['decision'] = np.where(
        new_df['grade'] == "T", 'TO WRITE AS FIRST ATTEMPT', new_df['decision'])

    # Process the 'gender' column
    new_df['gender'] = new_df['gender'].replace(
        {'female': 'Female', 'male': 'Male', "MALE": "Male", "FEMALE": "Female", "M": "Male", "F": "Female"})

    return new_df


""" def create_table(df):
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
    table = [html.Thead(header), html.Tbody(rows)]
    return table """


data = load_dataframe()
faculties = data.faculty.unique().tolist()
faculty_selection = dmc.Select(
    label="Select Faculty",
    id="faculty_selection",
    searchable=True,
    # clearable=True,
    data=faculties,
    value=faculties[0],

)

dash.register_page(__name__,
                   path='/',  # '/' is home page and it represents the url
                   name='Home',  # name of page, commonly used as name of link
                   title='Academicboard',  # title that appears on browser's tab
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
            style={"marginBottom": "10px", "marginTop": "10px"}
        ),
        dmc.Grid(
            children=[
                dmc.Col(
                    dmc.Paper(
                        children=[
                            dcc.Graph(id="decision_distribution") if 'decision' in data.columns else dcc.Graph(
                                id="failedmodules_distribution"),

                        ],
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
            gutter="md", style={"marginBottom": "10px"}
        ),
        dmc.Grid(
            children=[

                dmc.Col([
                    dmc.Paper(
                        id="tbl",
                        children=[],
                        shadow="xs",
                        style={"padding": "10px"}
                    )] if 'decision' in data.columns else dmc.Paper(
                        id="failedmodules_table",
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
            )if 'decision' in data.columns else dmc.Modal(
                title="Student Information",
                size="80%",
                id="failedmodules_modal",
                zIndex=10000,
                children=[dmc.Text("This is a vertically centered modal.")],
            ),
        ], style={'marginBottom': "20px"}),
        dmc.Select(
            label="Select Programme",
            searchable=True,
            # clearable=True,
            id="programme_selection",

        ),

        dmc.Grid(
            children=[
                dmc.Col([
                    dmc.Select(
                        label="Select Attendance Type",
                        searchable=True,
                        # clearable=True,
                        id="attendancetype_selection",

                    ),

                ], span="auto"),
                dmc.Col([
                    dmc.Select(
                        label="Select Academic Year",
                        searchable=True,
                        # clearable=True,
                        id="academicyear_selection",
                    ),

                ], span="auto"),
                dmc.Col([
                    dmc.Select(
                        label="Select Semester",
                        searchable=True,
                        # clearable=True,
                        id="semester_selection",

                    )

                ], span="auto"),

            ], style={"marginTop": "10px", "marginBottom": "10px"}
        ),
        dmc.Grid(
            children=[
                dmc.Col([
                    dmc.Paper(
                        children=[
                            dcc.Graph(id="programme_decisions")
                            if 'decision' in data.columns else dcc.Graph(id="failedmodules_programme_decisions"),

                        ],
                        shadow="xs",
                    )
                ], span="auto"),

            ], style={"marginBottom": "20px"}
        ),
        dmc.Grid(gutter="xl", children=[
            dmc.Col([

                dmc.Paper(
                        id="programme-decision-table",
                        children=[],
                        shadow="xs",
                        style={"padding": "10px"}
                )if 'decision' in data.columns else dmc.Paper(
                    id="failedmodules_programme_table",
                    children=[],
                    shadow="xs",
                    style={"padding": "10px"}
                )], span="auto"),
        ]),
        dmc.Paper(
            children=[dcc.Graph(id="module_performance")],
            shadow="xs",
            style={"marginTop": "20px", "padding": "10px"}
        ),
        html.Div(id="programme_selected_rows", children=[
            dmc.Modal(
                title="Student Information",
                size="80%",
                id="modal2",
                zIndex=10000,
                children=[dmc.Text("This is a vertically centered modal.")],
            ) if 'decision' in data.columns else dmc.Modal(
                title="Student Information",
                size="80%",
                id="failedmodules_programme_modal",
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
     Input("programme_selection", "value"),
     Input("attendancetype_selection", "value"),
     Input("academicyear_selection", "value"),
     Input("semester_selection", "value")]
)
def module_pass_rate(faculty, programme, attendancetype, academicyear, semester):
    def calculate_failed(grades):
        return grades[grades.isin(['F', 'Fail'])].count()

    def calculate_passed(grades):
        return grades[~grades.isin(['F', 'Fail', 'EX', 'T'])].count()

    def calculate_exampted(grades):
        return grades[grades.isin(['EX'])].count()

    df = data[(data['faculty'] == faculty) & (data['programme'] == programme) & (data['attendancetype'] ==
                                                                                 attendancetype) & (data['academicyear'] == int(academicyear)) & (data['semester'] == int(semester))]
    """ module_pass_rate = df.groupby(
        'module')['mark'].apply(lambda x: (x >= 50).mean() * 100).reset_index(
        name="Pass Rate")
    grouped_data = df.groupby(by="module")[
        'regnum'].nunique().reset_index(name="Students")
    average_marks = df.groupby('module')['mark'].mean().reset_index()
    failed_students = df[df['mark'] < 50].groupby(
        by="module")['regnum'].nunique().reset_index(name="Students") """
    grouped_data = df.groupby('module').agg(
        totalstudents=('regnum', 'nunique'),
        avgmark=('mark', 'mean'),
        failedstudents=('grade', calculate_failed),
        passedstudents=('grade', calculate_passed),
        examptedstudents=('grade', calculate_exampted),
        # Count 'T' grades as students to write on first attempt
        twfastudents=('grade', lambda x: (x == 'T').sum()),
        # passrate=('mark', lambda x: (x >= 50).mean() * 100)
    ).reset_index()
    grouped_data['passrate'] = (grouped_data['passedstudents'] /
                                (grouped_data['totalstudents'] - grouped_data['examptedstudents'] - grouped_data['twfastudents'])) * 100
    grouped_data['passrate'] = grouped_data['passrate'].fillna(0)
    grouped_data['passrate'] = grouped_data['passrate'].astype(int)
    grouped_data['avgmark'] = grouped_data['avgmark'].astype(int)
    return {
        "data": [
            go.Bar(
                x=grouped_data['module'],
                y=grouped_data['passrate'],
                name="Module Pass Rates",
                marker=dict(
                    color="orange",
                ),
                hoverinfo="text",
                hovertext="<b> Module: </b>" +
                grouped_data['module'] + "<br>" +
                "<b>Total Students: </b>" +
                grouped_data['totalstudents'].astype(str) + "<br>" +
                "<b>Students Passed: </b>" +
                grouped_data['passedstudents'].astype(str)+"<br>" +
                "<b>Students Failed: </b>" +
                grouped_data['failedstudents'].astype(str) + "<br>" +
                "<b>Students Exampted: </b>" +
                grouped_data['examptedstudents'].astype(str) + "<br>" +
                "<b>Writing on first attempt: </b>" +
                grouped_data['twfastudents'].astype(str) + "<br>" +
                "<b>Average Mark: </b>" + grouped_data['avgmark'].astype(str) + '<br>' +
                "<b> Pass Rate: </b>" +
                grouped_data["passrate"].astype(str)

            )
        ],
        "layout": go.Layout(
            barmode="stack",
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            title={
                "text": "<b>Student Performance by Module: Pass Rate Distribution</b>",
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
                title="<b> Pass Rate(%) </b>",
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
    df = data[(data['faculty'] == faculty) & (data['attendancetype'] == attendancetype) & (
        data['programme'] == programme) & (data['academicyear'] == int(academicyear)) & (data['semester'] == int(semester))]
    data_grouped = df.groupby(by="decision")[
        'regnum'].nunique().reset_index(
        name="Students")
    # print(data_grouped)
    return {
        'data': [
            go.Pie(
                labels=[
                    f"{decision}({data_grouped[data_grouped['decision']== decision]['Students'].iloc[0]})" for decision in data_grouped.decision],
                values=data_grouped["Students"],
                hoverinfo="label+value+percent",
                textinfo="percent",
                texttemplate="<b>%{percent}</b>",
                textfont=dict(size=14),
                hole=.7,
                rotation=45
            )
        ],
        "layout": go.Layout(
            hovermode='closest',
            title={
                "text": f"<b>Decision Distribution({df.regnum.nunique()})</b>",
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
                'orientation': 'v',
                "xanchor": 'right',
                "x": 1,
                "y": 1
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
                labels=[
                    f"{gender}({data_grouped[data_grouped['gender']==gender]['Students'].iloc[0]})" for gender in data_grouped.gender],
                values=data_grouped["Students"],
                hoverinfo="label+value+percent",
                textinfo="percent",
                texttemplate="<b>%{percent}</b>",
                textfont=dict(size=12),
                hole=.7,
                rotation=45
            )
        ],
        "layout": go.Layout(
            hovermode='closest',
            title={
                "text": "<b>Gender Distribution</b>",
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
                "orientation": 'v',
                "xanchor": 'right',
                "x": 0,
                "y": 0
            },
            font=dict(
                family="sans-serif",
                size=12,
                color='black'
            )
        )
    }

# Failed modules distribution


@callback(
    Output('failedmodules_distribution', "figure"),
    Input("faculty_selection", "value")
)
def update_failedmodules(faculty):
    data_grouped = data[(data['faculty'] == faculty)].groupby(by="failedmodules")[
        'regnum'].nunique()
    data_grouped = data_grouped.reset_index(
        name="Students")
    # print(data_grouped)
    return {
        'data': [
            go.Pie(
                labels=[
                    f'Modules: {failedmodule}' for failedmodule in data_grouped.failedmodules],
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
                "text": "Failed Modules Distribution ",
                "y": 0.93,
                "x": 0.6,
                "xanchor": 'right',
                "yanchor": 'top',

            },
            titlefont={
                "color": "black",
                "size": 16
            },
            legend={
                "orientation": 'v',
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
# failed modules programme decisions


@callback(
    Output('failedmodules_programme_decisions', "figure"),
    [
        Input("faculty_selection", "value"),
        Input("programme_selection", "value"),
        Input("attendancetype_selection", "value"),
        Input("academicyear_selection", "value"),
        Input("semester_selection", "value")]
)
def failedmodules_programme_distribution(faculty, programme, attendancetype, academicyear, semester):
    data_grouped = data[(data['faculty'] == faculty) & (data['programme'] == programme) &
                        (data['attendancetype'] == attendancetype) & (data['academicyear'] == int(academicyear)) &
                        (data['semester'] == int(semester))].groupby(by="failedmodules")[
        'regnum'].nunique()
    data_grouped = data_grouped.reset_index(
        name="Students")
    # print("failed modules ", data_grouped)
    return {
        'data': [
            go.Pie(
                labels=[
                    f'Modules: {failedmodule}' for failedmodule in data_grouped.failedmodules],
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
                "text": "Failed Modules Distribution ",
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
                labels=[
                    f"{decision}({data_grouped[data_grouped['decision']== decision]['Students'].iloc[0]})" for decision in data_grouped.decision],
                # labels=data_grouped.decision,
                values=data_grouped["Students"],
                hoverinfo="label+value+percent",
                textinfo="percent",
                texttemplate="<b>%{percent}</b>",
                textfont=dict(size=12),
                hole=.7,
                rotation=45
            )
        ],
        "layout": go.Layout(
            hovermode='closest',
            title={
                "text": f"<b>Decision Distribution({data[(data['faculty'] == faculty)].regnum.nunique()})</b>",
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
                "x": 0,
                "y": 0
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
            academicyear = click_data['points'][0]['label'].split(
                '(')[0].split(' ')[2]
            # print(academicyear.split('.'))
            if int(academicyear) in df['academicyear'].unique().tolist():

                data_grouped = df[df['academicyear'] == int(academicyear)].groupby(
                    by='semester')['regnum'].nunique().reset_index(name="Students")

                # returning the fig and unhiding the back button
                return {
                    'data': [
                        go.Pie(
                            labels=[
                                f"Academic Year {academicyear}.{semester}({data_grouped[data_grouped['semester']==semester]['Students'].iloc[0]})" for semester in data_grouped.semester],
                            values=data_grouped["Students"],
                            hoverinfo="label+value+percent",
                            textinfo="percent",
                            texttemplate="<b>%{percent}</b>",
                            textfont=dict(size=12),
                            hole=.7,
                            rotation=45
                        )
                    ],
                    "layout": go.Layout(
                        hovermode='closest',
                        title={
                            "text": "<b>Semester Students Distribution</b>",
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
                            "x": 0,
                            "y": 0
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
                                f"Academic Year {academicyear}.{semester}({data_grouped[data_grouped['semester']==semester]['Students'].iloc[0]})" for semester in data_grouped.semester],
                            values=data_grouped["Students"],
                            hoverinfo="label+value+percent",
                            textinfo="percent",
                            texttemplate="<b>%{percent}</b>",
                            textfont=dict(size=12),
                            hole=.7,
                            rotation=45
                        )
                    ],
                    "layout": go.Layout(

                        hovermode='closest',
                        title={
                            "text": "<b>Academic Year Students Distribution</b>",
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
                            "x": 0,
                            "y": 0
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
                        f"Academic Year {academicyear}({data_grouped[data_grouped['academicyear']==academicyear]['Students'].iloc[0]})" for academicyear in data_grouped.academicyear],
                    values=data_grouped["Students"],
                    hoverinfo="label+value+percent",
                    textinfo="percent",
                    texttemplate="<b>%{percent}</b>",
                    textfont=dict(size=12),
                    hole=.7,
                    rotation=45
                )
            ],
            "layout": go.Layout(
                hovermode='closest',
                title={
                    "text": "<b>Academic Year Students Distribution</b>",
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
                    "x": 0,
                    "y": 0
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
                                                                                 == attendancetype) & (data['academicyear'] == int(academicyear)) & (data['semester'] == int(semester))]
    decisions = df['decision'].unique().tolist()
    if trigger_id == 'programme_decisions':

        # get vendor name from clickData
        if click_data is not None:
            decision = click_data['points'][0]['label'].split('(')[0]
            # print(academicyear.split('.'))
            if decision in decisions:

                new_df = df[df['decision'] == decision]
                if decision == "FAILED AT LEAST ONE MODULE":
                    grouped_data = new_df[new_df['grade'].isin(['Fail', 'F'])].groupby(
                        'regnum')['module'].apply(list).reset_index(name="failedmodules")
                    new_df = new_df.merge(
                        grouped_data, on='regnum', how='left').drop_duplicates(
                        ['regnum'], keep='last')
                    header = {
                        "headerName": "Failed Modules",
                        'field': 'failedmodules',
                        "cellEditorPopup": True,
                        "cellEditorPopupPosition": "under",
                    }
                elif decision == 'EXAMPTED ON AT LEAST ONE MODULE':
                    grouped_data = new_df[new_df['grade'] == 'EX'].groupby(
                        'regnum')['module'].apply(list).reset_index(name="exampted_modules")
                    new_df = new_df.merge(
                        grouped_data, on='regnum', how='left').drop_duplicates(
                        ['regnum'], keep='last')
                    header = {
                        "headerName": "Exampted Modules",
                        'field': 'exampted_modules',
                        "cellEditorPopup": True,
                        "cellEditorPopupPosition": "under",
                    }
                elif decision == "TO WRITE AS FIRST ATTEMPT":
                    grouped_data = new_df[new_df['grade'] == 'T'].groupby('regnum')['module'].apply(
                        list).reset_index(name="modules_to_write_as_first_attempt")
                    new_df = new_df.merge(
                        grouped_data, on='regnum', how='left').drop_duplicates(
                        ['regnum'], keep='last')
                    header = {
                        "headerName": "To Write As First Attempt Modules",
                        'field': 'modules_to_write_as_first_attempt',
                        "cellEditorPopup": True,
                        "cellEditorPopupPosition": "under",
                    }

                else:
                    new_df = new_df.drop_duplicates(
                        ['regnum'], keep='last')
                    header = {
                        "headerName": "decision",
                        'field': 'decision',
                        "cellEditorPopup": True,
                        "cellEditorPopupPosition": "under",
                    }

                # print("You clicked", new_df)
                ag_table = dmc.Accordion(
                    children=[
                        dmc.AccordionItem(
                            [
                                dmc.AccordionControl(f"{decision}",
                                                     icon=DashIconify(
                                                         icon="tabler:user",
                                                         width=20,
                                                     ),
                                                     ),
                                dmc.AccordionPanel(
                                    html.Div([
                                        html.Div([
                                            html.Div([
                                                dmc.ActionIcon(
                                                    DashIconify(
                                                        icon="bi:download"),
                                                    size="sm",
                                                    variant="subtle",
                                                    id="csv-button",
                                                    n_clicks=0,
                                                    mb=10,
                                                    style={
                                                        "marginLeft": "5px"}
                                                ),

                                            ], style={"display": "flex"}),
                                            dmc.Switch(
                                                id='cell-editing',
                                                label="Edit Mode",
                                                onLabel="ON",
                                                offLabel="OFF",
                                                checked=False
                                            )
                                        ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}),

                                        dag.AgGrid(
                                            id="programme_decision_table",
                                            rowData=new_df.to_dict(
                                                "records"),
                                            columnDefs=[
                                                {
                                                    "headerName": "RegNum",
                                                    'field': 'regnum'
                                                },
                                                {
                                                    "headerName": "First Name",
                                                    'field': 'firstnames'
                                                },
                                                {
                                                    "headerName": "Surname",
                                                    'field': 'surname'
                                                },
                                                header
                                            ],
                                            columnSize="sizeToFit",
                                            defaultColDef={
                                                "filter": True},
                                            csvExportParams={
                                                "fileName": f"{decisions[0]}.csv",
                                            },
                                            dashGridOptions={
                                                "rowSelection": "single", "animateRows": False, "rowHeight": 40},
                                        ), html.Div(id="output-1")

                                    ])
                                ),
                            ],
                            value="customization",
                        ),
                    ],
                    value=["flexibility", ],
                    transitionDuration=1000
                )
                return ag_table

        else:
            new_df = df[df["decision"] == decisions[-1]].drop_duplicates(
                ['regnum'], keep='last')
            ag_table = dmc.Accordion(
                children=[
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl(f"{decisions[-1]}",
                                                 icon=DashIconify(
                                                     icon="tabler:user",
                                                     width=20,
                                                 ),
                                                 ),
                            dmc.AccordionPanel(
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            dmc.ActionIcon(
                                                DashIconify(
                                                    icon="bi:download"),
                                                size="sm",
                                                variant="subtle",
                                                id="csv-button",
                                                n_clicks=0,
                                                mb=10,
                                                style={
                                                    "marginLeft": "5px"}
                                            ),

                                        ], style={"display": "flex"}),
                                        dmc.Switch(
                                            id='cell-editing',
                                            label="Edit Mode",
                                            onLabel="ON",
                                            offLabel="OFF",
                                            checked=False
                                        )
                                    ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}),

                                    dag.AgGrid(
                                        id="programme_decision_table",
                                        rowData=new_df.to_dict(
                                            "records"),
                                        columnDefs=[
                                            {
                                                "headerName": "RegNum",
                                                'field': 'regnum'
                                            },
                                            {
                                                "headerName": "First Name",
                                                'field': 'firstnames'
                                            },
                                            {
                                                "headerName": "Surname",
                                                'field': 'surname'
                                            },
                                            {
                                                "headerName": "Dicision",
                                                'field': 'decision',

                                                "cellEditorPopup": True,
                                                "cellEditorPopupPosition": "under",
                                            }
                                        ],
                                        columnSize="sizeToFit",
                                        defaultColDef={
                                            "filter": True},
                                        csvExportParams={
                                            "fileName": f"{decisions[0]}.csv",
                                        },
                                        dashGridOptions={
                                            "rowSelection": "single", "animateRows": False, "rowHeight": 40},
                                    ), html.Div(id="output-1")

                                ])
                            ),
                        ],
                        value="customization",
                    ),
                ],
                value=["flexibility", ],
                transitionDuration=1000
            )
            return ag_table
    else:
        if len(decisions) > 0:
            new_df = df[df["decision"] == decisions[-1]]
            if decisions[-1] == "FAILED AT LEAST ONE MODULE":
                grouped_data = new_df[new_df['grade'].isin(['Fail', 'F'])].groupby(
                    'regnum')['module'].apply(list).reset_index(name="failedmodules")
                new_df = new_df.merge(
                    grouped_data, on='regnum', how='left').drop_duplicates(
                    ['regnum'], keep='last')
                header = {
                    "headerName": "Failed Modules",
                    'field': 'failedmodules',
                    "cellEditorPopup": True,
                    "cellEditorPopupPosition": "under",
                }
            elif decisions[-1] == 'EXAMPTED ON AT LEAST ONE MODULE':
                grouped_data = new_df[new_df['grade'] == 'EX'].groupby(
                    'regnum')['module'].apply(list).reset_index(name="exampted_modules")
                new_df = new_df.merge(
                    grouped_data, on='regnum', how='left').drop_duplicates(
                    ['regnum'], keep='last')
                header = {
                    "headerName": "Exampted Modules",
                    'field': 'exampted_modules',
                    "cellEditorPopup": True,
                    "cellEditorPopupPosition": "under",
                }
            elif decisions[-1] == "TO WRITE AS FIRST ATTEMPT":
                grouped_data = new_df[new_df['grade'] == 'T'].groupby('regnum')['module'].apply(
                    list).reset_index(name="modules_to_write_as_first_attempt")
                new_df = new_df.merge(
                    grouped_data, on='regnum', how='left').drop_duplicates(
                    ['regnum'], keep='last')
                header = {
                    "headerName": "To Write As First Attempt Modules",
                    'field': 'modules_to_write_as_first_attempt',
                    "cellEditorPopup": True,
                    "cellEditorPopupPosition": "under",
                }

            else:
                new_df = new_df.drop_duplicates(
                    ['regnum'], keep='last')
                header = {
                    "headerName": "decision",
                    'field': 'decision',
                    "cellEditorPopup": True,
                    "cellEditorPopupPosition": "under",
                }

            ag_table = dmc.Accordion(
                children=[
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl(f"{decisions[-1]}",
                                                 icon=DashIconify(
                                                     icon="tabler:user",
                                                     width=20,
                                                 ),
                                                 ),
                            dmc.AccordionPanel(
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            dmc.ActionIcon(
                                                DashIconify(
                                                    icon="bi:download"),
                                                size="sm",
                                                variant="subtle",
                                                id="csv-button",
                                                n_clicks=0,
                                                mb=10,
                                                style={
                                                    "marginLeft": "5px"}
                                            ),

                                        ], style={"display": "flex"}),
                                        dmc.Switch(
                                            id='cell-editing',
                                            label="Edit Mode",
                                            onLabel="ON",
                                            offLabel="OFF",
                                            checked=False
                                        )
                                    ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}),

                                    dag.AgGrid(
                                        id="programme_decision_table",
                                        rowData=new_df.to_dict(
                                            "records"),
                                        columnDefs=[
                                            {
                                                "headerName": "RegNum",
                                                'field': 'regnum'
                                            },
                                            {
                                                "headerName": "First Name",
                                                'field': 'firstnames'
                                            },
                                            {
                                                "headerName": "Surname",
                                                'field': 'surname'
                                            },
                                            header
                                        ],
                                        columnSize="sizeToFit",
                                        defaultColDef={
                                            "filter": True},
                                        csvExportParams={
                                            "fileName": f"{decisions[0]}.csv",
                                        },
                                        dashGridOptions={
                                            "rowSelection": "single", "animateRows": False, "rowHeight": 40},
                                    ), html.Div(id="output-1")

                                ])
                            ),
                        ],
                        value="customization",
                    ),
                ],
                value=["flexibility", ],
                transitionDuration=1000
            )
            return ag_table
        else:
            return dmc.Alert(
                "Based on the selection you have made there is no data to display",
                title="No data to display",
            )

# Download csv file


@callback(
    Output("programme_decision_table", "exportDataAsCsv"),
    Input("csv-button", "n_clicks"),
)
def export_data_as_csv(n_clicks):
    if n_clicks:
        return True
    return False
# ag grid edit


@callback(
    Output('programme_decision_table', 'defaultColDef'),
    Input('cell-editing-switch', 'checked')
)
def update_cell_editing_options(checked):
    if checked:
        return {"editable": True, "filter": True}
    else:
        return {"editable": False, "filter": True}


@callback(
    Output("output-1", "children"), Input(
        "programme_decision_table", "cellValueChanged")
)
def update(cell_changed):
    if cell_changed:
        """ student = Student(
            regnum=cell_changed[0]['data']['regnum'],
            firstnames=cell_changed[0]['data']['firstnames'],
            surname=cell_changed[0]['data']['surname'],
            programmecode=cell_changed[0]['data']['programmecode'],
            decision=cell_changed[0]['data']['decision'],
            faculty=cell_changed[0]['data']['faculty'],
            grade=cell_changed[0]['data']['grade'],
        )
        db.session.add(student)
        db.session.commit() """
        return dmc.Alert(f"Database updated with edited data: {cell_changed[0]['data']['firstnames']}", title="Success!", color="green")
    return None

# Failed modules table


@callback(
    Output('failedmodules_table', "children"),
    [Input("failedmodules_distribution", "clickData"),
     Input("faculty_selection", "value")]
)
def failedmodules_table(click_data, faculty):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    df = data[data['faculty'] == faculty].drop_duplicates(
        ['regnum'], keep='last')
    failedmodules = df['failedmodules'].unique().tolist()
    if trigger_id == 'failedmodules_distribution':

        # get vendor name from clickData
        if click_data is not None:
            failedmodule = int(click_data['points'][0]['label'].split(' ')[-1])
            # print(failedmodule)
            if failedmodule in failedmodules:
                # print("Module is in modules")
                new_df = df[df['failedmodules'] == failedmodule]
                ag_table = html.Div([
                    html.Div([
                        html.Div([
                            dmc.Text(
                                f"Failed Modules: {failedmodule}", weight=500),
                            dmc.ActionIcon(
                                DashIconify(icon="bi:download"),
                                size="sm",
                                variant="subtle",
                                id="failedmodules_tbl-btn",
                                n_clicks=0,
                                mb=10,
                                style={"marginLeft": "5px"}
                            ),

                        ], style={"display": "flex"}),
                        dmc.Switch(
                            id='cell-editing',
                            label="Edit Mode",
                            onLabel="ON",
                            offLabel="OFF",
                            checked=False
                        )
                    ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}),
                    dag.AgGrid(
                        id="failedmodules_tbl",
                        rowData=new_df.to_dict("records"),
                        columnDefs=[
                            {
                                "headerName": "RegNum",
                                'field': 'regnum'
                            },
                            {
                                "headerName": "First Name",
                                'field': 'firstnames'
                            },
                            {
                                "headerName": "Surname",
                                'field': 'surname'
                            },
                            {
                                "headerName": "Decision",
                                'field': 'decision',
                                "cellEditorPopup": True,

                                "cellEditorPopupPosition": "under",
                            }
                        ],
                        columnSize="sizeToFit",
                        defaultColDef={"filter": True},
                        csvExportParams={
                            "fileName": f"Failed_{failedmodule}.csv",
                        },
                        dashGridOptions={
                            "rowSelection": "single", "animateRows": False, "rowHeight": 40},
                    ),
                ])
                return ag_table

        else:
            new_df = df[df["failedmodules"] == failedmodules[0]]
            ag_table = html.Div([
                html.Div([
                    html.Div([
                        dmc.Text(
                            f"Failed Modules: {failedmodules[0]}", weight=500),
                        dmc.ActionIcon(
                            DashIconify(icon="bi:download"),
                            size="sm",
                            variant="subtle",
                            id="failedmodules_tbl-btn",
                            n_clicks=0,
                            mb=10,
                            style={"marginLeft": "5px"}
                        ),

                    ], style={"display": "flex"}),
                    dmc.Switch(
                        id='cell-editing',
                        label="Edit Mode",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=False
                    )
                ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}),

                dag.AgGrid(
                    id="failedmodules_tbl",
                    rowData=new_df.to_dict("records"),
                    columnDefs=[
                        {
                            "headerName": "RegNum",
                            'field': 'regnum'
                        },
                        {
                            "headerName": "First Name",
                            'field': 'firstnames'
                        },
                        {
                            "headerName": "Surname",
                            'field': 'surname'
                        },
                        {
                            "headerName": "Decision",
                            'field': 'decision',
                            "cellEditorPopup": True,
                            "cellEditorPopupPosition": "under",
                        }
                    ],
                    columnSize="sizeToFit",
                    defaultColDef={"filter": True},
                    csvExportParams={
                        "fileName": f"Failed_{failedmodules[0]}.csv",
                    },
                    dashGridOptions={
                        "rowSelection": "single", "animateRows": False, "rowHeight": 40},
                ), html.Div(id="output")

            ])
            return ag_table
    else:
        if len(failedmodules) > 0:
            new_df = df[df["failedmodules"] == failedmodules[0]]
            ag_table = html.Div([
                html.Div([
                    html.Div([
                        dmc.Text(
                            f"Failed Modules: {failedmodules[0]}", weight=500),
                        dmc.ActionIcon(
                            DashIconify(icon="bi:download"),
                            size="sm",
                            variant="subtle",
                            id="failedmodules_tbl-btn",
                            n_clicks=0,
                            mb=10,
                            style={"marginLeft": "5px"}
                        ),

                    ], style={"display": "flex"}),
                    dmc.Switch(
                        id='cell-editing',
                        label="Edit Mode",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=False
                    )
                ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}),

                dag.AgGrid(
                    id="failedmodules_tbl",
                    rowData=new_df.to_dict("records"),
                    columnDefs=[
                        {
                            "headerName": "RegNum",
                            'field': 'regnum'
                        },
                        {
                            "headerName": "First Name",
                            'field': 'firstnames'
                        },
                        {
                            "headerName": "Surname",
                            'field': 'surname'
                        },
                        {
                            "headerName": "Decision",
                            'field': 'decision',

                            "cellEditorPopup": True,
                            "cellEditorPopupPosition": "under",
                        }
                    ],
                    columnSize="sizeToFit",
                    defaultColDef={"filter": True},
                    csvExportParams={
                        "fileName": f"failed_{failedmodules[0]}.csv",
                    },
                    dashGridOptions={
                        "rowSelection": "single", "animateRows": False, "rowHeight": 40},
                ), html.Div(id="output")

            ])
            return ag_table
        return dmc.Alert(
            "Something happened! You made a mistake and there is no going back, your data was lost forever!",
            title="No data to display",
        )
# Download csv
# Download csv


@callback(
    Output("failedmodules_tbl", "exportDataAsCsv"),
    Input("failedmodules_tbl-btn", "n_clicks"),
)
def export_data(n_clicks):
    if n_clicks:
        return True
    return False

# failed modules programme table


@callback(
    Output('failedmodules_programme_table', "children"),
    [Input("failedmodules_programme_decisions", "clickData"),
     Input("faculty_selection", "value"),
        Input("programme_selection", "value"),
        Input("attendancetype_selection", "value"),
        Input("academicyear_selection", "value"),
        Input("semester_selection", "value")]
)
def failedmodules_programme_table(click_data, faculty, programme, attendancetype, academicyear, semester):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    df = data[(data['faculty'] == faculty) & (data['programme'] == programme) & (data['attendancetype'] == attendancetype) &
              (data['academicyear'] == int(academicyear)) & (data['semester'] == int(semester))].drop_duplicates(
        ['regnum'], keep='last')
    failedmodules = df['failedmodules'].unique().tolist()
    if trigger_id == 'failedmodules_programme_decisions':

        # get vendor name from clickData
        if click_data is not None:
            failedmodule = int(click_data['points'][0]['label'].split(' ')[-1])
            # print(failedmodule)
            if failedmodule in failedmodules:
                # print("Module is in modules")
                new_df = df[df['failedmodules'] == failedmodule]
                ag_table = html.Div([
                    html.Div([
                        html.Div([
                            dmc.Text(
                                f"Failed Modules: {failedmodule}", weight=500),
                            dmc.ActionIcon(
                                DashIconify(icon="bi:download"),
                                size="sm",
                                variant="subtle",
                                id="failedmodules_programme_tbl-btn",
                                n_clicks=0,
                                mb=10,
                                style={"marginLeft": "5px"}
                            ),

                        ], style={"display": "flex"}),
                        dmc.Switch(
                            id='cell-editing',
                            label="Edit Mode",
                            onLabel="ON",
                            offLabel="OFF",
                            checked=False
                        )
                    ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}),
                    dag.AgGrid(
                        id="failedmodules_programme_tbl",
                        rowData=new_df.to_dict("records"),
                        columnDefs=[
                            {
                                "headerName": "RegNum",
                                'field': 'regnum'
                            },
                            {
                                "headerName": "First Name",
                                'field': 'firstnames'
                            },
                            {
                                "headerName": "Surname",
                                'field': 'surname'
                            },
                            {
                                "headerName": "Decision",
                                'field': 'decision',
                                "cellEditorPopup": True,

                                "cellEditorPopupPosition": "under",
                            }
                        ],
                        columnSize="sizeToFit",
                        defaultColDef={"filter": True},
                        csvExportParams={
                            "fileName": f"{failedmodule}.csv",
                        },
                        dashGridOptions={
                            "rowSelection": "single", "animateRows": False, "rowHeight": 40},
                    ),
                ])
                return ag_table

        else:
            new_df = df[df["failedmodules"] == failedmodules[0]]
            ag_table = html.Div([
                html.Div([
                    html.Div([
                        dmc.Text(
                            f"Failed Modules: {failedmodules[0]}", weight=500),
                        dmc.ActionIcon(
                            DashIconify(icon="bi:download"),
                            size="sm",
                            variant="subtle",
                            id="failedmodules_programme_tbl-btn",
                            n_clicks=0,
                            mb=10,
                            style={"marginLeft": "5px"}
                        ),

                    ], style={"display": "flex"}),
                    dmc.Switch(
                        id='cell-editing',
                        label="Edit Mode",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=False
                    )
                ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}),

                dag.AgGrid(
                    id="failedmodules_programme_tbl",
                    rowData=new_df.to_dict("records"),
                    columnDefs=[
                        {
                            "headerName": "RegNum",
                            'field': 'regnum'
                        },
                        {
                            "headerName": "First Name",
                            'field': 'firstnames'
                        },
                        {
                            "headerName": "Surname",
                            'field': 'surname'
                        },
                        {
                            "headerName": "decision",
                            'field': 'decision',
                            "cellEditorPopup": True,
                            "cellEditorPopupPosition": "under",
                        }
                    ],
                    columnSize="sizeToFit",
                    defaultColDef={"filter": True},
                    csvExportParams={
                        "fileName": f"{failedmodules[0]}.csv",
                    },
                    dashGridOptions={
                        "rowSelection": "single", "animateRows": False, "rowHeight": 40},
                ), html.Div(id="output")

            ])
            return ag_table
    else:
        if len(failedmodules) > 0:
            new_df = df[df["failedmodules"] == failedmodules[0]]
            ag_table = html.Div([
                html.Div([
                    html.Div([
                        dmc.Text(
                            f"Failed Modules: {failedmodules[0]}", weight=500),
                        dmc.ActionIcon(
                            DashIconify(icon="bi:download"),
                            size="sm",
                            variant="subtle",
                            id="failedmodules_programme_tbl-btn",
                            n_clicks=0,
                            mb=10,
                            style={"marginLeft": "5px"}
                        ),

                    ], style={"display": "flex"}),
                    dmc.Switch(
                        id='cell-editing',
                        label="Edit Mode",
                        onLabel="ON",
                        offLabel="OFF",
                        checked=False
                    )
                ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}),

                dag.AgGrid(
                    id="failedmodules_programme_tbl",
                    rowData=new_df.to_dict("records"),
                    columnDefs=[
                        {
                            "headerName": "RegNum",
                            'field': 'regnum'
                        },
                        {
                            "headerName": "First Name",
                            'field': 'firstnames'
                        },
                        {
                            "headerName": "Surname",
                            'field': 'surname'
                        },
                        {
                            "headerName": "Decision",
                            'field': 'decision',

                            "cellEditorPopup": True,
                            "cellEditorPopupPosition": "under",
                        }
                    ],
                    columnSize="sizeToFit",
                    defaultColDef={"filter": True},
                    csvExportParams={
                        "fileName": f"{failedmodules[0]}.csv",
                    },
                    dashGridOptions={
                        "rowSelection": "single", "animateRows": False, "rowHeight": 40},
                ), html.Div(id="output")

            ])
            return ag_table
        return dmc.Alert(
            "Something happened! You made a mistake and there is no going back, your data was lost forever!",
            title="No data to display",
        )

# Download csv


@callback(
    Output("failedmodules_programme_tbl", "exportDataAsCsv"),
    Input("failedmodules_programme_tbl-btn", "n_clicks"),
)
def export_data(n_clicks):
    if n_clicks:
        return True
    return False
# output failed module programme selected rows


@ callback(
    Output("failedmodules_programme_modal", "opened"),
    Output("failedmodules_programme_modal", "children"),
    Input("failedmodules_programme_tbl", "n_clicks"),
    Input("failedmodules_programme_tbl", "selectedRows"),
    State("failedmodules_programme_modal", "opened"),
    prevent_initial_call=True,
)
def output_failedmodules_programme_selected_rows(n_clicks, selected_rows, opened):
    ctx = dash.callback_context
    # print(ctx.triggered[0]['prop_id'])
    children = []
    if ctx.triggered[0]['prop_id'] == "failedmodules_programme_tbl.selectedRows":
        if selected_rows:
            # print(f"The row is selected {selected_rows}")
            regnum = selected_rows[0]["regnum"]
            student_info = data[data['regnum'] == regnum]

            info = html.Div([
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Registration Number"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['regnum']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("First names"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['firstnames']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Surname"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['surname']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Faculty"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['faculty']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Programme"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['programme']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Attendance Type"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['attendancetype']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Academic Year"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['academicyear']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Semester"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['semester']}"), span=6),
                    ],
                    gutter="xl",
                ),
                html.Br(),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Failed Modules"), span=6),
                        dmc.Col([
                            dmc.Text(
                                f"{student_info['failedmodules'].iloc[0]}")
                        ], span=6),
                    ],
                    gutter="xl",
                ),
                html.Br(),
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
# Output failed module selected rows


@ callback(
    Output("failedmodules_modal", "opened"),
    Output("failedmodules_modal", "children"),
    Input("failedmodules_tbl", "n_clicks"),
    Input("failedmodules_tbl", "selectedRows"),
    State("failedmodules_modal", "opened"),
    prevent_initial_call=True,
)
def output_failedmodules_selected_rows(n_clicks, selected_rows, opened):
    ctx = dash.callback_context
    # print(ctx.triggered[0]['prop_id'])
    children = []
    if ctx.triggered[0]['prop_id'] == "failedmodules_tbl.selectedRows":
        if selected_rows:
            # print(f"The row is selected {selected_rows}")
            regnum = selected_rows[0]["regnum"]
            student_info = data[data['regnum'] == regnum]

            info = html.Div([
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Registration Number"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['regnum']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("First names"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['firstnames']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Surname"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['surname']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Faculty"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['faculty']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Programme"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['programme']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Attendance Type"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['attendancetype']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Academic Year"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['academicyear']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Semester"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['semester']}"), span=6),
                    ],
                    gutter="xl",
                ),


                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Failed Modules"), span=6),
                        dmc.Col([
                            dmc.Text(
                                f"{student_info['failedmodules'].iloc[0]}")
                        ], span=6),
                    ],
                    gutter="xl",
                ),
                html.Br(),
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
# decisions


@callback(
    Output('tbl', "children"),
    [Input("decision_distribution", "clickData"),
     Input("faculty_selection", "value")]
)
def decision_table(click_data, faculty):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    df = data[data['faculty'] == faculty]
    decisions = df['decision'].unique().tolist()
    if trigger_id == 'decision_distribution':

        # get vendor name from clickData
        if click_data is not None:
            decision = click_data['points'][0]['label'].split('(')[0]
            # print(academicyear.split('.'))
            if decision in decisions:
                new_df = df[df['decision'] == decision]
                if decision == "FAILED AT LEAST ONE MODULE":
                    grouped_data = new_df[new_df['grade'].isin(['Fail', 'F'])].groupby(
                        'regnum')['module'].apply(list).reset_index(name="failedmodules")
                    new_df = new_df.merge(
                        grouped_data, on='regnum', how='left').drop_duplicates(
                        ['regnum'], keep='last')
                    header = {
                        "headerName": "Failed Modules",
                        'field': 'failedmodules',
                        "cellEditorPopup": True,
                        "cellEditorPopupPosition": "under",
                    }
                elif decision == 'EXAMPTED ON AT LEAST ONE MODULE':
                    grouped_data = new_df[new_df['grade'] == 'EX'].groupby(
                        'regnum')['module'].apply(list).reset_index(name="exampted_modules")
                    new_df = new_df.merge(
                        grouped_data, on='regnum', how='left').drop_duplicates(
                        ['regnum'], keep='last')
                    header = {
                        "headerName": "Exampted Modules",
                        'field': 'exampted_modules',
                        "cellEditorPopup": True,
                        "cellEditorPopupPosition": "under",
                    }
                elif decision == "TO WRITE AS FIRST ATTEMPT":
                    grouped_data = new_df[new_df['grade'] == 'T'].groupby('regnum')['module'].apply(
                        list).reset_index(name="modules_to_write_as_first_attempt")
                    new_df = new_df.merge(
                        grouped_data, on='regnum', how='left').drop_duplicates(
                        ['regnum'], keep='last')
                    header = {
                        "headerName": "To Write As First Attempt Modules",
                        'field': 'modules_to_write_as_first_attempt',
                        "cellEditorPopup": True,
                        "cellEditorPopupPosition": "under",
                    }

                else:
                    header = {
                        "headerName": "decision",
                        'field': 'decision',
                        "cellEditorPopup": True,
                        "cellEditorPopupPosition": "under",
                    }

                ag_table = dmc.Accordion(
                    children=[
                        dmc.AccordionItem(
                            [
                                dmc.AccordionControl(f"{decision}",
                                                     icon=DashIconify(
                                                         icon="tabler:user",
                                                         width=20,
                                                     ),
                                                     ),
                                dmc.AccordionPanel(
                                    html.Div([
                                        html.Div([
                                            html.Div([
                                                dmc.ActionIcon(
                                                    DashIconify(
                                                        icon="bi:download"),
                                                    size="sm",
                                                    variant="subtle",
                                                    id="csv-btn",
                                                    n_clicks=0,
                                                    mb=10,
                                                    style={"marginLeft": "5px"}
                                                ),

                                            ], style={"display": "flex"}),
                                            dmc.Switch(
                                                id='cell-editing',
                                                label="Edit Mode",
                                                onLabel="ON",
                                                offLabel="OFF",
                                                checked=False
                                            )
                                        ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}),

                                        dag.AgGrid(
                                            id="ag_tbl",
                                            rowData=new_df.to_dict("records"),
                                            columnDefs=[
                                                {
                                                    "headerName": "RegNum",
                                                    'field': 'regnum'
                                                },
                                                {
                                                    "headerName": "First Name",
                                                    'field': 'firstnames'
                                                },
                                                {
                                                    "headerName": "Surname",
                                                    'field': 'surname'
                                                },
                                                header
                                            ],
                                            columnSize="sizeToFit",
                                            defaultColDef={"filter": True},
                                            csvExportParams={
                                                "fileName": f"{decisions[0]}.csv",
                                            },
                                            dashGridOptions={
                                                "rowSelection": "single", "animateRows": False, "rowHeight": 40},
                                        ), html.Div(id="output")

                                    ])
                                ),
                            ],
                            value="customization",
                        ),
                    ],
                    value=["flexibility", ],
                    transitionDuration=1000
                )
                return ag_table

        else:
            new_df = df[df["decision"] == decisions[-1]]
            ag_table = dmc.Accordion(
                children=[
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl(f"{decisions[-1]}",
                                                 icon=DashIconify(
                                                     icon="tabler:user",
                                                     width=20,
                                                 ),
                                                 ),
                            dmc.AccordionPanel(
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            dmc.ActionIcon(
                                                DashIconify(
                                                    icon="bi:download"),
                                                size="sm",
                                                variant="subtle",
                                                id="csv-btn",
                                                n_clicks=0,
                                                mb=10,
                                                style={"marginLeft": "5px"}
                                            ),

                                        ], style={"display": "flex"}),
                                        dmc.Switch(
                                            id='cell-editing',
                                            label="Edit Mode",
                                            onLabel="ON",
                                            offLabel="OFF",
                                            checked=False
                                        )
                                    ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}),

                                    dag.AgGrid(
                                        id="ag_tbl",
                                        rowData=new_df.to_dict("records"),
                                        columnDefs=[
                                            {
                                                "headerName": "RegNum",
                                                'field': 'regnum'
                                            },
                                            {
                                                "headerName": "First Name",
                                                'field': 'firstnames'
                                            },
                                            {
                                                "headerName": "Surname",
                                                'field': 'surname'
                                            },
                                            {
                                                "headerName": "Decision",
                                                'field': 'decision',

                                                "cellEditorPopup": True,
                                                "cellEditorPopupPosition": "under",
                                            }
                                        ],
                                        columnSize="sizeToFit",
                                        defaultColDef={"filter": True},
                                        csvExportParams={
                                            "fileName": f"{decisions[0]}.csv",
                                        },
                                        dashGridOptions={
                                            "rowSelection": "single", "animateRows": False, "rowHeight": 40},
                                    ), html.Div(id="output")

                                ])
                            ),
                        ],
                        value="customization",
                    ),
                ],
                value=["flexibility", ],
                transitionDuration=1000
            )
            return ag_table
    else:
        if len(decisions) > 0:
            new_df = df[df["decision"] == decisions[-1]]
            if decisions[-1] == "FAILED AT LEAST ONE MODULE":
                grouped_data = new_df[new_df['grade'].isin(['Fail', 'F'])].groupby(
                    'regnum')['module'].apply(list).reset_index(name="failedmodules")
                new_df = new_df.merge(
                    grouped_data, on='regnum', how='left').drop_duplicates(
                    ['regnum'], keep='last')
                header = {
                    "headerName": "Failed Modules",
                    'field': 'failedmodules',
                    "cellEditorPopup": True,
                    "cellEditorPopupPosition": "under",
                }
            elif decisions[-1] == 'EXAMPTED ON AT LEAST ONE MODULE':
                grouped_data = new_df[new_df['grade'] == 'EX'].groupby(
                    'regnum')['module'].apply(list).reset_index(name="exampted_modules")
                new_df = new_df.merge(
                    grouped_data, on='regnum', how='left').drop_duplicates(
                    ['regnum'], keep='last')
                header = {
                    "headerName": "Exampted Modules",
                    'field': 'exampted_modules',
                    "cellEditorPopup": True,
                    "cellEditorPopupPosition": "under",
                }
            elif decisions[-1] == "TO WRITE AS FIRST ATTEMPT":
                grouped_data = new_df[new_df['grade'] == 'T'].groupby('regnum')['module'].apply(
                    list).reset_index(name="modules_to_write_as_first_attempt")
                new_df = new_df.merge(
                    grouped_data, on='regnum', how='left').drop_duplicates(
                    ['regnum'], keep='last')
                header = {
                    "headerName": "To Write As First Attempt Modules",
                    'field': 'modules_to_write_as_first_attempt',
                    "cellEditorPopup": True,
                    "cellEditorPopupPosition": "under",
                }

            else:
                header = {
                    "headerName": "decision",
                    'field': 'decision',
                    "cellEditorPopup": True,
                    "cellEditorPopupPosition": "under",
                }

            ag_table = dmc.Accordion(
                children=[
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl(f"{decisions[-1]}",
                                                 icon=DashIconify(
                                                     icon="tabler:user",
                                                     width=20,
                                                 ),
                                                 ),
                            dmc.AccordionPanel(
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            dmc.ActionIcon(
                                                DashIconify(
                                                    icon="bi:download"),
                                                size="sm",
                                                variant="subtle",
                                                id="csv-btn",
                                                n_clicks=0,
                                                mb=10,
                                                style={"marginLeft": "5px"}
                                            ),

                                        ], style={"display": "flex"}),
                                        dmc.Switch(
                                            id='cell-editing',
                                            label="Edit Mode",
                                            onLabel="ON",
                                            offLabel="OFF",
                                            checked=False
                                        )
                                    ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}),

                                    dag.AgGrid(
                                        id="ag_tbl",
                                        rowData=new_df.to_dict("records"),
                                        columnDefs=[
                                            {
                                                "headerName": "RegNum",
                                                'field': 'regnum'
                                            },
                                            {
                                                "headerName": "First Name",
                                                'field': 'firstnames'
                                            },
                                            {
                                                "headerName": "Surname",
                                                'field': 'surname'
                                            },
                                            header
                                        ],
                                        columnSize="sizeToFit",
                                        defaultColDef={"filter": True},
                                        csvExportParams={
                                            "fileName": f"{decisions[0]}.csv",
                                        },
                                        dashGridOptions={
                                            "rowSelection": "single", "animateRows": False, "rowHeight": 40},
                                    ), html.Div(id="output")

                                ])
                            ),
                        ],
                        value="customization",
                    ),
                ],
                value=["flexibility", ],
                transitionDuration=1000
            )

            return ag_table
        return dmc.Alert(
            "Something happened! You made a mistake and there is no going back, your data was lost forever!",
            title="No data to display",
        )
# download csv


@callback(
    Output("ag_tbl", "exportDataAsCsv"),
    Input("csv-btn", "n_clicks"),
)
def export_data(n_clicks):
    if n_clicks:
        return True
    return False
# edit ag grid


@callback(
    Output('ag_tbl', 'defaultColDef'),
    Input('cell-editing', 'checked')
)
def update_cell_editing_options(checked):
    if checked:
        return {"editable": True, "filter": True}
    else:
        return {"editable": False, "filter": True}


@callback(
    Output("output", "children"), Input(
        "ag_tbl", "cellValueChanged")
)
def update_cell(cell_changed):
    if cell_changed:
        """ student = Student(
            regnum=cell_changed[0]['data']['regnum'],
            firstnames=cell_changed[0]['data']['firstnames'],
            surname=cell_changed[0]['data']['surname'],
            programmecode=cell_changed[0]['data']['programmecode'],
            decision=cell_changed[0]['data']['decision'],
            faculty=cell_changed[0]['data']['faculty'],
            grade=cell_changed[0]['data']['grade'],
        )
        db.session.add(student)
        db.session.commit() """
        return dmc.Alert(f"Database updated with edited data: {cell_changed[0]['data']['firstnames']}", title="Success!", color="green")
    return None

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
            # print(" The row is selected")
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
                        dmc.Col(dmc.Text("Faculty"), span=6),
                        dmc.Col(
                            dmc.Text(f"{student_info['faculty'].iloc[0]}"), span=6),
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
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Attendance Type"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['attendancetype']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Academic Year"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['academicyear']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Semester"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['semester']}"), span=6),
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
                        dmc.Col(dmc.Text("Failed Modules"), span=6),
                        dmc.Col([
                            dmc.Text(
                                f"{student_info['decisionextras'].iloc[0]}")
                        ], span=6),
                    ] if student_info['decision'].iloc[0] in ["SUPPLEMENT", "REPEAT", "RETAKE"] else None,
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Repeat Level"), span=6),
                        dmc.Col([
                            dmc.Text(
                                f"{student_info['decisionextras'].iloc[0]}")
                        ], span=6),
                    ] if student_info['decision'].iloc[0] == "REPEAT LEVEL" else None,
                    gutter="xl",
                ),
                html.Br(),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Overall Grade"), span=6),
                        dmc.Col(
                            dmc.Text(f"{student_info['decisionextras'].iloc[0]}"), span=6),
                    ] if student_info['decision'].iloc[0] == "PASS CLASS" else None,
                    gutter="xl",
                ),
                html.Br(),
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
                        dmc.Col(dmc.Text("Faculty"), span=6),
                        dmc.Col(
                            dmc.Text(f"{student_info['faculty'].iloc[0]}"), span=6),
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
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Attendance Type"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['attendancetype']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Academic Year"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['academicyear']}"), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Semester"), span=6),
                        dmc.Col(
                            dmc.Text(f"{selected_rows[0]['semester']}"), span=6),
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
                        dmc.Col(dmc.Text("Failed Modules"), span=6),
                        dmc.Col([
                            dmc.Text(
                                f"{student_info['decisionextras'].iloc[0]}")
                        ], span=6),
                    ] if student_info['decision'].iloc[0] in ["SUPPLEMENT", "REPEAT", "RETAKE"] else None,
                    gutter="xl",
                ),
                html.Br(),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Repeat Level"), span=6),
                        dmc.Col([
                            dmc.Text(
                                f"{student_info['decisionextras'].iloc[0]}")
                        ], span=6),
                    ] if student_info['decision'].iloc[0] == "REPEAT LEVEL" else None,
                    gutter="xl",
                ),
                html.Br(),
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("Overall Grade"), span=6),
                        dmc.Col(
                            dmc.Text(f"{student_info['decisionextras'].iloc[0]}"), span=6),
                    ] if student_info['decision'].iloc[0] == "PASS CLASS" else None,
                    gutter="xl",
                ),
                html.Br(),
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

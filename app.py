import dash
from datetime import datetime
import pandas as pd
import dash_auth
from dash import html, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input

current_year = datetime.now().year


def get_icon(icon):
    return DashIconify(icon=icon, height=16)


MSU_LOGO = "/assets/images/msu-logo.png"

app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        # include google fonts
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;900&display=swap",
        dbc.themes.SPACELAB
    ],
)
app.secret_key = 'testing321'
auth = dash_auth.BasicAuth(
    app,
    {
        "westonmf": "testing321",
        "chaibvan": "testing321"
    }
)
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=MSU_LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand(
                            "AcademicBody", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavLink(
                            [
                                html.Div(page["name"], className="ms-2"),
                            ],
                            href=page["path"],
                            active="exact",
                        )
                        for page in dash.page_registry.values()
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ],
    ),
    color="dark",
    dark=True,
    expand="xl",
    fixed='top'
)


header = dmc.Header(
    height=60, children=[dmc.Grid(
        children=[
            dmc.Group(
                children=[
                    dmc.NavLink(
                        label=page['name'],
                        icon=get_icon(icon="bi:house-door-fill"),

                    )
                    for page in dash.page_registry.values()
                ],
            )
        ],
        gutter="xl",
    )], style={"backgroundColor": "#9c86e2", "display": "flex", "alignItems": "center"}
)


app.layout = dmc.MantineProvider(
    theme={
        "fontFamily": "'Inter', sans-serif",
        "primaryColor": "indigo",
        "components": {
            "Button": {"styles": {"root": {"fontWeight": 400}}},
            "Alert": {"styles": {"title": {"fontWeight": 500}}},
            "AvatarGroup": {"styles": {"truncated": {"fontWeight": 500}}},
        },
    },
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        navbar,
        dmc.Title(f"Academic Body Results Presentation",
                  order=2, style={"marginBottom": "20px", "marginTop": "60px", "display": "flex", "justifyContent": "center", "alignItems": "center"}),
        html.Div([
            dash.page_container
        ], style={'marginTop': "40px"}),
        dmc.Footer(
            height=60,
            fixed=True,
            children=[
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("AcademicBody", weight=500,
                                color="white"), span="auto"),
                        dmc.Col([
                            dmc.Group(
                                [
                                    html.A(DashIconify(icon="ion:logo-github", color="white", width=30,
                                                       rotate=1, flip="horizontal"), href="https://github.com/Westly93/Academic-Body"),
                                    html.A(DashIconify(icon="mdi:facebook",
                                                       color="white", width=30), href="https://github.com/Westly93/Academic-Body"),
                                    html.A(DashIconify(icon="fa-brands:twitter",
                                                       color="white", width=30), href="https://github.com/Westly93/Academic-Body")
                                ]
                            )
                        ], span="auto"),
                        dmc.Col([
                            dmc.Text("Copyright", weight=500,
                                color="white"),
                            DashIconify(icon="mdi:copyright",
                                        width=24, rotate=0, flip="vertical", color="white"),
                            dmc.Text(f"{current_year}", weight=500,
                                color="white")
                        ], style={"display": "flex"}, span="auto"),
                    ],
                    gutter="xl",
                    style={"width": "80%", "margin": "10px auto"}
                ),

            ],
            style={"backgroundColor": "#343a40", "marginTop": "120px"},
        )

    ],
)
# Calbacks


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)

import dash
from datetime import datetime
import pandas as pd
# import dash_auth
from dash import html, State, dcc, ALL
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from flask import Flask, request, redirect, session
from flask_login import login_user, LoginManager, UserMixin, logout_user, current_user
from dash.exceptions import PreventUpdate
from utils.login_handler import restricted_page

current_year = datetime.now().year


def get_icon(icon):
    return DashIconify(icon=icon, height=16)


MSU_LOGO = "/assets/images/msu-logo.png"
# Exposing the Flask Server to enable configuring it for logging in
server = Flask(__name__)

app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        # include google fonts
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;900&display=swap",
        dbc.themes.SPACELAB
    ],
)


""" @server.route('/all-stats', methods=['GET'])
def statistics_redirect():
    if not current_user.is_authenticated:
        return redirect('/login')


@server.route('/', methods=['GET'])
def home_redirect():
    if not current_user.is_authenticated:
        return redirect('/login')


@server.route('/graduants', methods=['GET'])
def graduants_redirect():
    if not current_user.is_authenticated:
        return redirect('/login')
    return redirect('/graduants') """


@server.route('/login', methods=['POST'])
def login_button_click():
    if request.form:
        username = request.form['username']
        password = request.form['password']
        if VALID_USERNAME_PASSWORD.get(username) is None:
            return """invalid username and/or password <a href='/login'>login here</a>"""
        if VALID_USERNAME_PASSWORD.get(username) == password:
            login_user(User(username))
            if 'url' in session:
                if session['url']:
                    url = session['url']
                    session['url'] = None
                    return redirect(url)  # redirect to target url
            return redirect('/')  # redirect to home
        return """invalid username and/or password <a href='/login'>login here</a>"""


guest_links = [page for page in dash.page_registry.values()
               if page['path'] != "/login"]
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=MSU_LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand(
                            "AcademicBoard", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(

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


# Keep this out of source code repository - save in a file or a database
#  passwords should be encrypted
VALID_USERNAME_PASSWORD = {"test": "test", "hello": "world"}


# Updating the Flask Server configuration with Secret Key to encrypt the user session cookie
server.config.update(SECRET_KEY="testing321#")

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


class User(UserMixin):
    # User data model. It has to have at least self.id as a minimum
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    """This function loads the user by user id. Typically this looks up the user from a user database.
    We won't be registering or looking up users in this example, since we'll just login using LDAP server.
    So we'll simply return a User object with the passed in username.
    """
    return User(username)


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
        dmc.Title(f"Academic Board Results Presentation",
                  order=2, style={"marginBottom": "20px", "marginTop": "60px", "display": "flex", "justifyContent": "center", "alignItems": "center"}),
        html.Div([
            dcc.Location(id="url"),
            html.Div(id="user-status-header"),
            dash.page_container
        ], style={'marginTop': "40px"}),
        html.Br(),
        html.Hr(),
        dmc.Footer(
            height=60,
            fixed=True,
            children=[
                dmc.Grid(
                    children=[
                        dmc.Col(dmc.Text("AcademicBoard", weight=500,
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
# login callbacks


@app.callback(
    Output("navbar-collapse", "children"),
    Output('url', 'pathname'),
    Input("url", "pathname"),
    Input({'index': ALL, 'type': 'redirect'}, 'n_intervals')
)
def update_authentication_status(path, n):
    # logout redirect
    if n:
        if not n[0]:
            return '', dash.no_update
        else:

            return '', '/login'

    # test if user is logged in
    if current_user.is_authenticated:
        if path == '/login':
            nav = dbc.Nav(
                [
                    dbc.NavLink(
                        [
                            html.Div(page["name"], className="ms-2"),
                        ],
                        href=page["path"],
                        active="exact",
                    )
                    for page in guest_links
                ],
                className="ms-auto",
                navbar=True,
            ),
            return nav, '/'
        guest_links = [page for page in dash.page_registry.values()
                       if page['path'] != "/login"]
        nav = dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in guest_links
            ],
            className="ms-auto",
            navbar=True,
        ),
        return nav, dash.no_update
    else:
        # if page is restricted, redirect to login and save path
        if path in restricted_page:
            session['url'] = path
            guest_links = [page for page in dash.page_registry.values()
                           if page['path'] == "/login"]
            nav = dbc.Nav(
                [
                    dbc.NavLink(
                        [
                            html.Div(page["name"], className="ms-2"),
                        ],
                        href=page["path"],
                        active="exact",
                    )
                    for page in guest_links
                ],
                className="ms-auto",
                navbar=True,
            ),
            return nav, '/login'

    # if path not login and logout display login link
    if current_user and path not in ['/login', '/logout']:
        guest_links = [page for page in dash.page_registry.values()
                       if page['path'] == "/login"]
        nav = dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in guest_links
            ],
            className="ms-auto",
            navbar=True,
        ),
        return nav, dash.no_update

    # if path login and logout hide links
    if path in ['/login', '/logout']:
        return '', dash.no_update

# navbar collapse callbacks


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

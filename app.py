import dash
from datetime import datetime
from os import path
import pandas as pd
# import dash_auth
from werkzeug.security import generate_password_hash, check_password_hash
from dash import html, State, dcc, ALL
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from flask import Flask, request, redirect, session
from flask_login import login_user, LoginManager, UserMixin, logout_user, current_user
from dash.exceptions import PreventUpdate
from utils.login_handler import restricted_page
from flaskapp.models import User, db
from flaskapp.config import Config

current_year = datetime.now().year


def get_icon(icon):
    return DashIconify(icon=icon, height=16)


MSU_LOGO = "/assets/images/msu-logo.png"
# Exposing the Flask Server to enable configuring it for logging in


def create_server(config_class=Config):
    server = Flask(__name__)
    # Updating the Flask Server configuration with Secret Key to encrypt the user session cookie
    server.config.from_object(Config)
    db.init_app(server)
    # server.config.update(SECRET_KEY="testing321#")

    # Login manager object will be used to login / logout users
    login_manager = LoginManager()
    login_manager.init_app(server)
    login_manager.login_view = "/login"
    with server.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return server


server = create_server()

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
        user = User.query.filter_by(email=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)  # redirect to target url
            return redirect('/')  # redirect to home

        return """invalid username and/or password <a href='/login'>login here</a>"""


@server.route('/signup', methods=['POST'])
def signup_button_click():
    if request.form:
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if email and password and confirm_password:
            user = User.query.filter_by(email=email).first()
            if user:
                return """Please this email is taken <a href='/signup'>Signup here</a>"""
            if password != confirm_password:
                return """Please Passwords do not match <a href='/signup'>Signup here</a>"""
            password = generate_password_hash(password, method='pbkdf2:sha256')
            user = User(
                email=email, password=password
            )
            db.session.add(user)
            db.session.commit()
            return redirect('/login')  # redirect to home
        return """Please Fill in the required fields <a href='/signup'>Signup here</a>"""


guest_links = [page for page in dash.page_registry.values()
               if page['path'] not in ["/login", '/signup', '/logout']]
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


def create_database(server):
    if not path.exists('database.db'):
        db.create_all(app=server)
        print('Created Database!')


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
        dmc.Footer(
            height=60,
            fixed=True,
            children=[
                dmc.Breadcrumbs(
                    separator="→",
                    children=[
                        html.P(id="faculty-output",
                               style={"marginTop": "20px"}),
                        html.P(id="programme-output",
                               style={"marginTop": "20px"})
                    ],
                    style={"color": "white", "display": "flex",
                           "justifyContent": "center", "alignItems": "center"}
                ),
                """ dmc.Grid(
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
                ), """

            ],
            style={"backgroundColor": "#343a40", "marginTop": "120px"},
        )

    ],
)
# Calbacks


@app.callback(
    Output("faculty-output", 'children'),
    Input("faculty_selection", "value")
)
def update_faculty_output(faculty):
    return dmc.Text(

        f"{faculty}",

        variant="gradient",
        gradient={"from": "red",
                  "to": "yellow", "deg": 45},
    ),


@app.callback(
    Output("programme-output", 'children'),
    Input("programme_selection", "value")
)
def update_programme_output(programme):
    return dmc.Text(

        f"{programme}",

        variant="gradient",
        gradient={"from": "red",
                  "to": "yellow", "deg": 45},
    ),
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
                       if page['path'] not in ["/login", "/signup", "/logout"]]
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
                           if page['path'] in ["/login", "/signup"]]
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

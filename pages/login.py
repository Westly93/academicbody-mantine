
import time
import dash
import dash_mantine_components as dmc
from dash import html, Output, Input, no_update, callback
from dash_iconify import DashIconify
dash.register_page(__name__)
layout = html.Form(
    style={"width": 400, "margin": "20px auto"},
    children=[dmc.LoadingOverlay(
        dmc.Paper(
            children=[
                dmc.Stack(
                    id="loading-form",
                    children=[
                        dmc.Image(style={"width": "300px"},
                                  withPlaceholder=True,
                                  placeholder=[dmc.Loader(
                                      color="gray", size="sm")],
                                  src="/assets/images/logo.png"),
                        dmc.TextInput(
                            type="text",
                            label="Username",
                            name="username",
                            id="uname-box",
                            placeholder="Your username",
                            icon=DashIconify(icon="radix-icons:person"),
                        ),
                        dmc.TextInput(
                            label="Password",
                            type="Password",
                            name="password",
                            id="pwd-box",
                            placeholder="Your password",
                            icon=DashIconify(icon="radix-icons:lock-closed"),
                        ),
                        dmc.Checkbox(
                            label="Remember me",
                            checked=True,
                        ),
                        dmc.Button(
                            "Login", n_clicks=0,
                            type="submit", id="login-button", variant="outline", fullWidth=True
                        ),

                    ],
                )
            ],
            shadow="xs",
            style={
                "padding": "20px"
            }
        )
    )], method='POST'
)


@callback(
    Output("loading-form", "children"),
    Input("load-button", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    time.sleep(2)
    return no_update

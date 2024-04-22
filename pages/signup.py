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
                    id="signup-form",
                    children=[
                        dmc.Image(style={"width": "300px"},
                                  withPlaceholder=True,
                                  placeholder=[dmc.Loader(
                                      color="gray", size="sm")],
                                  src="/assets/images/logo.png"),
                        dmc.TextInput(
                            type="text",
                            label="Email",
                            name="email",
                            id="email-box",
                            placeholder="Your Email",
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
                        dmc.TextInput(
                            label="Password",
                            type="Password",
                            name="confirm_password",
                            id="confirmpwd-box",
                            placeholder="confirm password",
                            icon=DashIconify(icon="radix-icons:lock-closed"),
                        ),
                        dmc.Button(
                            "Signup", n_clicks=0,
                            type="submit", id="signup-button", variant="outline", fullWidth=True
                        ),
                        html.Div(
                            [
                                dmc.Text(
                                    "Already Have an account? ", size="md"),
                                dmc.Anchor(
                                    "SignIn",
                                    href="/login",
                                    style={
                                        "marginLeft": "5px"
                                    }
                                )
                            ],
                            style={
                                "display": "flex",
                            }
                        )

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
    Output("signup-form", "children"),
    Input("signup-button", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    time.sleep(2)
    return no_update

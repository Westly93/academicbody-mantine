import dash
from dash import html, dcc
from flask_login import logout_user, current_user
import dash_mantine_components as dmc

dash.register_page(__name__)


def layout(**kwargs):
    if current_user.is_authenticated:
        logout_user()
    return dmc.Paper(
        children=[
            dmc.Text("You have been logged out - Please login",
                     color="red", weight=500, size="md"),
            html.Br(),
            dmc.Anchor(
                "Login",
                href="/login",
            )],
        shadow="xs",
        style={"width": "600px", "margin": "20px auto", "padding": "20px"}
    )

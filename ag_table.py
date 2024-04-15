import dash_ag_grid as dag
from dash import Dash, Input, Output, html, ctx, no_update, callback
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])


columnDefs = [{"field": i} for i in ["make", "model", "price"]]


rowData = [
    {"make": "Toyota", "model": "Celica", "price": 35000},
    {"make": "Ford", "model": "Mondeo", "price": 32000},
    {"make": "Porsche", "model": "Boxster", "price": 72000},
]

app.layout = html.Div(
    [
        dag.AgGrid(
            id="row-selection-popup-popup",
            rowData=rowData,
            columnDefs=columnDefs,
            columnSize="sizeToFit",
            dashGridOptions={"rowSelection": "single", "animateRows": False},
        ),
        dbc.Modal(
            [
                dbc.ModalHeader("More information about selected row"),
                dbc.ModalBody(id="row-selection-modal-content"),
                dbc.ModalFooter(dbc.Button(
                    "Close", id="row-selection-modal-close", className="ml-auto")),
            ],
            id="row-selection-modal",
        ),
    ]
)


@callback(
    Output("row-selection-modal", "is_open"),
    Output("row-selection-modal-content", "children"),
    Input("row-selection-popup-popup", "selectedRows"),
    Input("row-selection-modal-close", "n_clicks"),
)
def open_modal(selection, _):
    if ctx.triggered_id == "row-selection-modal-close":
        return False, no_update
    if selection:
        return True, "You selected " + ", ".join(
            [
                f"{s['make']} (model {s['model']} and price {s['price']})"
                for s in selection
            ]
        )

    return no_update, no_update


if __name__ == "__main__":
    app.run(debug=True)

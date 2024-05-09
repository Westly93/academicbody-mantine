import dash_ag_grid as dag
from dash import Dash, Input, Output, html, ctx, no_update, callback
import dash_mantine_components as dmc

app = Dash(__name__)

columnDefs = [{"field": i} for i in ["make", "model", "price"]]


rowData = [
    {"make": "Toyota", "model": "Celica", "price": 35000},
    {"make": "Ford", "model": "Mondeo", "price": 32000},
    {"make": "Porsche", "model": "Boxster", "price": 72000},
]
app.layout = html.Div(dmc.Accordion(
    children=[
        dmc.AccordionItem(
            [
                dmc.AccordionControl("Customization"),
                dmc.AccordionPanel(
                    dag.AgGrid(
                        id="row-selection-popup-popup",
                        rowData=rowData,
                        columnDefs=columnDefs,
                        columnSize="sizeToFit",
                        dashGridOptions={
                            "rowSelection": "single", "animateRows": False},
                    )
                ),
            ],
            value="customization",
        ),
    ],
    value=["flexibility", ],
    transitionDuration=1000
))


if __name__ == "__main__":
    app.run(debug=True)

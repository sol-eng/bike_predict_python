from shiny import *
from ipyshiny import output_widget, register_widget, reactive_read
from ipyleaflet import Map, basemaps, Circle
from ipywidgets import HTML
from htmltools import css
import numpy as np
import pins
import requests as req
import pandas as pd
from dotenv import load_dotenv
from plotnine import *

load_dotenv()

board = pins.board_rsconnect(server_url="https://colorado.rstudio.com/rsc")
df_stations = board.pin_read("alex.gold/bike_station_info")

# convert longitude for map projection
df_stations.loc[:, "lon"] = df_stations.loc[:, "lon"] + 360
df_stations["pred"] = np.random.randint(0, 30, size=df_stations.shape[0])

location_options = {
    str(df_stations["station_id"][l]): df_stations["name"][l] for l in df_stations.index
}


app_ui = ui.page_fluid(
    ui.div(
        ui.input_slider("zoom", "Map zoom level", value=14, min=1, max=20),
        style=css(
            display="flex", justify_content="center", align_items="center", gap="2rem"
        ),
    ),
    output_widget("map"),
    ui.div(
        ui.input_select("bike_station", "Select location", location_options),
        ui.output_text_verbatim("txt"),
        ui.output_plot("plot"),
    ),
)


def server(input, output, session):

    # Initialize and display when the session starts (1)
    map = Map(basemap=basemaps.Esri.WorldTopoMap, center=(38.9072, 282.9631), zoom=14)
    register_widget("map", map)
    map.layout.height = "400px"
    map.layout.width = "100%"

    def handle_click(**kwargs):
        coordinates = kwargs["coordinates"]
        print(coordinates)
        return coordinates

    for station_id, name, lat, lon, pred_num_bikes in df_stations.values:
        message = HTML(value=f"Predicated # of bikes at {name}: {pred_num_bikes}")
        circle = Circle(
            location=(lat, lon),
            radius=pred_num_bikes * 2,
            color="dodgerblue",
            fill_color="dodgerblue",
        )
        circle.on_click(handle_click)
        circle.popup = message
        map.add_layer(circle)

    # @reactive.Calc
    # def val_click():
    #     print(f'text {input.on_click()}')
    #     return input.on_click()

    @output
    @render.text
    def text():
        coord = input.on_click(handle_click)
        return f"{coord}"

    # When the slider changes, update the map's zoom attribute (2)
    @reactive.Effect
    def _():
        map.zoom = input.zoom()

    # When zooming directly on the map, update the slider's value (2 and 3)
    @reactive.Effect
    def _():
        ui.update_slider("zoom", value=reactive_read(map, "zoom"))

    @output()
    @render.plot(alt="line chart")
    def plot():
        r = req.get(
            "https://colorado.rstudio.com/rsc/bike_predict_api/pred",
            params={"station_id": input.bike_station()},
        )
        prediction = pd.DataFrame.from_dict(r.json())
        prediction.times = pd.to_datetime(prediction.times)
        fig = (
            ggplot(prediction)
            + aes(x="times", y="pred")
            + geom_line()  # line plot
            + scale_x_datetime(
                date_breaks="4 hours", date_labels="%I:%M %p", minor_breaks=4
            )
            + labs(x="time", y="# of predicted bikes in the next 24 hrs")
            + theme_light()
        )

        return fig


app = App(app_ui, server)

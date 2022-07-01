
from datetime import datetime
import calendar
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
from vetiver.server import predict, vetiver_endpoint

load_dotenv()

board = pins.board_rsconnect(server_url="https://colorado.rstudio.com/rsc")
df_stations = board.pin_read("alex.gold/bike_station_info")

# convert longitude for map projection
# df_stations.loc[:, "lon"] = df_stations.loc[:, "lon"] + 360
# df_stations["pred"] = np.random.randint(0, 30, size=df_stations.shape[0])

location_options = {
    str(df_stations["station_id"][l]): df_stations["name"][l] for l in df_stations.index
}


now = datetime.now()
hour, month, day_of_week = now.hour, now.month, calendar.day_name[datetime.today().weekday()]
df_stations['hour'] = hour
df_stations['month'] = month
df_stations[f'{day_of_week}'] = 1
dict_day_of_week = {
    "Friday": 0,
    "Monday": 0,
    "Saturday": 0,
    "Sunday": 0,
    "Thursday": 0,
    "Tuesday": 0,
    "Wednesday": 0
}
dict_day_of_week.pop(day_of_week)

for key, value in dict_day_of_week.items():
    df_stations[key] = value

df_to_predict = df_stations.loc[:,~df_stations.columns.isin(['station_id'])]

print('done with df processing')

endpoint = vetiver_endpoint("https://colorado.rstudio.com/rsc/bike-predict-python-api/predict/")
df_to_predict.loc[:, 'pred'] = predict(endpoint, df_to_predict)
df_to_map = df_to_predict.loc[:,['name', 'lat', 'lon', 'pred']]
print(df_to_map.head())

app_ui = ui.page_fluid(
    ui.div(
        ui.input_slider("zoom", "Map zoom level", value=14, min=1, max=20),
        style=css(
            display="flex", justify_content="center", align_items="center", gap="2rem"
        ),
    ),
    output_widget("map"),
    ui.div(
        # ui.input_select("bike_station", "Select location by clicking on a circle on the map", location_options),
        ui.output_plot("plot"),
    ),
    ui.row(
        ui.output_text_verbatim("text"),
    )
)


def server(input, output, session):

    # Initialize and display when the session starts (1)
    map = Map(basemap=basemaps.Esri.WorldTopoMap, center=(38.9072, 282.9631), zoom=14)
    register_widget("map", map)
    map.layout.height = "400px"
    map.layout.width = "100%"

    station = reactive.Value()
    df_to_map.loc[:, "lon"] = df_to_map.loc[:, "lon"] + 360

    def handle_click(**kwargs):
        coords = kwargs['coordinates']
        station.set(coords)

    for name, lat, lon, pred_num_bikes in df_to_map.values:
        message = HTML(value=f"Predicted # of bikes at {name}: {int(pred_num_bikes)}")
        circle = Circle(
            location=(lat, lon),
            radius=int(pred_num_bikes) * 2,
            color="dodgerblue",
            fill_color="dodgerblue",
        )
        circle.on_click(handle_click)
        circle.popup = message
        map.add_layer(circle)

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
        hrs = pd.date_range(now, periods=24, freq="H")
        df_to_plot: pd.DataFrame = pd.DataFrame(
            index=range(24),
            columns=['station_id', 'lat', 'lon', 'datetime', 'hour', 'month', 'day_of_week']
        )
        df_to_plot.loc[:, "lat"] = station()[0]
        df_to_plot.loc[:, "lon"] = station()[1] - 360
        df_to_plot.loc[:, "datetime"] = hrs
        df_to_plot.loc[:, "day_of_week"] = hrs.day_name()
        df_to_plot.loc[:, "hour"] = hrs.hour
        df_to_plot.loc[:, "month"] = hrs.month

        day_of_week: dict = {
            "Friday": 0,
            "Monday": 0,
            "Saturday": 0,
            "Sunday": 0,
            "Thursday": 0,
            "Tuesday": 0,
            "Wednesday": 0
        }
        df_to_plot = df_to_plot.join(pd.get_dummies(df_to_plot.day_of_week))
        days: set = set(df_to_plot.loc[:, "day_of_week"].values)
        remaining_days: dict = {k: v for k, v in day_of_week.items() if k not in days}
        for key, value in remaining_days.items():
            df_to_plot[key] = value
        df_to_pred2 = df_to_plot.loc[:,~df_to_plot.columns.isin(['station_id', 'datetime', 'day_of_week'])]
        df_to_plot['pred'] = predict(endpoint, df_to_pred2)
        df_to_plot_f = df_to_plot.loc[:,['datetime', 'pred']]

        fig = (
                ggplot(df_to_plot_f)
                + aes(x='datetime', y='pred')
                + geom_line() # line plot
                + scale_x_datetime(date_breaks = "4 hours", date_labels = "%I:%M %p")
                + labs(x='time', y='# of predicted bikes in the next 24 hrs') 
                + theme_light()
            )

        return fig

    @output()
    @render.text()
    def text():
        return f'Coordinates are: {station()}'

app = App(app_ui, server)

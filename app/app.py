from datetime import datetime
import calendar
from shiny import *
from shinywidgets import output_widget, register_widget, reactive_read
from ipyleaflet import Map, basemaps, Circle, MarkerCluster
from ipywidgets import HTML
from htmltools import css
import pins
import pandas as pd
from dotenv import load_dotenv
from plotnine import *
from vetiver.server import predict, vetiver_endpoint

load_dotenv()

now = datetime.now()


def add_time_to_df(df: pd.DataFrame) -> pd.DataFrame:
    df_time = df.copy()
    hour, month, day_of_week = (
        now.hour,
        now.month,
        calendar.day_name[datetime.today().weekday()],
    )
    df_time["hour"] = hour
    df_time["month"] = month
    df_time[f"{day_of_week}"] = 1
    dict_day_of_week = {
        "Friday": 0,
        "Monday": 0,
        "Saturday": 0,
        "Sunday": 0,
        "Thursday": 0,
        "Tuesday": 0,
        "Wednesday": 0,
    }
    dict_day_of_week.pop(day_of_week)
    for key, value in dict_day_of_week.items():
        df_time[key] = value
    return df_time


# def create_df_station_to_predict(df: pd.DataFrame) -> pd.DataFrame:
#     df_to_pred = df.loc[:, ~df.columns.isin(["name", "lat", "lon"])].copy()
#     df_to_pred.rename(columns={"station_id": "id"}, inplace=True)
#     return df_to_pred


def add_live_feed(df_json: pd.DataFrame, df_add_column: pd.DataFrame) -> pd.DataFrame:
    df_add_column["num_bikes_available"] = df_json["num_bikes_available"]
    return df_add_column


def add_coordinates_to_df(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()
    df_copy["coords"] = df_copy[["lat", "lon"]].values.tolist()
    return df_copy


def process_dataframe_for_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """Process dataframe so it can be mapped"""
    df_copy = add_coordinates_to_df(df)
    df_to_map = df_copy.loc[:, ["name", "lat", "lon", "num_bikes_available", "coords"]]
    return df_to_map


def create_coords_station_dict(df: pd.DataFrame) -> dict:
    """Create a dictionary with coordinates as keys and station id as values"""
    df_copy = add_coordinates_to_df(df)
    coords_station: dict = {
        tuple(coords): (str(id), name) for coords, id, name in df_copy[["coords", "station_id", "name"]].values
    }
    return coords_station


board = pins.board_rsconnect(server_url="https://colorado.rstudio.com/rsc")
df_stations = board.pin_read("sam.edwardes/bike-predict-r-station-info-pin")
endpoint = vetiver_endpoint(
    "https://colorado.rstudio.com/rsc/new-bikeshare-model/predict/"
)
df_time = add_time_to_df(df_stations)
df_json = pd.read_json("https://gbfs.capitalbikeshare.com/gbfs/en/station_status.json")['data']['stations']
df_json_normal = pd.json_normalize(df_json)
# df_pred_all_stations = create_df_station_to_predict(df_time)
df_time = add_live_feed(df_json_normal, df_time)

app_ui = ui.page_fluid(
    ui.row(
        ui.panel_well("Where can I get a bike? Capitol Bikeshare Python"),
        ui.help_text("Bike Station Map"),
    ),
    output_widget("map"),
    ui.div(
        ui.output_text_verbatim("text"),
    ),
    ui.div(
        ui.output_plot("plot"),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):

    map = Map(
        basemap=basemaps.Esri.WorldTopoMap,
        center=(38.888553, -77.032429),
        zoom=14,
        scroll_wheel_zoom=True,
    )
    map.layout.height = "500px"
    map.layout.width = "100%"
    register_widget("map", map)

    station = reactive.Value(False)
    df_to_map = process_dataframe_for_mapping(df_time)
    coords_station: dict = create_coords_station_dict(df_stations)

    def create_dataframe_to_plot() -> pd.DataFrame:
        hrs = pd.date_range(now, periods=24, freq="H")
        df_to_plot: pd.DataFrame = pd.DataFrame(
            index=range(24), columns=["id", "datetime", "hour", "month", "day_of_week"]
        )
        df_to_plot["datetime"] = hrs
        df_to_plot["day_of_week"] = hrs.day_name()
        df_to_plot["hour"] = hrs.hour
        df_to_plot["month"] = hrs.month
        if station():
            df_to_plot["id"] = int(coords_station[tuple(station())][0])
        day_of_week: dict = {
            "Friday": 0,
            "Monday": 0,
            "Saturday": 0,
            "Sunday": 0,
            "Thursday": 0,
            "Tuesday": 0,
            "Wednesday": 0,
        }
        df_to_plot = df_to_plot.join(pd.get_dummies(df_to_plot.day_of_week))
        days: set = set(df_to_plot.loc[:, "day_of_week"].values)
        remaining_days: dict = {k: v for k, v in day_of_week.items() if k not in days}
        for key, value in remaining_days.items():
            df_to_plot[key] = value
        df_to_plot = df_to_plot.loc[:, ~df_to_plot.columns.isin(["day_of_week"])].copy()
        return df_to_plot

    def handle_click(**kwargs):
        coords = kwargs["coordinates"]
        station.set(coords)


    circle_markers: list = []
    for name, lat, lon, pred_num_bikes, coords in df_to_map.values:
        message = HTML(value=f"Right now there are {int(pred_num_bikes)} bikes at: {name}")
        circle = Circle(
            location=(lat, lon),
            radius=int(pred_num_bikes),
            color="darkblue",
            fill_color="darkblue",
            fill_opacity=0.4,
            opacity=0.4,
            name=name,
        )
        circle.on_click(handle_click)
        circle.popup = message
        circle_markers.append(circle)

    marker_cluster = MarkerCluster(markers=circle_markers)
    map.add_layer(marker_cluster)

    
    @output()
    @render.text()
    def text():
        return "" if station() else "Please click on a circle marker to see the predicted # of bikes over the next 24 hours"

    @output()
    @render.plot(alt="line chart")
    def plot():
        df_to_plot = create_dataframe_to_plot()
        df_to_pred = df_to_plot.loc[:, ~df_to_plot.columns.isin(["datetime"])]
        if station():
            df_to_plot["pred"] = predict(endpoint, df_to_pred)
            name = coords_station[tuple(station())][1]
            fig = (
                ggplot(df_to_plot)
                + aes(x="datetime", y="pred")
                + geom_line(color='dimgray')
                + scale_x_datetime(date_breaks="3 hours", date_labels="%I:%M %p")
                + labs(x="time", y="# of bikes predicted")
                + ggtitle(f"Predicted # of bikes at {name} over the next 24 hrs")
                + theme_light()
                + theme(text = element_text(size = 15))
            )
            return fig
        pass
    


app = App(app_ui, server)

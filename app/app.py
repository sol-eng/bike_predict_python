from datetime import datetime
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
from scipy import spatial

load_dotenv()


def add_current_num_bikes(
    df_json: pd.DataFrame, df_add_column: pd.DataFrame
) -> pd.DataFrame:
    """Add the current # of bikes from live feed."""
    df_add_column["num_bikes_available"] = df_json["num_bikes_available"]
    df_add_column["num_bikes_available"].fillna(0, inplace=True)
    return df_add_column


def add_coordinates_to_df(df: pd.DataFrame) -> pd.DataFrame:
    """Add the combined coordinates column to dataframe."""
    df_copy = df.copy()
    df_copy["coords"] = df_copy[["lat", "lon"]].values.tolist()
    return df_copy


def process_dataframe_for_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """Process dataframe so it can be mapped."""
    df_copy = add_coordinates_to_df(df)
    df_to_map = df_copy.loc[:, ["name", "lat",
                                "lon", "num_bikes_available", "coords"]]
    return df_to_map


def create_coords_station_dict(df: pd.DataFrame) -> dict:
    """Create a dictionary with coordinates as keys and station id as values to reverse loop up ids."""
    df_copy = add_coordinates_to_df(df)
    coords_station: dict = {
        tuple(coords): (str(id), name)
        for coords, id, name in df_copy[["coords", "station_id", "name"]].values
    }
    return coords_station


def create_24_hrs_df_to_plot() -> pd.DataFrame:
    """Create a dataframe 24 hours from the current time for plotting predicted number of bikes."""
    now = datetime.now()
    hrs = pd.date_range(now, periods=24, freq="H")
    df_to_plot: pd.DataFrame = pd.DataFrame(
        index=range(24), columns=["id", "datetime", "hour", "month", "day_of_week"]
    )
    df_to_plot["datetime"] = hrs
    df_to_plot["day_of_week"] = hrs.day_name()
    df_to_plot["hour"] = hrs.hour
    df_to_plot["month"] = hrs.month
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
    remaining_days: dict = {k: v for k,
                            v in day_of_week.items() if k not in days}
    for key, value in remaining_days.items():
        df_to_plot[key] = value
    df_to_plot = df_to_plot.loc[:, ~
                                df_to_plot.columns.isin(["day_of_week"])].copy()
    return df_to_plot


#####################################
# Loading data from an existing R pin
#####################################

df_to_plot = create_24_hrs_df_to_plot()
board = pins.board_rsconnect(server_url="https://colorado.rstudio.com/rsc")
df_stations = board.pin_read("sam.edwardes/bike-predict-r-station-info-pin")
endpoint = vetiver_endpoint(
    "https://colorado.rstudio.com/rsc/new-bikeshare-model/predict/"
)

df_json = pd.read_json("https://gbfs.capitalbikeshare.com/gbfs/en/station_status.json")[
    "data"
]["stations"]
df_json_normal = pd.json_normalize(df_json)
df_stations = add_current_num_bikes(df_json_normal, df_stations)

###########################
# UI components
###########################
app_ui = ui.page_fluid(
    ui.row(
        ui.panel_well("Where can I get a bike? -- Capital Bikeshare Python"),
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

###########################
# Server components
###########################


def server(input: Inputs, output: Outputs, session: Session):
    def get_id_name(df_map: pd.DataFrame) -> tuple:
        '''Look up station id and name based on the coordinates from the click event'''
        if tuple(station()) in coords_station:
            id = coords_station[tuple(station())][0]
            name = coords_station[tuple(station())][1]
        else:
            coords_tree = spatial.KDTree(df_map["coords"].values.tolist())
            closest_idx = coords_tree.query(station())[1]
            coords: tuple = tuple(df_map.loc[closest_idx, "coords"])
            id = coords_station[coords][0]
            name = coords_station[coords][1]
        return (id, name)

    def add_id(df: pd.DataFrame, df_map: pd.DataFrame) -> pd.DataFrame:
        '''Add the id column to dataframe from looked up id'''
        if station():
            df["id"] = get_id_name(df_map)[0]
        return df

    def handle_click(**kwargs):
        '''A callback function to assign the coordinate values to a reactive Value station'''
        coords = kwargs["coordinates"]
        station.set(coords)

    station = reactive.Value(False)
    map = Map(
        basemap=basemaps.Esri.WorldTopoMap,
        center=(38.888553, -77.032429),
        zoom=14,
        scroll_wheel_zoom=True,
    )
    map.layout.height = "500px"
    map.layout.width = "100%"
    register_widget("map", map)

    df_to_map = process_dataframe_for_mapping(df_stations)
    coords_station: dict = create_coords_station_dict(df_stations)

    COLOR = "darkblue"
    circle_markers: list = []
    for name, lat, lon, pred_num_bikes, coords in df_to_map.values:
        message = HTML(
            value=f"Right now there are {int(pred_num_bikes)} bikes at: {name}"
        )
        circle = Circle(
            location=(lat, lon),
            radius=int(pred_num_bikes) * 2,
            color=COLOR,
            fill_color=COLOR,
            fill_opacity=0.4,
            opacity=0.4,
            name=name,
        )
        circle.on_click(handle_click)
        circle.popup = message
        circle_markers.append(circle)

    marker_cluster = MarkerCluster(markers=circle_markers)
    map.add_layer(marker_cluster)

###########################
# Reactive outputs
###########################

    @output()
    @render.text()
    def text():
        return (
            ""
            if station()
            else "Please click on a circle marker to see the predicted # of bikes over the next 24 hours"
        )

    @output()
    @render.plot(alt="line chart")
    def plot():
        df_to_plot_id = add_id(df_to_plot, df_to_map)
        df_to_pred = df_to_plot_id.loc[:, ~
                                       df_to_plot_id.columns.isin(["datetime"])]
        if station():
            df_to_plot_id["pred"] = predict(endpoint, df_to_pred)
            name = get_id_name(df_to_map)[1]
            fig = (
                ggplot(df_to_plot_id)
                + aes(x="datetime", y="pred")
                + geom_line(color="dimgray")
                + scale_x_datetime(date_breaks="3 hours",
                                   date_labels="%I:%M %p")
                + labs(x="time", y="# of bikes predicted")
                + ggtitle(f"Predicted # of bikes at {name} over the next 24 hrs")
                + theme_light()
                + theme(text=element_text(size=15))
            )
            return fig
        pass


app = App(app_ui, server)

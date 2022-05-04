from shiny import *
import pins
import requests as req
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter


board = pins.board_rsconnect(server_url="https://colorado.rstudio.com/rsc")
df_stations = board.pin_read("alex.gold/bike_station_info")

location_options = {
    str(df_stations["station_id"][l]):df_stations["name"][l] for l in df_stations.index
    }

app_ui = ui.page_fluid(
    ui.input_select("bike_station", "Select input", location_options),
    ui.output_text_verbatim("txt"),
    ui.output_plot("plot"),    
)

def server(input: Inputs, output: Outputs, session: Session):
    @output()
    @render_text()
    def txt():
        return f'bike_station: "{location_options[input.bike_station()]}"'

    @output()
    @render_plot(alt="A histogram")
    def plot():
        r = req.get(
        "https://colorado.rstudio.com/rsc/bike_predict_api/pred",
        params={"station_id": input.bike_station()},
        )
        prediction = pd.DataFrame.from_dict(r.json())
        fig, ax = plt.subplots()
        plt.plot(prediction["times"], prediction["pred"])
        plt.title("Bike Availability")
        plt.xlabel("Time")
        plt.ylabel("# of bikes");
        return fig



app = App(app_ui, server, debug=True)
import vetiver
import pins


b = pins.board_rsconnect(server_url='https://colorado.rstudio.com/rsc', allow_pickle_read=True)
v = vetiver.vetiver_pin_read(b, 'gagan/bikeshare-rf-2306', version = '58019')

vetiver_api = vetiver.VetiverAPI(v)
api = vetiver_api.app

from vetiver import VetiverModel
import vetiver
import pins


b = pins.board_connect(server_url='https://colorado.posit.co/rsc', allow_pickle_read=True)
v = VetiverModel.from_pin(b, 'sam.edwardes/bikeshare-rf-python', version = '75565')

vetiver_api = vetiver.VetiverAPI(v)
api = vetiver_api.app

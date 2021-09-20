from opentrons import protocol_api, types

#Metadata
metadata = {
    'protocolName': 'Move Tips',
    'author': 'J. Wang',
    'description': 'Move sterile tips from middle to the front',
    'apiLevel': '2.8'
}
tip_rack_slot = 6
pipette_tip_200 = 'opentrons_96_filtertiprack_200ul'
start_columns = ["A5", "A6", "A7", "A8"]
end_columns = ["A1", "A2", "A3", "A4"]

def run(protocol: protocol_api.ProtocolContext):
	tip_rack = [protocol.load_labware(pipette_tip_200, tip_rack_slot)]
	#pipettes
	left_300_pipette = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks = tip_rack)
	for i in range(4):
    		left_300_pipette.pick_up_tip(tip_rack[0][start_columns[i]]) 
    		left_300_pipette.drop_tip(tip_rack[0][end_columns[i]])
   

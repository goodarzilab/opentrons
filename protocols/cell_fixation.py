from opentrons import protocol_api, types
import sys
sys.path.append("/root/utils")
from common_methods import load_tips, discard_tips, eliminate_droplets, mixing

#Metadata
metadata = {
    'protocolName': 'Cell Fixation',
    'author': 'J. Wang',
    'description': 'Protocol for Cell Fixation',
    'apiLevel': '2.8'
}

#Test Mode
test_mode = True
#Continuous Mode
cont_mode = False
#Number of Sample Columns
num_columns = 12
#Number of Plates to Run
num_plates = 1

#Labware Types
type_of_sample_plate = 'nest_96_wellplate_100ul_pcr_full_skirt' #Slot 2: Sample Plate
type_reservoir_plate = 'nest_12_reservoir_15ml' #Slot5: 12 Trough Reservoir
pipette_tip_200 = 'opentrons_96_filtertiprack_200ul'

#Well Numbering
well_list = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']
#Plate slots
plate_slot_order = [1, 2, 4, 7, 10] #Based on number of plates to use per run, place plates in the slot number according to the order of this list.
#Tip slots
tip_slot_order = [5, 6, 8, 9, 11]

def run(protocol: protocol_api.ProtocolContext):
    tr_200=[]
    plate_list = []
    test_tip_rack = None
    if test_mode: #If test_mode just use one box and reuse tips
        tr_200.append(protocol.load_labware(pipette_tip_200, tip_slot_order[0]))
        test_tip_rack = tr_200[0]
    else:
        for i in range(num_plates):
            tr_200.append(protocol.load_labware(pipette_tip_200, tip_slot_order[i])) 
            
    for i in range(num_plates):        
        plate_list.append(protocol.load_labware(type_of_sample_plate, plate_slot_order[i]))
    left_300_pipette = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks = tr_200)
    fixation_trough = protocol.load_labware(type_reservoir_plate, '3') #Fixation Solution
    
    def transfer_fix(amount):
        for i in range(num_plates):
            sample_plate = plate_list[i]
            for j in range(num_columns):
                sample_well = sample_plate[well_list[j]]
                load_tips(left_300_pipette, num_tips=8, test_mode=test_mode, test_tip_rack=test_tip_rack)
                left_300_pipette.aspirate(amount, fixation_trough.wells()[trough_num])
                left_300_pipette.dispense(amount, sample_well)	
                mixing(left_300_pipette, amount=70, rep=10, well=sample_well, aspirate_speed=150, dispense_speed=400)
                eliminate_droplets(left_300_pipette, loc=sample_well.top(), protocol=protocol)
                discard_tips(left_300_pipette, test_mode=test_mode)
                
    #Experiment States
    trough_num = 0
    #Actual Run
    if cont_mode:
        while trough_num < 12:
            protocol.comment("Transfer and mix fixation solution")
            protocol.comment(" ")
            transfer_fix(amount=25)
            protocol.pause('Switch plates') #Switch out plates and then press resume.
            protocol.comment(" ")
            trough_num += 1          
    else:
        protocol.comment("Transfer and mix fixation solution")
        protocol.comment(" ")
        transfer_fix(amount=25)


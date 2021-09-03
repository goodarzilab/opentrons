from opentrons import protocol_api, types
import sys
sys.path.append("/root/utils")
from common_methods import load_tips, discard_tips, eliminate_droplets, mixing

#Metadata
metadata = {
    'protocolName': 'Cell Fixation',
    'author': 'J. Wang',
    'description': 'Protocol for Cell Resuspension',
    'apiLevel': '2.8'
}

#User Parameters: ONLY MAKE EDITS HERE
parameters = {"test_mode" : False,
              "num_columns" : 1, #Number of columns per plate with cells
              "num_plates" : 1, #Number of plates used
              "transfer_amount" : 100, #Liquid amount to resuspend
              "mix_amount" : 85, #amount to pipette during mixing in ul
              "mix_rep" : 10, #number of mixing steps
              "mix_aspirate_speed" : 50,
              "mix_dispense_speed" : 450
             }

#Labware Parameters
lab_params = {"type_of_sample_plate" : "nest_96_wellplate_100ul_pcr_full_skirt",
              "plate_slot_order" : [1, 2, 4, 7, 10], #Based on number of plates to use per run, place plates in the slot number according to the order of this list.
              "type_reservoir_plate" : "nest_12_reservoir_15ml",
              "reservoir_slot" : 3, 
              "pipette_tip_200" : "opentrons_96_filtertiprack_200ul",
              "pipette_type" : "p300_multi_gen2",
              "tip_slot_order" : [5, 6, 8, 9, 11], #Based on number of plates to use per run, place tips in the slot number according to the order of this list.
              "well_list" : ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12'],
             }
    
def run(protocol: protocol_api.ProtocolContext):
    #Load user parameters
    test_mode, num_columns, num_plates = parameters["test_mode"], parameters["num_columns"], parameters["num_plates"]
    transfer_amount, mix_amount, mix_rep = parameters["transfer_amount"], parameters["mix_amount"], parameters["mix_rep"]
    mix_aspirate_speed, mix_dispense_speed = parameters["mix_aspirate_speed"], parameters["mix_dispense_speed"]
    
    #Load labware parameters
    type_of_sample_plate, plate_slot_order = lab_params["type_of_sample_plate"], lab_params["plate_slot_order"]
    type_reservoir_plate, reservoir_slot = lab_params["type_reservoir_plate"], lab_params["reservoir_slot"]
    pipette_tip_200, pipette_type = lab_params["pipette_tip_200"], lab_params["pipette_type"]
    well_list, tip_slot_order = lab_params["well_list"],  lab_params["tip_slot_order"]
    
    #Load equipment
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
    left_300_pipette = protocol.load_instrument(pipette_type, 'right', tip_racks = tr_200)
    fixation_trough = protocol.load_labware(type_reservoir_plate, reservoir_slot).wells()[0] #Fixation Solution in leftmost trough at slot3
    
    #Fixation Function
    def transfer_fix(transfer_amount, mix_amount, mix_rep, mix_aspirate_speed, mix_dispense_speed):
        for i in range(num_plates):
            sample_plate = plate_list[i]
            for j in range(num_columns):
                sample_well = sample_plate[well_list[j]]
                load_tips(left_300_pipette, num_tips=8, test_mode=test_mode, test_tip_rack=test_tip_rack)
                left_300_pipette.aspirate(transfer_amount, fixation_trough)
                left_300_pipette.dispense(transfer_amount, sample_well)
                mixing(left_300_pipette, amount=mix_amount, rep=mix_rep, well=sample_well, aspirate_speed=mix_aspirate_speed, dispense_speed=mix_dispense_speed)
                eliminate_droplets(left_300_pipette, loc=sample_well.top(), protocol=protocol)
                discard_tips(left_300_pipette, test_mode=test_mode)
                
    protocol.comment("Transfer and mix fixation solution")
    protocol.comment(" ")
    transfer_fix(transfer_amount=transfer_amount, mix_amount=mix_amount, mix_rep=mix_rep, mix_aspirate_speed=mix_aspirate_speed, mix_dispense_speed=mix_dispense_speed)

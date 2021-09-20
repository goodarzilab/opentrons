from opentrons import protocol_api, types
import sys
sys.path.append("/root/utils")
from common_methods import load_tips, discard_tips, eliminate_droplets, mixing

#Metadata
metadata = {
    'protocolName': 'Cell Resuspension',
    'author': 'J. Wang',
    'description': 'Protocol for Cell Resuspension',
    'apiLevel': '2.8'
}

#User Parameters: ONLY MAKE EDITS HERE
parameters = {"test_mode" : False,
              "num_columns" : 12, #Number of columns per plate with cells
              "num_plates" : 4, #Number of plates used
              "transfer_amount" : 50, #Liquid amount to resuspend
              "mix_amount" : 30, #amount to pipette during mixing in ul
              "mix_rep" : 5, #number of mixing steps
              "mix_aspirate_speed" : 900,
              "mix_dispense_speed" : 900
             }

#Labware Parameters
lab_params = {"type_of_sample_plate" : "corning_96_wellplate_330ul",
              "plate_slot_order" : [1, 2, 4, 5, 7, 8, 10, 11], #Based on number of plates to use per run, place plates in the slot number according to the order of this list.
              "type_reservoir_plate" : "nest_12_reservoir_15ml",
              "reservoir_slot" : 3, 
              "pipette_tip_200" : "opentrons_96_filtertiprack_200ul",
              "pipette_type" : "p300_multi_gen2",
              "tip_slot" : 6, #Based on number of plates to use per run, place tips in the slot number according to the order of this list.
              "well_list" : ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12'],
              "trough_dict" : {0:11, 1:10, 2:9, 3:8, 4:7, 5:6, 6:5, 7:4}
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
    well_list, trough_dict, tip_slot = lab_params["well_list"], lab_params["trough_dict"], lab_params["tip_slot"]
    
    #Load equipment
    tr_200=[protocol.load_labware(pipette_tip_200, tip_slot)]
    test_tip_rack = None
    if test_mode: #If test_mode just use one box and reuse tips
        test_tip_rack = tr_200[0]
    plate_list = []      
    for i in range(num_plates):        
        plate_list.append(protocol.load_labware(type_of_sample_plate, plate_slot_order[i]))
    left_300_pipette = protocol.load_instrument(pipette_type, 'right', tip_racks = tr_200)
    fixation_trough = protocol.load_labware(type_reservoir_plate, reservoir_slot).wells() #Fixation Solution in leftmost trough at slot3
    
    #Fixation Function
    def transfer_fix(transfer_amount, mix_amount, mix_rep, mix_aspirate_speed, mix_dispense_speed):
        for i in range(num_plates):
            sample_plate = plate_list[i]
            trough_well = fixation_trough[trough_dict[i]]
            load_tips(left_300_pipette, num_tips=8, test_mode=test_mode, test_tip_rack=test_tip_rack)
            for j in range(num_columns):
                sample_well = sample_plate[well_list[j]]
                #sample_well = sample_plate["A8"]
                #left_300_pipette.pick_up_tip(tr_200[0]["A2"])
                left_300_pipette.aspirate(transfer_amount, trough_well)
                left_300_pipette.dispense(transfer_amount, sample_well)
                mixing(left_300_pipette, amount=mix_amount, rep=mix_rep, well=sample_well, aspirate_speed=mix_aspirate_speed, dispense_speed=mix_dispense_speed, height=1)
                eliminate_droplets(left_300_pipette, loc=sample_well.top(), protocol=protocol)
            discard_tips(left_300_pipette, test_mode=test_mode)
                
    protocol.comment("Transfer and resuspend")
    protocol.comment(" ")
    transfer_fix(transfer_amount=transfer_amount, mix_amount=mix_amount, mix_rep=mix_rep, mix_aspirate_speed=mix_aspirate_speed, mix_dispense_speed=mix_dispense_speed)

from opentrons import protocol_api, types

#Metadata
metadata = {
    'protocolName': 'Quick-RNA MagBead',
    'author': 'J. Wang',
    'description': 'RNA Purification for Zymo Quick-RNA MagBead Protocol',
    'apiLevel': '2.8'
}

#Test Mode
test_mode = True
#Continuous Mode
cont_mode = True
#Number of sample Columns
num_column = 1


#Labware Types
type_of_sample_plate = 'nest_96_wellplate_100ul_pcr_full_skirt' #Slot 2: Sample Plate
type_reservoir_plate = 'nest_12_reservoir_15ml' #Slot5: 12 Trough Reservoir
pipette_tip_200 = 'opentrons_96_filtertiprack_200ul'

#Well Numbering
well_list = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']


def run(protocol: protocol_api.ProtocolContext):
    #Load Labware
    tr_200=[]
    if test_mode: #If test_mode just use one box and reuse tips
        tr_200.append(protocol.load_labware(pipette_tip_200, 3))
    else:
        tr_200.append(protocol.load_labware(pipette_tip_200, 3))
    
    left_300_pipette = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks = tr_200)
    
    sample_plate = protocol.load_labware(type_of_sample_plate, '2') #Samples
    fixation_trough = protocol.load_labware(type_of_reservoir_plate, '5') #Fixation Solution
    
    #Experiment States
    num_transfers = 0
    trough_num = 0
    
    #Basic Methods
    def load_tips():
        if test_mode:
            if tr_200[0].next_tip(num_tips=8):
                left_300_pipette.pick_up_tip()
            else:
                left_300_pipette.reset_tipracks() #Reset tiprack[0] to keep using.
                left_300_pipette.pick_up_tip()
        else:
            left_300_pipette.pick_up_tip()
    
    #To prevent unncessary wastes during testing we write a discard tip function
    def discard_tips():
        if test_mode:
            left_300_pipette.return_tip()
        else:
            left_300_pipette.drop_tip()
    
    def mixing(amount, rep, well_num, aspirate_speed=150, dispense_speed=300): #Default for robot is 150 and 300
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        loc1 = sample_plate[well_list[well_num]].bottom().move(types.Point(x=1, y =0, z=.6))
        loc2 = sample_plate[well_list[well_num]].bottom().move(types.Point(x=1, y =0, z=3.6))
        left_300_pipette.aspirate(20, loc1)
        for i in range(rep):
            left_300_pipette.aspirate(amount, loc1)
            left_300_pipette.dispense(amount, loc2)
        left_300_pipette.dispense(20, loc2)
        left_300_pipette.move_to(sample_plate[well_list[well_num]].top())
        protocol.delay(seconds=1)
        left_300_pipette.blow_out(sample_plate[well_list[well_num]].top())
        
        
    def transfer_fix(amount):
        global num_transfers
        for i in range(num_col):
            load_tips()
            left_300_pipette.aspirate(amount, fixation_trough.wells()[trough_num])
            left_300_pipette.dispense(amount, sample_plate[well_list[i]])
            mixing(50, 10, i, 150, 400)
            discard_tips()
            num_transfers += 1
    
    if cont_mode:
        while True:
            protocol.comment("Transfer and mix fixation solution")
            protocol.comment(" ")
            transfer_fix(25)
            protocol.pause('Switch plates') #Switch out plates and then press resume.
            protocol.comment(" ")
    else:
        protocol.comment("Transfer and mix fixation solution")
        protocol.comment(" ")
        transfer_fix(25)


            

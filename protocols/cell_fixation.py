from opentrons import protocol_api, types

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
cont_mode = True
#Number of Sample Columns
num_column = 1
#Number of Plates to Run
num_plates = 1

#Labware Types
type_of_sample_plate = 'nest_96_wellplate_100ul_pcr_full_skirt' #Slot 2: Sample Plate
type_reservoir_plate = 'nest_12_reservoir_15ml' #Slot5: 12 Trough Reservoir
pipette_tip_200 = 'opentrons_96_filtertiprack_200ul'

#Well Numbering
well_list = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']
#Plate slots
plate_slot = [1, 4, 7, 10] #Based on number of plates to use per run, place plates in the slot number according to the order of this list.
#Tip slots
tip_slots = [2, 3, 5, 6]

def run(protocol: protocol_api.ProtocolContext):
    #Load Labware
    tr_200=[]
    plate_list = []
    if test_mode: #If test_mode just use one box and reuse tips
        tr_200.append(protocol.load_labware(pipette_tip_200, 2))
    else:
        for i in range(num_plates)
            tr_200.append(protocol.load_labware(pipette_tip_200, tip_slots[i])) 
            plate_list.append(protocol.load_labware(type_of_sample_plate, plate_slot[i]))

    left_300_pipette = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks = tr_200)
    fixation_trough = protocol.load_labware(type_of_reservoir_plate, '8') #Fixation Solution
    
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
            
    def eliminate_droplets(loc):
        left_300_pipette.move_to(loc)
        protocol.delay(seconds=1)
        left_300_pipette.blow_out(loc)
                 
    def mixing(amount, rep, well, aspirate_speed=150, dispense_speed=300): #Default for robot is 150 and 300
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        loc1 = well.bottom().move(types.Point(x=1, y =0, z=.6))
        loc2 = well.bottom().move(types.Point(x=1, y =0, z=3.6))
        for i in range(rep):
            left_300_pipette.transfer(amount, loc1, loc2)     
        eliminate_droplets(well.top())

    def transfer_fix(amount):
        nonlocal num_transfers
        for i in range(num_plates):
            sample_plate = plate_list[i]
            for j in range(num_col):
                sample_well = sample_plate[well_list[j]]
                load_tips()
                left_300_pipette.transfer(amount, fixation_trough.wells()[trough_num], sample_well)
                mixing(70, 10, sample_well, 150, 400)
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
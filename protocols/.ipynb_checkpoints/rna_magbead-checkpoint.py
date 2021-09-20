from opentrons import protocol_api, types

# metadata
metadata = {
    'protocol name': 'Quick-RNA MagBead',
    'author': 'J. Wang',
    'description': 'RNA Purification for Zymo Quick-RNA MagBead Protocol',
    'apiLevel': '2.7'
}

#User Edits Here. Edit these number to change position, amount, liquid class, etc. They will be split up by steps.
#Testing mode
test_mode = True
#Sample Columns
plate_column = 1 #Specifies how many columns to use (max 6): Named column 1, 3, 5, 7, 9, 11. Corresponds with how many samples: 8-16-24-32-40-48

#Plates
type_of_reaction_plate = "nest_96_wellplate_2ml_deep" #Slot 1: Deep well plate sits on magnetic module (must have 200 microliters of sample already pipette in)
type_of_elution_plate = 'nest_96_wellplate_100ul_pcr_full_skirt' #Slot 2: Final Elution Plate. Original was 200 microlioter
type_of_reservoir_plate_1 = "nest_96_wellplate_2ml_deep" #Slot 5: Ethanol Deep Well Plate. Zymo's protocol name was wrong: 'nest_96_deepwell_2ml'
type_of_reservoir_plate_2 = 'nest_12_reservoir_15ml' #Slot 8: 12 Trough Reservoir
type_of_liquid_waste_plate = 'nest_1_reservoir_195ml' #Slot 9: Liquid Waste

#pipette tips
pipette_tip_200 = 'opentrons_96_filtertiprack_200ul'

#Magnetic module engage height
magheight = 13.7
magwell_height = 7

#Well numbering
well_list = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']

#Sample numbering
sample_column_list = ['A1', 'A3', 'A5', 'A7', 'A9', 'A11']

ethanol_list_1 = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6']
ethanol_list_2 = ['A7', 'A8', 'A9', 'A10', 'A11', 'A12']

def run(protocol: protocol_api.ProtocolContext):
    #assigning pipette box
    tr_200=[]
    if test_mode: #If test_mode just use one box and reuse tips
        tr_200.append(protocol.load_labware(pipette_tip_200, 3))
    else:
        tr_200.append(protocol.load_labware(pipette_tip_200, 3))
        tr_200.append(protocol.load_labware(pipette_tip_200, 4))
        tr_200.append(protocol.load_labware(pipette_tip_200, 6))
        tr_200.append(protocol.load_labware(pipette_tip_200, 7))
        tr_200.append(protocol.load_labware(pipette_tip_200, 10))
        tr_200.append(protocol.load_labware(pipette_tip_200, 11))

    #pipettes
    left_300_pipette = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks = tr_200)
    #loading magnetic module
    magnetic_module = protocol.load_module('magnetic module gen2', '1') #Note we have gen2 module
    magnetic_module.disengage()

    #plate loading and column number
    reaction_plate = magnetic_module.load_labware(type_of_reaction_plate)
    elution_plate = protocol.load_labware(type_of_elution_plate, '2')
    reservoir_plate_1 = protocol.load_labware(type_of_reservoir_plate_1, '5') #Ethanol
    reservoir_plate_2 = protocol.load_labware(type_of_reservoir_plate_2, '8') #12 Trough Reservoir
    liquid_waste_plate = protocol.load_labware(type_of_liquid_waste_plate, '9') #Liquid Waste Container
    liquid_waste = liquid_waste_plate.wells()[0]

    #12 (reservoir_plate_2) well assignments (slot 8)
    DNA_RNA_Lysis_Buffer_well = reservoir_plate_2.wells()[0]
    magbead_DNA_RNA_Wash_1_1_well = reservoir_plate_2.wells()[2]
    magbead_DNA_RNA_Wash_1_2_well = reservoir_plate_2.wells()[3]
    magbead_DNA_RNA_Wash_2_1_well = reservoir_plate_2.wells()[5]
    magbead_DNA_RNA_Wash_2_2_well = reservoir_plate_2.wells()[6]
    DNase_RNase_free_water_well = reservoir_plate_2.wells()[8]
    magbinding_bead_well = reservoir_plate_2.wells()[10]

    #Basic Methods

    def mixing(amount, rep, well_num, aspirate_speed=150, dispense_speed=300): #Default for robot is 150 and 300
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        loc1 = reaction_plate[sample_column_list[well_num]].bottom().move(types.Point(x=1, y =0, z=.6))
        loc2 = reaction_plate[sample_column_list[well_num]].bottom().move(types.Point(x=1, y =0, z=5.5))
        left_300_pipette.aspirate(20, loc1)
        for x in range(rep):
            left_300_pipette.aspirate(amount, loc1)
            left_300_pipette.dispense(amount, loc2)
        left_300_pipette.dispense(20, loc2)
        left_300_pipette.flow_rate.aspirate = 50
        left_300_pipette.flow_rate.dispense = 100

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
            left_300_pipette.move_to(liquid_waste.top(-2))
            protocol.delay(seconds=3)
            left_300_pipette.blow_out(liquid_waste.top(-2))
            left_300_pipette.return_tip()
        else:
            left_300_pipette.drop_tip()

    #Step 1
    def DNA_RNA_lysis_buffer_transfer(transfer_amount, mix_num, mix_amount, aspirate_speed, dispense_speed):
        global well_list
        global plate_column
        global sample_column_list
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        for x in range(plate_column):
            load_tips()
            if x == 0:
                left_300_pipette.mix(mix_num, mix_amount, DNA_RNA_Lysis_Buffer_well)

            left_300_pipette.aspirate(transfer_amount, DNA_RNA_Lysis_Buffer_well)
            left_300_pipette.dispense(transfer_amount, reaction_plate[sample_column_list[x]])
            mixing(180, 5, x)
            left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
            protocol.delay(seconds=3)
            left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))
            discard_tips()

    protocol.comment(" ")
    protocol.comment("DNA and RNA Lysis Buffer Transfer")
    protocol.comment(" ")
    #DNA_RNA_lysis_buffer_tranfer_amount = 200, DNA_RNA_lysis_buffer_mix_num = 3, DNA_RNA_lysis_buffer_mix_amount = 50 #uL,
    #DNA_RNA_lysis_buffer_aspirate_speed = 5, DNA_RNA_lysis_buffer_dispense_speed = 5
    DNA_RNA_lysis_buffer_transfer(200, 3, 100, 50, 100)

    #Step 2
    def ethanol_transfer(transfer_amount, aspirate_speed, dispense_speed):
        global well_list
        global plate_column
        global sample_column_list
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        for x in range(plate_column):
            load_tips()
            left_300_pipette.aspirate(transfer_amount/2, reservoir_plate_1[ethanol_list_1[x]])
            left_300_pipette.dispense(transfer_amount/2, reaction_plate[sample_column_list[x]])
            left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
            protocol.delay(seconds=3)
            left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))
            left_300_pipette.aspirate(transfer_amount/2, reservoir_plate_1[ethanol_list_1[x]])
            left_300_pipette.dispense(transfer_amount/2, reaction_plate[sample_column_list[x]])
            mixing(150, 5, x)
            left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
            protocol.delay(seconds=3)
            left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))
            discard_tips()
            # left_300_pipette.drop_tip()

    protocol.comment("Ethanol Transfer")
    protocol.comment(" ")
    ##Ethanol Transfer Step: ethanol_transfer_amount = 400 #uL, ethanol_aspirate_speed = 5, ethanol_dispense_speed = 5
    ethanol_transfer(400, 50, 100)

    #Step 3
    def magbinding_bead_transfer(transfer_amount, mix_num, mix_amount, aspirate_speed, dispense_speed):
        global well_list
        global plate_column
        global sample_column_list

        for x in range(plate_column):
            load_tips()
            left_300_pipette.flow_rate.aspirate = 100
            left_300_pipette.flow_rate.dispense = 200
            left_300_pipette.mix(mix_num, mix_amount, magbinding_bead_well)
            left_300_pipette.flow_rate.aspirate = aspirate_speed
            left_300_pipette.flow_rate.dispense = dispense_speed
            left_300_pipette.aspirate(transfer_amount, magbinding_bead_well)
            left_300_pipette.dispense(transfer_amount, reaction_plate[sample_column_list[x]])
            mixing(180, 5, x)
            left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
            protocol.delay(seconds=3)
            left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))
            discard_tips()

    protocol.comment(" ")
    protocol.comment("Magnetic Binding Bead Transfer")
    protocol.comment(" ")
    #magbinding_bead_tranfer_amount = 30, magbinding_bead_mix_num = 5, magbinding_bead_mix_amount = 40
    #magbinding_bead_aspirate_speed = 3, magbinding_bead_dispense_speed = 5
    magbinding_bead_transfer(30, 5, 40, 50, 100)

    magnetic_module.engage(height=magheight)
    protocol.delay(minutes=2)

    #Step 4
    def supernatant_removal_1(transfer_amount, aspirate_speed, dispense_speed):
        global well_list
        global plate_column
        global sample_column_list
        global tip_box
        global tip_well_num
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        for x in range(plate_column):
            load_tips()
            for i in range(5):
                left_300_pipette.aspirate(transfer_amount/5, reaction_plate[sample_column_list[x]].bottom().move(types.Point(x=-1, y=0, z=magwell_height))) #Aspirate 175 microliter per time.
                left_300_pipette.dispense(transfer_amount/5 + 50, liquid_waste.top(-2)) #Extra 50 dispense to prevent dripping.
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(liquid_waste.top(-2))
            discard_tips()

    protocol.comment(" ")
    protocol.comment("Supernatant Removal")
    protocol.comment(" ")
    supernatant_removal_1(875, 50, 100)

    magnetic_module.disengage()

    #Step 5
    def wash_1_transfer(transfer_amount, mix_num, mix_amount, aspirate_speed, dispense_speed):
        global well_list
        global plate_column
        global sample_column_list
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        for x in range(plate_column):
            if x < 3: #For first three columns
                load_tips()
                left_300_pipette.aspirate(200, magbead_DNA_RNA_Wash_1_1_well)
                left_300_pipette.dispense(200, reaction_plate[sample_column_list[x]].top(-5))
                left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))

                left_300_pipette.aspirate(150, magbead_DNA_RNA_Wash_1_1_well)
                left_300_pipette.dispense(150, reaction_plate[sample_column_list[x]].top(-5))
                left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))

                left_300_pipette.aspirate(150, magbead_DNA_RNA_Wash_1_1_well)
                left_300_pipette.dispense(150, reaction_plate[sample_column_list[x]])
                mixing(180, 5, x)
                left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))
                discard_tips()
            elif x > 2: #For last three columns
                load_tips()
                left_300_pipette.aspirate(200, magbead_DNA_RNA_Wash_1_2_well)
                left_300_pipette.dispense(200, reaction_plate[sample_column_list[x]].top(-5))
                left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))

                left_300_pipette.aspirate(150, magbead_DNA_RNA_Wash_1_2_well)
                left_300_pipette.dispense(150, reaction_plate[sample_column_list[x]].top(-5))
                left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))

                left_300_pipette.aspirate(150, magbead_DNA_RNA_Wash_1_2_well)
                left_300_pipette.dispense(150, reaction_plate[sample_column_list[x]].top(-5))
                mixing(180, 5, x)
                left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))
                discard_tips()

    protocol.comment(" ")
    protocol.comment("Wash 1")
    protocol.comment(" ")
    wash_1_transfer(500, 5, 180, 50, 100)
    magnetic_module.engage(height = magheight)
    protocol.delay(minutes = 5)

    #Step 6
    def supernatant_removal_2(transfer_amount, aspirate_speed, dispense_speed):
        global well_list
        global plate_column
        global sample_column_list
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        for x in range(plate_column):
            load_tips()
            for i in range(3):
                left_300_pipette.aspirate(transfer_amount/3, reaction_plate[sample_column_list[x]].bottom().move(types.Point(x=-1, y=0, z=magwell_height)))
                left_300_pipette.dispense(transfer_amount/3 + 50, liquid_waste.top(-2))
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(liquid_waste.top(-2))
            discard_tips()

    protocol.comment(" ")
    protocol.comment("Supernatant Removal")
    protocol.comment(" ")
    supernatant_removal_2(540, 50, 100) #40 microliters more than actually there.
    magnetic_module.disengage()

    #Step 7
    def wash_2_transfer(transfer_amount, mix_num, mix_amount, aspirate_speed, dispense_speed):
        global well_list
        global plate_column
        global sample_column_list
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        for x in range(plate_column):
            if x < 3: #First three columns
                load_tips()
                left_300_pipette.aspirate(200, magbead_DNA_RNA_Wash_2_1_well)
                left_300_pipette.dispense(200, reaction_plate[sample_column_list[x]].top(-5))
                left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5)) #Should dispense at top and eliminate return step, reuse for second transfer
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))

                left_300_pipette.aspirate(150, magbead_DNA_RNA_Wash_2_1_well)
                left_300_pipette.dispense(150, reaction_plate[sample_column_list[x]].top(-5))
                left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5)) #Should dispense at top and eliminate return step, reuse for second transfer
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))

                left_300_pipette.aspirate(150, magbead_DNA_RNA_Wash_2_1_well)
                left_300_pipette.dispense(150, reaction_plate[sample_column_list[x]])
                mixing(180, 5, x)
                left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5)) #Should dispense at top and eliminate return step, reuse for second transfer
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))
                discard_tips()
            elif x > 2: #Last three columns
                load_tips()
                left_300_pipette.aspirate(200, magbead_DNA_RNA_Wash_2_2_well)
                left_300_pipette.dispense(200, reaction_plate[sample_column_list[x]].top(-5))
                left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))

                left_300_pipette.aspirate(150, magbead_DNA_RNA_Wash_2_2_well)
                left_300_pipette.dispense(150, reaction_plate[sample_column_list[x]].top(-5))
                left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))

                left_300_pipette.aspirate(150, magbead_DNA_RNA_Wash_2_2_well)
                left_300_pipette.dispense(150, reaction_plate[sample_column_list[x]])
                mixing(180, 5, x)
                left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
                protocol.delay(seconds=3)
                left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))
                discard_tips()

    protocol.comment(" ")
    protocol.comment("Wash 2")
    protocol.comment(" ")
    wash_2_transfer(500, 5, 180, 50, 100)
    magnetic_module.engage(height = magheight)
    protocol.delay(minutes = 5)

    #Step 8
    protocol.comment(" ")
    protocol.comment("Supernatant Removal")
    protocol.comment(" ")
    supernatant_removal_2(540, 50, 100)
    magnetic_module.disengage()

    #Step 9
    def ethanol_wash_1_transfer(transfer_amount, aspirate_speed, dispense_speed):
        global well_list
        global plate_column
        global sample_column_list
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        for x in range(plate_column):
            load_tips()
            left_300_pipette.aspirate(200, reservoir_plate_1[ethanol_list_2[x]])
            left_300_pipette.dispense(200, reaction_plate[sample_column_list[x]].top(-5))
            left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
            protocol.delay(seconds=3)
            left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))

            left_300_pipette.aspirate(150, reservoir_plate_1[ethanol_list_2[x]])
            left_300_pipette.dispense(150, reaction_plate[sample_column_list[x]].top(-5))
            left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
            protocol.delay(seconds=3)
            left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))

            left_300_pipette.aspirate(150, reservoir_plate_1[ethanol_list_2[x]])
            left_300_pipette.blow_out(reaction_plate[sample_column_list[x]])

            mixing(180, 5, x)
            left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
            protocol.delay(seconds=3)
            left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))
            discard_tips()

    protocol.comment(" ")
    protocol.comment("Ethanol Transfer")
    protocol.comment(" ")
    ethanol_wash_1_transfer(500, 50, 100)
    magnetic_module.engage(height=magheight)
    protocol.delay(minutes = 3)

    #Step 10
    protocol.comment(" ")
    protocol.comment("Supernatant Removal")
    protocol.comment(" ")
    supernatant_removal_2(540, 50, 100)
    magnetic_module.disengage()

    #Step 11
    def ethanol_wash_2_transfer(transfer_amount, aspirate_speed, dispense_speed):
        global well_list
        global plate_column
        global sample_column_list
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        for x in range(plate_column):
            load_tips()
            left_300_pipette.aspirate(200, reservoir_plate_1[ethanol_list_2[x]])
            left_300_pipette.dispense(200, reaction_plate[sample_column_list[x]])
            left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
            protocol.delay(seconds=3)
            left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))

            left_300_pipette.aspirate(150, reservoir_plate_1[ethanol_list_2[x]])
            left_300_pipette.dispense(150, reaction_plate[sample_column_list[x]])
            left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
            protocol.delay(seconds=3)
            left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))

            left_300_pipette.aspirate(150, reservoir_plate_1[ethanol_list_2[x]])
            left_300_pipette.dispense(150, reaction_plate[sample_column_list[x]])
            mixing(180, 5, x)
            left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
            protocol.delay(seconds=3)
            left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))
            discard_tips()

    protocol.comment(" ")
    protocol.comment("Ethanol Transfer")
    protocol.comment(" ")
    ethanol_wash_2_transfer(500, 50, 100)
    magnetic_module.engage(height=magheight)
    protocol.delay(minutes = 3)

    #Step 12

    protocol.comment(" ")
    protocol.comment("Supernatant Transfer")
    protocol.comment(" ")
    supernatant_removal_2(540, 50, 100)

    print("Drying stage: 8 min.")
    protocol.delay(minutes=8) #This is the drying stage
    magnetic_module.disengage()

    #Step 13
    def elution(transfer_amount, mix_num, mix_amount, aspirate_speed, dispense_speed):
        global well_list
        global plate_column
        global sample_column_list
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        for x in range(plate_column):
            load_tips()
            left_300_pipette.aspirate(transfer_amount,DNase_RNase_free_water_well)
            left_300_pipette.dispense(transfer_amount, reaction_plate[sample_column_list[x]].bottom().move(types.Point(x=-1, y=0, z=0.5))) #Here it mag is disengaged should be okay.
            mixing(mix_amount, mix_num, x)
            left_300_pipette.move_to(reaction_plate[sample_column_list[x]].top(-5))
            protocol.delay(seconds=3)
            left_300_pipette.blow_out(reaction_plate[sample_column_list[x]].top(-5))
            discard_tips()

    protocol.comment(" ")
    protocol.comment("Elution Transfer")
    protocol.comment(" ")
    #Elution_transfer_amount = 50, Elution_mix_amount = 30, elution_mix_num=5
    elution(50, 5, 30, 50, 100)

    magnetic_module.engage(height = magheight)
    protocol.delay(minutes = 3)
    #Step 14
    def elution_transfer(transfer_amount,aspirate_speed, dispense_speed):
        global well_list
        global plate_column
        global sample_column_list
        left_300_pipette.flow_rate.aspirate = aspirate_speed
        left_300_pipette.flow_rate.dispense = dispense_speed
        for x in range(plate_column):
            load_tips()
            left_300_pipette.aspirate(transfer_amount,reaction_plate[sample_column_list[x]].bottom().move(types.Point(x=-1, y=0, z=magwell_height)))
            left_300_pipette.dispense(transfer_amount, elution_plate[sample_column_list[x]].bottom().move(types.Point(x=0, y=0, z= 2)))
            protocol.delay(seconds=3)
            left_300_pipette.move_to(elution_plate[sample_column_list[x]].top(-5))
            left_300_pipette.blow_out(elution_plate[sample_column_list[x]].top(-5))
            discard_tips()

    protocol.comment(" ")
    protocol.comment("Transfer to product plate.")
    protocol.comment(" ")
    elution_transfer(50, 50, 100)
    magnetic_module.disengage()
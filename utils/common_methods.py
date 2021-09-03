from opentrons import types

def load_tips(pipette, num_tips, test_mode=False, test_tip_rack=None):
    """Function to load tips. Test mode will conserve tips and reuse tips from same tip rack
    pipette -- opentrons pipette object. 
    num_tips -- Number of tips to load at once (int, 1 for single or 8 for multi-channel)
    test_mode -- Denote whether to load tips in test mode (Default False)
    tip_rack - Specifiy which tip rack to use for test mode (Default None)
    """
    if test_mode:
        assert test_tip_rack, "No tip rack specificed for test mode loading"
        if test_tip_rack.next_tip(num_tips=num_tips):
            pipette.pick_up_tip()
        else:
            pipette.reset_tipracks() #Reset tiprack to keep using the same tip box.
            pipette.pick_up_tip()
    else:
        pipette.pick_up_tip()
        
def discard_tips(pipette, test_mode=False):
    """Function to discard tips. Test mode will conserve tips and return to original tip rack"""
    if test_mode:
        pipette.return_tip()
    else:
        pipette.drop_tip()


def eliminate_droplets(pipette, loc, protocol):
    """Blow out extra droplets to prevent dripping at LOC"""
    pipette.move_to(loc)
    protocol.delay(seconds=1)
    pipette.blow_out(loc)

    
def mixing(pipette, amount, rep, well, aspirate_speed=150, dispense_speed=300): #Default for robot is 150 and 300
    """Method to mix liquid in WELL by AMOUNT"""
    pipette.flow_rate.aspirate = aspirate_speed
    pipette.flow_rate.dispense = dispense_speed
    loc1 = well.bottom().move(types.Point(x=1, y =0, z=.6))
    loc2 = well.bottom().move(types.Point(x=1, y =0, z=2.6))
    for i in range(rep):
        pipette.aspirate(amount, loc1)
        pipette.dispense(amount,loc2)
    pipette.flow_rate.aspirate = 150
    pipette.flow_rate.dispense = 300

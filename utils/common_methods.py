
def load_tips(pipette, num_tips, test_mode=False, tip_rack=None):
    """Function to load tips. Test mode will conserve tips and reuse tips from same tip rack
    pipette -- opentrons pipette object. 
    num_tips -- Number of tips to load at once (int, 1 for single or 8 for multi-channel)
    test_mode -- Denote whether to load tips in test mode (Default False)
    tip_rack - Specifiy which tip rack to use for test mode (Default None)
    """
    if test_mode:
        assert tip_rack, "No tip rack specificed for test mode loading"
        if tip_rack.next_tip(num_tips=num_tips):
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
        

        

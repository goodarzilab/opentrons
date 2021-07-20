
"""Function to load tips. 
PIPETTE - opentrons pipette object. 
NUM_TIPS - int. Number of tips to load at once (1 for single or 8 for multi)
TEST_MODE - boolean value. Used to denote whether to load tips in test mode. Default False
TIP_RACK - Specifiy which tip rack to use for test mode. Default None
"""
def load_tips(pipette, num_tips, test_mode=False, tip_rack=None):
    if test_mode:
        assert tip_rack, "No tip rack specificed for loading"
        if tip_rack.next_tip(num_tips=num_tips):
            pipette.pick_up_tip()
        else:
            pipette.reset_tipracks() #Reset tiprack[0] to keep using.
            pipette.pick_up_tip()
    else:
        pipette.pick_up_tip()
        
        
"""Function to discard tips."""
def discard_tips(pipette, test_mode=False):
    if test_mode:
        pipette.return_tip()
    else:
        pipette.drop_tip()
        

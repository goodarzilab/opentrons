
metadata = {
    "apiLevel": "2.6"
}

import json
import os
from pathlib import Path

# Modify HIGH_CURRENT for A and Z motors to 0.5
from opentrons.config.robot_configs import HIGH_CURRENT
NEW_HIGH_CURRENT = 0.5

# Modify default currents for A and Z motors to 0.5
from opentrons.config.robot_configs import DEFAULT_CURRENT
NEW_DEFAULT_CURRENT = 0.5

robot_settings_path = Path("/data/robot_settings.json")

def run(protocol):
    json_contents = json.loads(robot_settings_path.read_text())
    # Modify HIGH_CURRENT for A and Z motors to 0.5
    new_high = {k: v for k, v in HIGH_CURRENT.items()}
    new_high['A'] = NEW_HIGH_CURRENT
    new_high['Z'] = NEW_HIGH_CURRENT
    json_contents["high_current"] = new_high

    # Modify default currents for A and Z motors to 0.5
    new_default = {k: v for k, v in DEFAULT_CURRENT.items()}
    new_default['A'] = NEW_DEFAULT_CURRENT
    new_default['Z'] = NEW_DEFAULT_CURRENT
    json_contents["default_current"] = new_default

    robot_settings_path.write_text(json.dumps(json_contents, indent=4))
    os.sync()
    protocol.comment("Done.")

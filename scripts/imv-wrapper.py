#!/usr/bin/env python3

# Start imv pointing to the media folder where the images have been downloaded
# to and set the duration per image based on the snap configuration.

import os
import subprocess

snap = os.getenv('SNAP')
snap_user_common = os.getenv('SNAP_USER_COMMON')
MEDIA_DIR = f'{snap_user_common}/media'
IMV_CMD = f'{snap}/user/bin/imv'

duration = int(subprocess.check_output(['snapctl', 'get', 'imv-duration']))
if not duration:
    duration = 10 # default for safety

subprocess.run([IMV_CMD, '-f', f'-t {duration}', MEDIA_DIR])

#!/usr/bin/env python3

# Start imv pointing to the media folder where the images have been downloaded
# to and set the duration per image based on the snap configuration.

import os
import subprocess

snap = os.getenv('SNAP')
snap_user_common = os.getenv('SNAP_USER_COMMON')
media_dir = f'{snap_user_common}/media'
imv_cmd = f'{snap}/usr/bin/imv'
duration = subprocess.check_output(['snapctl', 'get', 'imv-duration'], encoding='UTF-8').rstrip()
if not duration:
    duration = 10 # default for safety

subprocess.run([imv_cmd, '-f', f'-t {duration}', media_dir])

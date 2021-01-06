#!/usr/bin/env python3

# Downloads all images from the specified Backblaze B2 bucket to a local
# MEDIA_DIR folder where they can be found by imv. Snap runs scripts as
# root so the media folder belongs to root. It does nothing if the B2
# authorization keys and bucket aren’t configured. Only images newer
# than the remove-after-days snap config value will be downloaded. Since
# local files are removed, older images will automatically dissapear.

import glob
import os
import subprocess
import sys
import time
from b2sdk.v1 import B2Api
from b2sdk.v1 import InMemoryAccountInfo
from b2sdk.v1 import NewerFileSyncMode
from b2sdk.v1 import ScanPoliciesManager
from b2sdk.v1 import SyncReport
from b2sdk.v1 import Synchronizer
from b2sdk.v1 import parse_sync_folder

SNAP_NAME = os.getenv('SNAP_NAME')
snap_user_common = os.getenv('SNAP_USER_COMMON')
MEDIA_DIR = f'{snap_user_common}/media'

def get_snap_config(var):
    """Get a value from the snap’s configuration"""
    val = subprocess.check_output(['snapctl', 'get', var], encoding='UTF-8').rstrip()
    if not val:
        sys.exit(f'Config {val} is empty, set with "snap set {SNAP_NAME} {var}"')
    return val

def sync():
    """Synchronize files modified in last x days from the bucket to the media folder"""
    b2 = B2Api(InMemoryAccountInfo())
    app_key_id = get_snap_config('b2-application-key-id')
    app_key = get_snap_config('b2-application-key')
    b2.authorize_account('production', app_key_id, app_key)
    exclude_before_timestamp = int(time.time()) - (int(get_snap_config('remove-after-days')) * 86400)
    policies_manager = ScanPoliciesManager(
            exclude_file_regexes=("index.html",),
            exclude_modified_before=exclude_before_timestamp * 1000 # in ms
        )
    synchronizer = Synchronizer(
            max_workers=5,
            newer_file_mode=NewerFileSyncMode.SKIP,
            policies_manager=policies_manager
        )
    bucket_uri = 'b2://' + get_snap_config('b2-bucket')
    source = parse_sync_folder(bucket_uri, b2)
    destination = parse_sync_folder(MEDIA_DIR, b2)
    if not os.path.isdir(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)
    with SyncReport(sys.stdout, False) as reporter:
        synchronizer.sync_folders(
            source_folder=source,
            dest_folder=destination,
            now_millis=time.time() * 1000, # in ms
            reporter=reporter
        )

def remove_old_media():
    """Delete all media files older than x days"""
    max_lifetime = int(get_snap_config('remove-after-days')) * 86400 # in seconds
    for image in glob.glob(MEDIA_DIR + '/*'):
        if image.endswith('html'):
            continue
        modified_at = os.path.getmtime(image)
        if time.time() - modified_at > max_lifetime:
            os.remove(image)

def restart_imv():
    """Restart imv so it sees the newly downloaded images"""
    subprocess.run(['snapctl', 'restart', f'{SNAP_NAME}.imv'])

sync()
remove_old_media()
restart_imv()

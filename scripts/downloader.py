#!/usr/bin/env python3

# Downloads all images from the specified Backblaze B2 bucket to a local
# MEDIA_DIR folder where they can be found by imv. Snap runs scripts as
# root so the media folder belongs to root. It does nothing if the B2
# authorization keys and bucket aren’t configured.

import glob
import os
import subprocess
import sys
import time
from b2sdk.v1 import B2Api
from b2sdk.v1 import InMemoryAccountInfo
from b2sdk.v1 import ScanPoliciesManager
from b2sdk.v1 import SyncReport
from b2sdk.v1 import Synchronizer
from b2sdk.v1 import parse_sync_folder

snap_user_common = os.getenv('SNAP_USER_COMMON')
MEDIA_DIR = f'{snap_user_common}/media'

def get_snap_config(var):
    """Get a value from the snap’s configuration"""
    val = subprocess.check_output(['snapctl', 'get', var], encoding='UTF-8').rstrip()
    if not val:
        sys.exit(f'Config {val} is empty, set with "snap set omabox {var}"')
    return val

def empty_media_dir():
    """Remove all non HTML files in the media directory"""
    if not os.path.isdir(MEDIA_DIR):
        sys.exit(f'Media directory "{MEDIA_DIR}" not found')
    for image in glob.glob(MEDIA_DIR + '/*'):
        if not image.endswith('html'):
            os.remove(image)

def download():
    """Download all from the bucket to the media folder"""
    b2 = B2Api(InMemoryAccountInfo())
    app_key_id = get_snap_config('b2-application-key-id')
    app_key = get_snap_config('b2-application-key')
    b2.authorize_account('production', app_key_id, app_key)
    bucket_uri = 'b2://' + get_snap_config('b2-bucket')
    source = parse_sync_folder(bucket_uri, b2)
    destination = parse_sync_folder(MEDIA_DIR, b2)
    synchronizer = Synchronizer(max_workers=10, policies_manager=ScanPoliciesManager())
    with SyncReport(sys.stdout, False) as reporter:
        synchronizer.sync_folders(
            source_folder=source,
            dest_folder=destination,
            now_millis=int(round(time.time() * 1000)),
            reporter=reporter
        )

empty_media_dir()
download()

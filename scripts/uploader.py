#!/usr/bin/env python3

# The upload URL in the webUI is only valid for 24 hours so we use this script
# to copy the read-only index.html from the snap, replace the auth token and
# upload URL placheolders and upload the modified file to the the B2 bucket.
# This script needs to run at least once every 24 hours.

# TODO optimization idea: extract the depeated bucket to bucket_id network requests

import os
import shutil
import subprocess
import sys
from b2sdk.v1 import InMemoryAccountInfo
from b2sdk.v1 import B2Api

snap = os.getenv('SNAP')
snap_user_common = os.getenv('SNAP_USER_COMMON')

MEDIA_DIR = f'{snap_user_common}/media'
TEMPLATE_FILE = f'{snap}/uploader/index.html'
INDEX_FILE = f'{MEDIA_DIR}/index.html'

def get_snap_config(var):
    """Get a value from the snap’s configuration"""
    val = subprocess.check_output(['snapctl', 'get', var], encoding='UTF-8').rstrip()
    if not val:
        sys.exit(f'Config {val} is empty, set with "snap set omabox {var}"')
    return val

def copy_template():
    """Copy tempate HTML from snap to writable directory"""
    if not os.path.isfile(TEMPLATE_FILE):
        sys.exit(f'Template file "{TEMPLATE_FILE}" not found')
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)
    shutil.copyfile(TEMPLATE_FILE, INDEX_FILE)

def tokens():
    """Request new authorization token and upload URL from Backblaze B2"""
    name = get_snap_config('b2-bucket')
    bucket = B2.get_bucket_by_name(name)
    return B2.session.get_upload_url(bucket.get_id())

def replace_keys():
    """Replace the placeholder authorization token and upload URL in the index file"""
    with open(INDEX_FILE, 'r+') as f:
        data = f.read()
        f.seek(0)
        t = tokens()
        replaced = data.replace('CHANGEME_AUTHORIZATION_TOKEN', t['authorizationToken'])
        replaced = replaced.replace('CHANGEME_UPLOAD_URL', t['uploadUrl'])
        f.write(replaced)
        f.truncate()

def upload():
    """Upload the modified file to the bucket"""
    name = get_snap_config('b2-bucket')
    bucket = B2.get_bucket_by_name(name)
    bucket.upload_local_file(INDEX_FILE, 'index.html')

B2 = B2Api(InMemoryAccountInfo())
app_key_id = get_snap_config('b2-application-key-id')
app_key = get_snap_config('b2-application-key')
B2.authorize_account('production', app_key_id, app_key)

copy_template()
replace_keys()
upload()

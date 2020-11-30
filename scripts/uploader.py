#!/usr/bin/env python3

# The upload URL in the webUI is only valid for 24 hours so we use this
# script to copy the read-only index.html from the snap, replace the auth
# token and upload URL placheolders and upload the modified file to the
# the B2 bucket. This script needs to run at least once every 24 hours.

import json
import os
import shutil
import sys
from b2sdk.v1 import InMemoryAccountInfo
from b2sdk.v1 import B2Api

SNAP = os.getenv('SNAP')
SNAP_USER_COMMON = os.getenv('SNAP_USER_COMMON')

APPLICATION_KEY_ID = os.system("snapctl get b2-application-key-id")
APPLICATION_KEY = os.system("snapctl get b2-application-key")
BUCKET_NAME = os.system("snapctl get b2-bucket")

MEDIA_DIR = f'{SNAP_USER_COMMON}/media'
TEMPLATE_FILE = f'{SNAP}/uploader/dist/index.html'
INDEX_FILE = f'{MEDIA_DIR}/index.html'

def copy_template():
    """Copy tempate HTML from snap to writable directory"""
    if not os.path.isfile(TEMPLATE_FILE):
        sys.exit(f'Template file "{TEMPLATE_FILE}" not found')
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)
    shutil.copyfile(TEMPLATE_FILE, INDEX_FILE)

def tokens():
    """Request new authorization token and upload URL from Backblaze B2"""
    bucket = B2.get_bucket_by_name(BUCKET_NAME)
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
    bucket = B2.get_bucket_by_name(BUCKET_NAME)
    bucket.upload_local_file(INDEX_FILE, 'index.html')

B2 = B2Api(InMemoryAccountInfo())
B2.authorize_account('production', APPLICATION_KEY_ID, APPLICATION_KEY)

copy_template()
replace_keys()
upload()

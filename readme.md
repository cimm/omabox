<div align='center'>
  <img src='uploader/src/logo.webp'>
  <p>
    <em>A <a href='https://snapcraft.io/about'>snap</a> for <a href='https://ubuntu.com/core'>Ubuntu Core</a> intended to run on a <a href='https://www.raspberrypi.org/products/raspberry-pi-3-model-b/'>Raspberry Pi</a> as an internet-connected digital picture frame.</em>
  </p>
</div>

## What

A Raspberry Pi with a screen that loops over a local directory with pictures and periodically refreshes these from a Backblaze B2 bucket. New pictures in the bucket will, after a while, automatically show up on the picture frame.

## Why

We can no longer visit my grandmother - something to do with a worldwide pandemic - and she has no interest in learning how to use a tablet for video calls. She has one of these digital picture frames with the same 20 photos for years now. If only we would remember to refresh the pictures from time to time! Oh, wait, what if the family could send pictures to the device directly? A quick photo from the grandchildren at school? A picture of her newborn great-grandchild in the hospital?

## How

A little webpage where family and friends can upload images to a Backblaze B2 bucket on one side, a Raspberry Pi with a screen on the other. The Raspberry refreshes the pictures multiple times per day.

## Build Your Own

A bit geeky but not too much: no soldering or programming required. You’ll need a Raspberry Pi, tested with a 3 model B but any will do, with a screen. This should cost you around €90.

### 1. Ubuntu Core

Install Ubuntu Core on the Raspberry Pi. Ubuntu Core is a self-updating read-only (almost) OS. We could use any Linux for this project but Ubuntu Core and the applications (called snaps) will automatically update. This helps to keep maintenance low. Configure the wifi or connect the Pi via ethernet.

### 2. Backblaze B2

Create a Backblaze B2 bucket and add some (family) pictures. Create a new [App Key pair](https://help.backblaze.com/hc/en-us/articles/360052129034-Creating-and-Managing-Application-Keys) with read and write access to the bucket while you are at it.

You’ll also need to configure custom CORS headers on the bucket to allow for file uploads. This needs to be done via the [B2 command line tool](https://www.backblaze.com/b2/docs/quick_command_line.html). Replace the `NNNN` with the Backblaze subdomain for your bucket (check the friendly URL on any file in the bucket or use the downloadUrl from `b2 get-account-info`).

```sh
$ b2 update-bucket --corsRules '[
{
  "corsRuleName": "uploadsFromOmaBOX",
  "allowedOrigins": ["<https://NNNN.backblazeb2.com>"],
  "allowedHeaders": ["*"],
  "allowedOperations": ["b2_upload_file"],
  "exposeHeaders": ["authorization", "x-bz-file-name", "x-bz-content-sha1"],
  "maxAgeSeconds": 3600
}]' <bucket-name> allPublic
```

### 3. Snaps

Next, install the [mir-kiosk](https://snapcraft.io/mir-kiosk) snap on the Raspberry Pi, it runs graphical applications. The omaBOX snap is next, this adds an image viewer and some scripts to tie the whole thing together. Configure the B2 bucket and App Key pair.

```sh
$ snap install mir-kiosk
$ snap install omabox
$ snap set omabox b2-application-key-id=123abc b2-application-key=abc123 b2-bucket=abc
```

Wait for up to an hour for the Pi to sync and show the photos on the screen. An `index.html` file will appear in the bucket as well, this can be used by friends and family to quickly add new photos.

### 4. Optional Configuration

Each picture will be shown for 10 seconds, this can be changed via the omaBOX configuration settings on the Raspberry Pi.

```sh
$ snap set omabox imv-duration=30
```

## Development

This section explains the inner workings of the omaBOX snap and is not needed to get your omaBOX up and running.

The omaBOX snap has 3 main components, all run locally on the Raspberry Pi.

### 1. Image Viewer

The [imv](https://github.com/eXeC64/imv) image viewer for the heavy lifting of showing the pixels on the screen.

### 2. Downloader

A Python script that syncs the images from the bucket to the Pi via the [B2 SDK](https://github.com/Backblaze/b2-sdk-python) library. It runs hourly but this can all be tweaked in the [snapcraft.yaml](snap/snapcraft.yaml).

### 3. Uploader

An uploader script to refresh the B2 authorization key and upload URL in the `index.html` and upload it to the bucket, also via the B2 SDK. The `index.html` is a simple website so friends and family don’t need access to B2 bucket. Since the B2 authorization key is only valid for 24 hours the uploader needs to run daily. The `index.html` also resizes the pictures before uploading, it’s faster and I noticed imv has issues with larger images.

The `index.html` is a single HTML page for easier installation. The `uploader/src` folder is for development. Inline the JavaScript, CSS, and logo with [inliner](https://github.com/remy/inliner) to the `uploader/dist` folder before building a new snap.

```sh
inliner --nocompress uploader/src/index.html > uploader/dist/index.html
```

## FAQ

- Why is the screen upside down?

  Depending on your hardware the screen might be upside down. We can [rotate the screen](https://askubuntu.com/a/1293464) in the mir-kiosk config.

- How do I change the network settings?

  You can change the network settings via the `console-conf` command.

- Why does it show a number after the index.html file in my Backblaze bucket?

  The script reuploads the index.html file over and over with a new authorization key and upload URL. Backblaze will keep old versions around for [one day](https://help.backblaze.com/hc/en-us/articles/360039296494-How-to-set-Lifecycle-Rules-on-B2) before deleting them, even with the lifecycle settings set to only keep the last version.

## License

The snap itself, imv, and B2 SDK library are all MIT licensed. The omaBOX was forked from the [picviewer-kiosk](https://snapcraft.io/picviewer-kiosk) snap.

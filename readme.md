<div align='center'>
  <img src='logo.svg' alt='Logo' width='130px'/>
  <p><em>A <a href='https://snapcraft.io/about'>snap</a> for <a href='https://ubuntu.com/core'>Ubuntu Core</a> intended to run on a <a href='https://www.raspberrypi.org/products/raspberry-pi-3-model-b/'>Raspberry Pi</a> as an internet-connected digital picture frame.</em></p>
</div>

## What?

A Raspberry Pi with a screen that loops over a local directory with pictures and periodically refreshes these from a Backblaze B2 bucket. New pictures in the bucket will, after a while, automatically show up on the picture frame.

## Why?

We can no longer visit my grandmother - something to do with a worldwide pandemic - and she has no interest in learning how to use a tablet for video calls. How can we keep in touch without her needing to learn something new? She has one of these digital picture frames which has been looping over the same 20 photos for years now. If only we would remember to refresh the pictures from time to time! Wait, what if the family can send pictures to the device directly?

## How?

Install Ubuntu Core on a Raspberry Pi. Ubuntu Core is a self-updating read-only (almost) OS. We could use any Linux for this project but Ubuntu Core comes with 10 years of security updates and the OS and applications will automatically update. I am not going to explain to my grandmother how to use the terminal on her picture frame. The goal is as little maintenance as possible.

Now create a Backblaze B2 [bucket](https://www.backblaze.com/b2/docs/buckets.html) and add some family pictures. Create a new App Key pair with read-only access to the bucket while you are at it.

Next install the [mir-kiosk](https://snapcraft.io/mir-kiosk) snap, needed to run graphical applications. The omaBOX snap is next, it adds the [imv](https://github.com/eXeC64/imv) image viewer and script to periodically sync with the bucket. Configure the B2 bucket and App Key pair:

```sh
snap install mir-kiosk
snap install omabox
snap set omabox b2-application-key-id=123abc b2-application-key=abc123 b2-bucket=abc
```

Each picture will be shown for 10 seconds, this can be changed via the omaBOX configuration settings.

```sh
snap set omabox imv-duration=30
```

Depending on your hardware the screen might be upside down and the enclosure could make it impossible to physically turn the screen. Luckily we can [rotate the screen](https://askubuntu.com/a/1293464) in the mir-kiosk config.

## Uploader

Images can simply be uploaded to the bucket via the Backblaze website. The repository includes a small upload webpage in the `upload/` folder (work in progress) if multiple people want to upload photos to the same bucket.

## License

The snap itself, imv, and the [B2](https://github.com/Backblaze/B2_Command_Line_Tool) application are all MIT licensed. The icon is by [DesignBite](https://designbite.in/) and [CCBY](https://creativecommons.org/licenses/by/3.0/us/legalcode) licensed.

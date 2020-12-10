#!/usr/bin/env python3

# Calculates today's sunrise and sunset UTC times.
# Forked from https://stackoverflow.com/a/39867990

from datetime import datetime
import math
import sys

def forceRange(v, max):
    # force v to be >= 0 and < max
    if v < 0:
        return v + max
    elif v >= max:
        return v - max
    return v

def calcSunTime(coords, isRiseTime, zenith=90.8):
    now = datetime.utcnow()
    longitude = coords['longitude']
    latitude = coords['latitude']
    PI_RAD = math.pi/180

    # 1. first calculate the day of the year
    N1 = math.floor(275 * now.month / 9)
    N2 = math.floor((now.month + 9) / 12)
    N3 = (1 + math.floor((now.year - 4 * math.floor(now.year / 4) + 2) / 3))
    N = N1 - (N2 * N3) + now.day - 30

    # 2. convert the longitude to hour value and calculate an approximate time
    lngHour = longitude / 15
    if isRiseTime: # sunrise
        t = N + ((6 - lngHour) / 24)
    else: # sunset
        t = N + ((18 - lngHour) / 24)

    # 3. calculate the Sun's mean anomaly
    M = (0.9856 * t) - 3.289

    # 4. calculate the Sun's true longitude
    L = M + (1.916 * math.sin(PI_RAD*M)) + (0.020 * math.sin(PI_RAD * 2 * M)) + 282.634
    L = forceRange(L, 360) # adjusted into the range [0,360)

    # 5a. calculate the Sun's right ascension
    RA = (1/PI_RAD) * math.atan(0.91764 * math.tan(PI_RAD*L))
    RA = forceRange(RA, 360) # adjusted into the range [0,360)

    # 5b. right ascension value needs to be in the same quadrant as L
    Lquadrant  = (math.floor(L/90)) * 90
    RAquadrant = (math.floor(RA/90)) * 90
    RA = RA + (Lquadrant - RAquadrant)

    # 5c. right ascension value needs to be converted into hours
    RA = RA / 15

    # 6. calculate the Sun's declination
    sinDec = 0.39782 * math.sin(PI_RAD*L)
    cosDec = math.cos(math.asin(sinDec))

    # 7a. calculate the Sun's local hour angle
    cosH = (math.cos(PI_RAD*zenith) - (sinDec * math.sin(PI_RAD*latitude))) / (cosDec * math.cos(PI_RAD*latitude))
    if cosH > 1:
        sys.exit('The sun never rises on this location on the specified date')
    if cosH < -1:
        sys.exit('The sun never sets on this location on the specified date')

    # 7b. finish calculating H and convert into hours
    if isRiseTime:
        H = 360 - (1/PI_RAD) * math.acos(cosH)
    else: #setting
        H = (1/PI_RAD) * math.acos(cosH)
    H = H / 15

    # 8. calculate local mean time of rising/setting
    T = H + RA - (0.06571 * t) - 6.622

    # 9. adjust back to UTC
    UT = T - lngHour
    UT = forceRange(UT, 24) # UTC time in decimal format (e.g. 23.23)
    human = (forceRange(int(UT), 24) * 100) + round((UT - int(UT))*60)

    return {'decimal': UT, 'human': human}

def isDayTime(coords):
    sunset = calcSunTime(coords, False)
    sunrise = calcSunTime(coords, True)
    utc = datetime.utcnow()
    now = (utc.hour * 100) + utc.minute
    if now >= sunrise['human'] and now <= sunset['human']:
        return True
    return False

coords = {'latitude': 50.8898, 'longitude': 4.6982}
f = open("/sys/class/backlight/rpi_backlight/brightness", "w") # this file is probably not writable from within the snap
if isDayTime(coords):
    f.write("90")
else:
    f.write("20")
f.close()

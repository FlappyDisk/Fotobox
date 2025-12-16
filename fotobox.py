import sys
import os
import subprocess
from config import fotoboxCfg, fotoboxText
from datetime import datetime, date, time
from time import sleep
from picamera2 import Picamera2, Preview

picam = Picamera2()
picam.start_preview(Preview.QTGL)
preview_config = picam.create_preview_configuration()
capture_config = picam.create_still_configuration()

picam.configure(preview_config)
picam.start()
time.sleep(2)

image = picam.switch_mode_and_capture_image(capture_config)
image.show()

time.sleep(5)
picam.close()







try:
    import RPi.GPIO as GPIO
except ImportError:
    print("RPi GPIO not found - operating in simulation mode")
    fotoboxCfg['nopi']            = True   
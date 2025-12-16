import sys
import os
import subprocess
from config import fotoboxCfg, fotoboxText
from datetime import datetime, date, time
from time import sleep
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTime, QTimer, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QCursor
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from picamera2 import Picamera2, Preview

picam = Picamera2()
picam.start_preview(Preview.DRM)
preview_config = picam.create_preview_configuration()
capture_config = picam.create_still_configuration()

picam.configure(preview_config)
picam.start()
sleep(2)

image = picam.switch_mode_and_capture_file(capture_config, "photo.jpg")

sleep(5)
picam.close()

class Ui_Form_mod(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowTitle("Fotobox")
        Form.resize(fotoboxCfg['window-width'], fotoboxCfg['window-height'])
        Form.setMinimumSize(QtCore.QSize(fotoboxCfg['window-width'], fotoboxCfg['window-height']))
        Form.setMaximumSize(QtCore.QSize(fotoboxCfg['window-width'], fotoboxCfg['window-height']))
        Form.setHtml("Initializing...")
        self.countdownTime = fotoboxCfg['countdown']
        self.entries = None
        self.tplImage = "init.png"
        self.tplFooter = self.tplFooterOrg
        self.tplInstruct = "Instruction placeholder"
        self.tplBtn1 = "Button 1"
        self.tplBtn2 = "Button 2"
        self.tplBtn3 = "Button 3"
        with open('design/template.html', 'r') as myfile:
            self.template=myfile.read().replace('\n', '')

        if fotoboxCfg['nopi']:
            self.tplFooterOrg = "Demo simulation mode"







# try:
#     import RPi.GPIO as GPIO
# except ImportError:
#     print("RPi GPIO not found - operating in simulation mode")
#     fotoboxCfg['nopi']            = True   

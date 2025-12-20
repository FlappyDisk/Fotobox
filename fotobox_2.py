import sys
import os
import subprocess

from config import fotoboxText, fotoboxCfg

from datetime import datetime
from time import sleep

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebKitWidgets import QWebView

from shutil import copyfile, move
from stat import S_ISREG, ST_MTIME, ST_MODE

# ======================
# Camera / GPIO imports
# ======================
if not fotoboxCfg['nopi']:
    try:
        from picamera2 import Picamera2
        from picamera2.previews.qt import Preview
        from libcamera import controls
    except ImportError:
        print("Picamera2 not found - simulation mode")
        fotoboxCfg['nopi'] = True

    try:
        import RPi.GPIO as GPIO
    except ImportError:
        print("RPi.GPIO not found - simulation mode")
        fotoboxCfg['nopi'] = True


class Ui_Form_mod(object):
    def setupUi(self, Form):
        Form.setWindowTitle("Fotobox")
        Form.resize(fotoboxCfg['window-width'], fotoboxCfg['window-height'])
        Form.setMinimumSize(QtCore.QSize(fotoboxCfg['window-width'], fotoboxCfg['window-height']))
        Form.setMaximumSize(QtCore.QSize(fotoboxCfg['window-width'], fotoboxCfg['window-height']))
        Form.setHtml("Initializing...")

        self.countdownTime = fotoboxCfg['countdown']
        self.entries = None

        self.tplFooterOrg = "Fotobox 0.2 · © Florian Knodt"
        self.tplFooter = self.tplFooterOrg
        self.tplImage = "init.png"
        self.tplInstruct = ""
        self.tplBtn1 = ""
        self.tplBtn2 = ""
        self.tplBtn3 = ""

        with open('design/template.html', 'r') as f:
            self.template = f.read().replace('\n', '')

        if fotoboxCfg['nopi']:
            self.tplFooterOrg = "Demo simulation mode"

    def initSystem(self, Form):
        # ======================
        # Camera init
        # ======================
        if not fotoboxCfg['nopi']:
            self.camera = Picamera2()

            self.preview_config = self.camera.create_preview_configuration(
                main={"size": (fotoboxCfg['cam-p-width'], fotoboxCfg['cam-p-height'])}
            )

            self.capture_config = self.camera.create_still_configuration(
                main={"size": (fotoboxCfg['cam-c-width'], fotoboxCfg['cam-c-height'])}
            )

            self.camera.configure(self.preview_config)
            self.camera.set_controls({
                "HorizontalFlip": fotoboxCfg['cam-c-hflip'],
                "AfMode": controls.AfModeEnum.Continuous,
                "AeEnable": True,
                "AwbEnable": True
            })

        self.isLive = False

        # Countdown timer
        self.timerCnt = QTimer(Form)
        self.timerCnt.timeout.connect(self.updateCountdown)
        self.timerCnt.setSingleShot(True)

        self.lastPhoto = ""
        self.screen = ""
        self.temp = fotoboxCfg['temp'].rstrip('/') + '/'
        self.save = fotoboxCfg['save'].rstrip('/') + '/'

        os.makedirs(self.temp, exist_ok=True)
        os.makedirs(self.save, exist_ok=True)

    def updateHtml(self, Form):
        data = self.template
        data = data.replace('${btn1}', self.tplBtn1, 1)
        data = data.replace('${btn2}', self.tplBtn2, 1)
        data = data.replace('${btn3}', self.tplBtn3, 1)
        data = data.replace('${info}', self.tplInstruct, 1)
        data = data.replace('${status}', self.tplFooter, 1)
        data = data.replace('${image}', self.tplImage, 1)

        Form.setHtml(
            data,
            QUrl('file://' + os.path.dirname(os.path.realpath(__file__)) + '/design/.')
        )

    # ======================
    # Screens
    # ======================
    def screenMain(self, Form):
        self.screen = 1
        self.tplInstruct = fotoboxText['info-home']
        self.tplBtn1 = fotoboxText['btn-capture']
        self.tplBtn2 = fotoboxText['btn-view']
        self.tplBtn3 = fotoboxText['btn-empty']
        self.tplFooter = self.tplFooterOrg

        if not self.isLive:
            self.tplImage = "liveBack.png"
            if not fotoboxCfg['nopi']:
                self.camera.configure(self.preview_config)
                self.camera.start()
                self.camera.start_preview(
                    Preview.QTGL,
                    x=fotoboxCfg['cam-p-x'],
                    y=fotoboxCfg['cam-p-y'],
                    width=fotoboxCfg['cam-p-width'],
                    height=fotoboxCfg['cam-p-height']
                )
            self.isLive = True

        self.updateHtml(Form)

    def screenCapture(self, Form):
        self.screen = 2
        self.tplBtn1 = self.tplBtn2 = self.tplBtn3 = ""
        self.tplFooter = self.tplFooterOrg
        self.updateHtml(Form)

        self.countdownTime = fotoboxCfg['countdown']
        self.updateCountdown()

    def updateCountdown(self):
        Form = window
        self.tplInstruct = fotoboxText['info-count'].replace(
            '${countdown}', str(self.countdownTime), 1
        )
        self.updateHtml(Form)

        self.countdownTime -= 1

        if self.countdownTime > 0:
            self.timerCnt.start(1000)
        elif self.countdownTime == 0:
            self.timerCnt.start(750)
        elif self.countdownTime == -1:
            self.tplInstruct = fotoboxText['info-capture']
            self.tplImage = "capturing.png"
            self.tplFooter = "Capturing..."
            self.updateHtml(Form)
            self.timerCnt.start(250)
        else:
            self.photoTake(Form)

    def photoTake(self, Form):
        if self.isLive and not fotoboxCfg['nopi']:
            self.camera.stop_preview()
            self.camera.stop()
            self.isLive = False

        self.lastPhoto = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"

        if not fotoboxCfg['nopi']:
            self.camera.configure(self.capture_config)
            self.camera.start()
            self.camera.capture_file(self.temp + self.lastPhoto)
            self.camera.stop()
        else:
            copyfile(
                os.path.join(os.path.dirname(__file__), 'design/dummy.jpg'),
                self.temp + self.lastPhoto
            )

        self.screenReview(Form)

    def screenReview(self, Form):
        self.screen = 3
        self.tplInstruct = fotoboxText['info-review']
        self.tplBtn1 = fotoboxText['btn-save']
        self.tplBtn2 = fotoboxText['btn-recapture']
        self.tplBtn3 = fotoboxText['btn-cancel']
        self.tplImage = self.temp + self.lastPhoto
        self.tplFooter = "Foto: " + self.lastPhoto
        self.updateHtml(Form)

    def tempDel(self):
        if self.lastPhoto and os.path.isfile(self.temp + self.lastPhoto):
            os.remove(self.temp + self.lastPhoto)
            self.lastPhoto = ""

    def doConfirm(self, Form):
        move(self.temp + self.lastPhoto, self.save + self.lastPhoto)
        self.screenMain(Form)

    def retry(self, Form):
        self.tempDel()
        self.screenCapture(Form)

    def noConfirm(self, Form):
        self.tempDel()
        self.screenMain(Form)


class QWebView_mod(QWebView):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form_mod()
        self.ui.setupUi(self)
        self.ui.initSystem(self)
        self.ui.screenMain(self)

        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))

        if not fotoboxCfg['nopi']:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            self.btnC1 = GPIO.HIGH
            self.btnC2 = GPIO.HIGH
            self.btnC3 = GPIO.HIGH

        self.timerKey = QTimer(self)
        self.timerKey.timeout.connect(self.buttonCheck)
        self.timerKey.start(25)
        self.btnB = 1

        self.showFullScreen()

    def buttonCheck(self):
        if fotoboxCfg['nopi']:
            return

        if self.btnB == 0:
            for pin, btn in [(17, 1), (21, 2), (22, 3)]:
                if GPIO.input(pin) == GPIO.LOW:
                    self.buttonPress(btn)
                    self.btnB = 3
        else:
            self.btnB -= 1

    def buttonPress(self, btn):
        if self.ui.screen == 1 and btn == 1:
            self.ui.screenCapture(self)
        elif self.ui.screen == 3:
            if btn == 1:
                self.ui.doConfirm(self)
            elif btn == 2:
                self.ui.retry(self)
            elif btn == 3:
                self.ui.noConfirm(self)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif e.key() == QtCore.Qt.Key_1:
            self.buttonPress(1)
        elif e.key() == QtCore.Qt.Key_2:
            self.buttonPress(2)
        elif e.key() == QtCore.Qt.Key_3:
            self.buttonPress(3)


app = QApplication(sys.argv)
window = QWebView_mod()
sys.exit(app.exec_())

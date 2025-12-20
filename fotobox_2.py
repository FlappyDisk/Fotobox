import sys
import os

from config import fotoboxText, fotoboxCfg
from datetime import datetime
from shutil import copyfile, move
from stat import S_ISREG, ST_MTIME, ST_MODE

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngine import QtWebEngine

# ==========================
# Enable QtWebEngine
# ==========================
QtWebEngine.initialize()

# ==========================
# Camera / GPIO
# ==========================
if not fotoboxCfg['nopi']:
    try:
        from picamera2 import Picamera2
        from picamera2.previews.qt import Preview
        from libcamera import controls
    except ImportError:
        print("Picamera2 missing – simulation mode")
        fotoboxCfg['nopi'] = True

    try:
        import RPi.GPIO as GPIO
    except ImportError:
        print("GPIO missing – simulation mode")
        fotoboxCfg['nopi'] = True


class Ui_Form_mod:
    def setupUi(self, Form):
        Form.setWindowTitle("Fotobox")
        Form.showFullScreen()

        self.tplImage = "init.png"
        self.tplFooterOrg = "Fotobox · Simulation" if fotoboxCfg['nopi'] else "Fotobox"
        self.tplFooter = self.tplFooterOrg
        self.tplInstruct = ""
        self.tplBtn1 = ""
        self.tplBtn2 = ""
        self.tplBtn3 = ""

        with open("design/template.html", "r") as f:
            self.template = f.read().replace("\n", "")

        self.countdownTime = fotoboxCfg['countdown']
        self.isLive = False
        self.screen = 0
        self.lastPhoto = ""

        self.temp = fotoboxCfg['temp'].rstrip("/") + "/"
        self.save = fotoboxCfg['save'].rstrip("/") + "/"
        os.makedirs(self.temp, exist_ok=True)
        os.makedirs(self.save, exist_ok=True)

    def initSystem(self, Form):
        if not fotoboxCfg['nopi']:
            self.camera = Picamera2()

            self.preview_cfg = self.camera.create_preview_configuration(
                main={"size": (fotoboxCfg['cam-p-width'], fotoboxCfg['cam-p-height'])}
            )
            self.capture_cfg = self.camera.create_still_configuration(
                main={"size": (fotoboxCfg['cam-c-width'], fotoboxCfg['cam-c-height'])}
            )

            self.camera.configure(self.preview_cfg)
            self.camera.set_controls({
                "HorizontalFlip": fotoboxCfg['cam-c-hflip'],
                "AfMode": controls.AfModeEnum.Continuous,
                "AeEnable": True,
                "AwbEnable": True
            })

        self.timerCnt = QTimer(Form)
        self.timerCnt.timeout.connect(self.updateCountdown)
        self.timerCnt.setSingleShot(True)

    # ==========================
    # HTML update
    # ==========================
    def updateHtml(self, Form):
        html = self.template
        html = html.replace("${btn1}", self.tplBtn1, 1)
        html = html.replace("${btn2}", self.tplBtn2, 1)
        html = html.replace("${btn3}", self.tplBtn3, 1)
        html = html.replace("${info}", self.tplInstruct, 1)
        html = html.replace("${status}", self.tplFooter, 1)
        html = html.replace("${image}", "file://" + os.path.abspath(self.tplImage), 1)
        Form.setHtml(html)

    # ==========================
    # Screens
    # ==========================
    def screenMain(self, Form):
        self.screen = 1
        self.tplInstruct = fotoboxText['info-home']
        self.tplBtn1 = fotoboxText['btn-capture']
        self.tplBtn2 = fotoboxText['btn-view']
        self.tplBtn3 = ""
        self.tplFooter = self.tplFooterOrg
        self.tplImage = "liveBack.png"

        if not fotoboxCfg['nopi'] and not self.isLive:
            self.camera.configure(self.preview_cfg)
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
        self.countdownTime = fotoboxCfg['countdown']
        self.updateCountdown()

    def updateCountdown(self):
        Form = window
        self.tplInstruct = fotoboxText['info-count'].replace(
            "${countdown}", str(self.countdownTime), 1
        )
        self.updateHtml(Form)

        self.countdownTime -= 1

        if self.countdownTime >= 0:
            self.timerCnt.start(1000)
        else:
            self.photoTake(Form)

    def photoTake(self, Form):
        if not fotoboxCfg['nopi']:
            self.camera.stop_preview()
            self.camera.stop()
            self.isLive = False

        self.lastPhoto = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"

        if not fotoboxCfg['nopi']:
            self.camera.configure(self.capture_cfg)
            self.camera.start()
            self.camera.capture_file(self.temp + self.lastPhoto)
            self.camera.stop()
        else:
            copyfile("design/dummy.jpg", self.temp + self.lastPhoto)

        self.screenReview(Form)

    def screenReview(self, Form):
        self.screen = 3
        self.tplInstruct = fotoboxText['info-review']
        self.tplBtn1 = fotoboxText['btn-save']
        self.tplBtn2 = fotoboxText['btn-recapture']
        self.tplBtn3 = fotoboxText['btn-cancel']
        self.tplImage = self.temp + self.lastPhoto
        self.tplFooter = self.lastPhoto
        self.updateHtml(Form)

    def doConfirm(self, Form):
        move(self.temp + self.lastPhoto, self.save + self.lastPhoto)
        self.screenMain(Form)

    def retry(self, Form):
        os.remove(self.temp + self.lastPhoto)
        self.screenCapture(Form)

    def noConfirm(self, Form):
        os.remove(self.temp + self.lastPhoto)
        self.screenMain(Form)


class QWebView_mod(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form_mod()
        self.ui.setupUi(self)
        self.ui.initSystem(self)
        self.ui.screenMain(self)

        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))

        if not fotoboxCfg['nopi']:
            GPIO.setmode(GPIO.BCM)
            for pin in (17, 21, 22):
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.timerKey = QTimer(self)
        self.timerKey.timeout.connect(self.buttonCheck)
        self.timerKey.start(25)

    def buttonCheck(self):
        if fotoboxCfg['nopi']:
            return

        if GPIO.input(17) == GPIO.LOW:
            self.buttonPress(1)
        elif GPIO.input(21) == GPIO.LOW:
            self.buttonPress(2)
        elif GPIO.input(22) == GPIO.LOW:
            self.buttonPress(3)

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

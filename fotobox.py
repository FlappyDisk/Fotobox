import sys
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, Qt, QTimer

from picamera2 import Picamera2

from config import fotoboxCfg, fotoboxText


# ---------- Camera bridge ----------
class CameraBridge(QObject):
    def __init__(self, picam, output_dir, view):
        super().__init__()
        self.picam = picam
        self.output_dir = output_dir
        self.view = view

    @pyqtSlot()
    def capture(self):
        filename = datetime.now().strftime("photo_%Y%m%d_%H%M%S.jpg")
        path = self.output_dir / filename

        self.picam.capture_file(str(path))

        # Update image in HTML
        js = f'document.getElementById("photo").src = "{filename}?t={datetime.now().timestamp()}"'
        self.view.page().runJavaScript(js)


class PhotoBox(QMainWindow):
    def __init__(self):
        super().__init__()

        # ---------- Window ----------
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setCursor(Qt.BlankCursor)

        # ---------- Web view ----------
        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)

        # ---------- Paths ----------
        self.design_dir = Path(fotoboxCfg["design_dir"]).resolve()
        self.layout_file = Path(fotoboxCfg["layout_file"]).resolve()
        self.output_dir = Path(fotoboxCfg["photo_dir"]).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # ---------- Camera ----------
        self.picam = Picamera2()
        config = self.picam.create_still_configuration(main={"size": (1920, 1080)})
        self.picam.configure(config)
        self.picam.start()

        # ---------- HTML ----------
        html = self.render_html(
            info=fotoboxText["info-home"],
            btn1=fotoboxText["btn-capture"],
            btn2=fotoboxText["btn-view"],
            btn3="",
            image="placeholder.png"
        )

        self.view.setHtml(html, QUrl(self.design_dir.as_uri() + "/"))

        # ---------- WebChannel ----------
        self.channel = QWebChannel()
        self.bridge = CameraBridge(self.picam, self.output_dir, self.view)
        self.channel.registerObject("camera", self.bridge)
        self.view.page().setWebChannel(self.channel)

        QTimer.singleShot(0, self.showFullScreen)

    def render_html(self, info, btn1, btn2, btn3, image):
        html = self.layout_file.read_text(encoding="utf-8")
        return (
            html.replace("${info}", info)
                .replace("${btn1}", btn1)
                .replace("${btn2}", btn2)
                .replace("${btn3}", btn3)
                .replace("${image}", image)
        )

    def closeEvent(self, event):
        self.picam.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoBox()
    sys.exit(app.exec_())

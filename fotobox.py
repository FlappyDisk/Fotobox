import sys
import os
import subprocess
from config import fotoboxCfg, fotoboxText
from datetime import datetime, date, time
from time import sleep
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


class PhotoBox(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fotobox")
        self.resize(
            fotoboxCfg['window-width'],
            fotoboxCfg['window-height']
        )

        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)

        # Paths
        project_dir = fotoboxCfg['project_dir']
        design_dir = fotoboxCfg['design_dir']
        layout_file = fotoboxCfg['layout_file']

        html = self.render_html(
            layout_file,
            info=fotoboxText['info-home'],
            btn1=fotoboxText['btn-capture'],
            btn2=fotoboxText['btn-view'],
            btn3="",
            image="placeholder.png"
        )

        # baseUrl must point to the design directory
        self.view.setHtml(
            html,
            QUrl.fromLocalFile(str(design_dir) + "/")
        )

    def render_html(self, layout_file, info, btn1, btn2, btn3, image):
        layout_path = Path(layout_file)
        html = layout_path.read_text(encoding="utf-8")

        return (
            html.replace("${info}", info)
                .replace("${btn1}", btn1)
                .replace("${btn2}", btn2)
                .replace("${btn3}", btn3)
                .replace("${image}", image)
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoBox()
    window.show()
    sys.exit(app.exec_())

        
# picam = Picamera2()
# picam.start_preview(Preview.DRM, x=fotoboxCfg['cam-p-x'], y=fotoboxCfg['cam-p-y'], width = fotoboxCfg['cam-p-width'], height = fotoboxCfg['cam-p-height'], transform = Transform(hflip=fotoboxCfg['cam-p-hflip']))
# preview_config = picam.create_preview_configuration()
# capture_config = picam.create_still_configuration()

# picam.configure(preview_config)
# picam.start()
# sleep(2)

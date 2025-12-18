import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from pathlib import Path


class PhotoBox(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fotobox")
        self.resize(1280, 1024)

        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)

        # Paths
        project_dir = Path(__file__).parent
        design_dir = project_dir / "design"
        layout_file = design_dir / "layout.html"

        html = self.render_html(
            layout_file,
            info="Scan QR code to download your photo",
            btn1="Start",
            btn2="Retry",
            btn3="Exit",
            image="placeholder.png"  # ← just filename
        )

        # IMPORTANT: baseUrl points to design folder
        self.view.setHtml(html, QUrl.fromLocalFile(str(design_dir)+"/"))

    def render_html(self, layout_file, info, btn1, btn2, btn3, image):
        html = layout_file.read_text(encoding="utf-8")

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
    sys.exit(app.exec())

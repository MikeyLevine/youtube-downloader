# Main UI logic
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        pass  # Suppress KeyboardInterrupt message

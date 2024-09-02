import sys
import threading
from PyQt5.QtWidgets import QApplication
from main import MainWindow
from receipt_template import app as flask_app

def run_flask():
    flask_app.run(host='0.0.0.0', port=1717)

class MosysPrinterWindow(MainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mosys Printer')  # Set the window title here

if __name__ == "__main__":
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Run PyQt5 application
    qt_app = QApplication(sys.argv)
    main_window = MosysPrinterWindow()
    main_window.show()
    sys.exit(qt_app.exec_())
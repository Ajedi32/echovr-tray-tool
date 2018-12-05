from PySide2.QtWidgets import QApplication
from .main_window import MainWindow

if __name__ == "__main__":
    import sys

    app = QApplication()

    mw = MainWindow()
    mw.show()

    sys.exit(app.exec_())

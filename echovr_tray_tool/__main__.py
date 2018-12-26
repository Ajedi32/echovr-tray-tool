from PySide2.QtWidgets import QApplication
from .main_window import MainWindow
from .single_application import SingleApplication, AlreadyRunningError

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Start the Echo VR tray tool')
    parser.add_argument(
        '--minimized', '-m',
        action='store_const',
        const=True,
        default=False
    )

    args = parser.parse_args()

    try:
        app = SingleApplication("562C83BD-3964-4CAD-B86F-91DE535BA5CE")
    except AlreadyRunningError:
        print('app is already running')
        sys.exit(1)

    mw = MainWindow()
    if not args.minimized:
        mw.show()

    sys.exit(app.exec_())

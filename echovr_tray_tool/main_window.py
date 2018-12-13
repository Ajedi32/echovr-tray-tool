from PySide2.QtWidgets import QMainWindow, QLabel, QBoxLayout, QWidget, \
                              QSystemTrayIcon, QStyle, QAction, QMenu, qApp
from .discord_presence import DiscordPresenceThread

class MainWindow(QMainWindow):
    """The main window of the application

    Currently just displays "Hello, world!".
    """

    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(300, 25)
        self.setWindowTitle("Echo VR Tray Tool")

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        main_layout = QBoxLayout(QBoxLayout.TopToBottom, main_widget)

        main_layout.addWidget(QLabel("Hello, world!", self), 0, 0)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(
            # TODO: Design better icon
            self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        )

        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self._quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self._discord_presence_thread = None
        self._start_discord_presence_thread()

    def closeEvent(self, event):
        """Overridden to minimize to tray instead of exiting"""

        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Application is still running",
            "Echo VR Tray Tool was minimized to tray. Right-click and press 'exit' to quit.",
            QSystemTrayIcon.Information,
            3000,
        )

    def _quit(self):
        if self._discord_presence_thread:
            self._discord_presence_thread.exit()
            self._discord_presence_thread.wait()

        qApp.quit()

    def _start_discord_presence_thread(self):
        if self._discord_presence_thread:
            return

        self._discord_presence_thread = DiscordPresenceThread()
        self._discord_presence_thread.start()

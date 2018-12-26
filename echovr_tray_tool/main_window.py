from PySide2.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, \
                              QSystemTrayIcon, QStyle, QAction, QMenu, qApp
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from .discord_presence import DiscordPresenceThread

_HEADER_FONT = QFont("helvetica", weight=QFont.Bold)
_RED_LABEL = "QLabel { color: red }"
_GREEN_LABEL = "QLabel { color: green }"

class MainWindow(QMainWindow):
    """The main window of the application

    Currently just displays "Hello, world!".
    """

    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(300, 50)
        self.setWindowTitle("Echo VR Tray Tool")

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        main_layout = QGridLayout(main_widget)

        discord_status_header = QLabel("Discord status:")
        discord_status_header.setFont(_HEADER_FONT)
        main_layout.addWidget(discord_status_header, 0, 0, Qt.AlignRight)

        self._discord_status_label = QLabel("Unknown")
        main_layout.addWidget(self._discord_status_label, 0, 1, Qt.AlignLeft)

        echo_vr_status_header = QLabel("Echo VR client status:")
        echo_vr_status_header.setFont(_HEADER_FONT)
        main_layout.addWidget(echo_vr_status_header, 1, 0, Qt.AlignRight)

        self._echo_vr_client_status_label = QLabel("Unknown")
        main_layout.addWidget(self._echo_vr_client_status_label, 1, 1, Qt.AlignLeft)

        main_layout.setRowStretch(2, 1)

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
        self._discord_presence_thread.connection_status_changed.connect(
            self._discord_connection_status_changed
        )
        self._discord_presence_thread.game_client_status_changed.connect(
            self._game_client_status_changed
        )
        self._discord_presence_thread.start()

    def _discord_connection_status_changed(self, connected):
        if connected:
            self._discord_status_label.setText("Connected")
            self._discord_status_label.setStyleSheet(_GREEN_LABEL)
        else:
            self._discord_status_label.setText("Disconnected")
            self._discord_status_label.setStyleSheet(_RED_LABEL)

    def _game_client_status_changed(self, connected):
        if connected:
            self._echo_vr_client_status_label.setText("Connected")
            self._echo_vr_client_status_label.setStyleSheet(_GREEN_LABEL)
        else:
            self._echo_vr_client_status_label.setText("Disconnected")
            self._echo_vr_client_status_label.setStyleSheet(_RED_LABEL)

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTextStream, Signal, Qt
from PySide2.QtNetwork import QLocalSocket, QLocalServer

class AlreadyRunningError(Exception):
    """Indicates that an instance of a SingleApplication is already running"""
    pass

class SingleApplication(QApplication):
    """A QApplication that can tell if another instance of itself is running

    :param id:
        A unique string used to identify other instances of the application.

    :raises AlreadyRunningError:
        Raised when you try to instantiate a SingleApplication with the ID of an
        application that is already running on the current machine.
    """

    messageReceived = Signal(str)

    def __init__(self, id):
        super().__init__()
        self._id = id

        # Try to connect to existing application instance's server
        self._out_socket = QLocalSocket()
        self._out_socket.connectToServer(self._id)

        # Connection succeeded?
        if self._out_socket.waitForConnected(msecs=1000):
            raise AlreadyRunningError(
                f"An instance of this application ({id}) is already running."
            )

        # Start server to inform future instances that we're already running
        self._out_socket = None
        self._server = QLocalServer()
        self._server.listen(self._id)

    @property
    def is_running(self):
        """Whether another instance of the application is already running"""
        return self._is_running

    @property
    def id(self):
        return self._id

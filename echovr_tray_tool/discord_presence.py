import time
import logging
from PySide2.QtCore import QThread, Signal
import pypresence
import echovr_api
from requests.exceptions import ConnectionError
from json.decoder import JSONDecodeError

log = logging.getLogger(__name__)

DISCORD_CLIENT_ID = 520065461896085515

GAME_STATUS_DICT = {
    "pre_match": "Pre-match",
    "playing": "In-progress",
    "score": "Round start",
    "round_start": "Round start",
    "pre_sudden_death": "Overtime",
    "sudden_death": "Overtime",
    "post_sudden_death": "Post-match",
    "round_over": "Post-match",
    "post_match": "Post-match",
}

class DiscordPresenceThread(QThread):
    """A thread responsible for keeping Discord Presence updated"""

    connection_status_changed = Signal(bool)
    game_client_status_changed = Signal(bool)

    def __init__(self):
        super().__init__()

        self._presence_client = pypresence.Presence(DISCORD_CLIENT_ID)
        self.__connected = False

        self._game_client_running = False
        self._game_state = None

    def run(self):
        """Start updating Discord Presence

        Use `requestInterruption` or `exit` to stop.
        """

        log.debug("Discord presence service started.")

        while not self.isInterruptionRequested():
            self._refresh_presence()
            self._interruptible_sleep(15) # Discord Presence rate limit

        log.debug("Stopping Discord presence service...")

        self._disconnect()

        log.debug("Discord presence service stopped.")

    def exit(self, retcode=0):
        """Stop updating Discord presence"""

        self.requestInterruption()
        super().exit(retcode)

    @property
    def connected(self):
        """Returns whether we're currently connected to Discord"""
        return self._connected

    @property
    def _connected(self):
        return self.__connected

    @_connected.setter
    def _connected(self, value):
        self.connection_status_changed.emit(value)
        self.__connected = value

    @property
    def game_client_running(self):
        """Returns whether we're connected to the Echo VR game client"""
        return self._game_client_running

    @property
    def _game_client_running(self):
        return self.__game_client_running

    @_game_client_running.setter
    def _game_client_running(self, value):
        self.game_client_status_changed.emit(value)
        self.__game_client_running = value

    def _refresh_presence(self):
        """Refresh Discord presence"""

        if not self._connect():
            return

        self._refresh_game_client_status()
        if self._game_client_running:
            if self._game_state != None:
                self._set_game_state_presence()
            else:
                self._set_idle_presence()
        else:
            self._clear_presence()

    def _connect(self):
        """Attempt to connect to Discord

        :returns: True if successful, otherwise False
        """
        if self._connected:
            return True

        try:
            self._presence_client.connect()
            self._connected = True
        except pypresence.exceptions.InvalidPipe:
            log.info("Failed to connect to Discord, likely because it is not running.")
            return False

        log.debug("Successfully connected to Discord.")
        return True

    def _disconnect(self):
        """Disconnect from Discord"""
        if not self._connected:
            return
        self._clear_presence()
        self._presence_client.close()
        self._connected = False

    def _set_presence(self, **details):
        """Set Discord presence to the specified state"""

        log.debug(f"Updating Discord presence: {str(details)}")

        try:
            self._presence_client.update(**details)
        except pypresence.exceptions.InvalidID as ex:
            log.info("Failed to update Discord Presence, likely because Discord is no longer running.")
            self._connected = False

    def _clear_presence(self, **details):
        """Clear Discord presence"""

        log.debug(f"Clearing Discord presence...")

        try:
            self._presence_client.clear()
        except pypresence.exceptions.InvalidID as ex:
            log.info("Failed to update Discord Presence, likely because Discord is no longer running.")
            self._connected = False

    def _set_idle_presence(self):
        """Update Discord presence to indicate the player is not in a match"""

        self._set_presence(
            large_image = 'echo_vr_cover_square_image',
            large_text = 'Echo VR',
        )

    def _set_game_state_presence(self):
        """Update Discord presence based on current game state"""

        state = self._game_state

        is_spectating = state.find_player(username=state.client_name) == None

        match_type = "Private" if state.private_match else "Public"
        score = f"{state.orange_team.score}-{state.blue_team.score}"
        blue_team_size = len(state.blue_team.players)
        orange_team_size = len(state.orange_team.players)
        team_size = f"{orange_team_size}v{blue_team_size}"
        role = "Spectating" if is_spectating else "Playing"
        game_status = GAME_STATUS_DICT.get(state.game_status, "Unknown")
        show_end_time = state.game_status == "playing"
        end_time = round(time.time() + state.game_clock)

        response = self._set_presence(
            details = f"Arena {match_type} ({team_size}): {score}",
            state = f"{role} - {game_status}",
            large_image = 'echo_vr_cover_square_image',
            large_text = 'Echo VR',
            small_image = 'echo_arena_store_icon_512x512',
            small_text = 'Echo Arena',
            end = end_time if show_end_time else None,
        )

    def _refresh_game_client_status(self):
        """Check if Echo VR is running and update game state"""

        try:
            self._game_state = echovr_api.fetch_state()
            self._game_client_running = True
            log.debug("Echo VR game state updated")
        except ConnectionError:
            self._game_state = None
            self._game_client_running = False
            log.debug("Failed to connect to Echo VR API. Either Echo VR is not running, or it was not started with the -http flag.")
        except JSONDecodeError:
            self._game_state = None
            self._game_client_running = True
            log.debug("Echo VR API returned invalid response, likely because a game is not in-progress.")

    def _interruptible_sleep(self, seconds, checkInterval=1.0/60.0):
        """A sleep that aborts early if `self.isInterruptionRequested()`"""

        while seconds > 0 and not self.isInterruptionRequested():
            sleepTime = min(seconds, checkInterval)
            self.msleep(sleepTime*1000)
            seconds -= sleepTime

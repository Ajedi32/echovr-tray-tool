import time
from PySide2.QtCore import QThread
from pypresence import Presence
import echovr_api
from requests.exceptions import ConnectionError
from json.decoder import JSONDecodeError

DISCORD_CLIENT_ID = 520065461896085515

class DiscordPresenceThread(QThread):
    """A thread responsible for keeping Discord Presence updated"""

    def __init__(self):
        super().__init__()

        self._presence_client = Presence(DISCORD_CLIENT_ID)
        self._connected = False

        self._game_client_running = False
        self._game_state = None

    def run(self):
        """Start updating Discord Presence

        Use `requestInterruption` or `exit` to stop.
        """
        while not self.isInterruptionRequested():
            self._update_presence()
            self._interruptible_sleep(15) # Discord Presence rate limit
        self._disconnect()

    def exit(self, retcode=0):
        """Stop updating Discord presence"""

        self.requestInterruption()
        super().exit(retcode)

    def _connect(self):
        if self._connected:
            return
        self._presence_client.connect()
        self._connected = True

    def _disconnect(self):
        if not self._connected:
            return
        self._presence_client.clear()
        self._presence_client.close()
        self._connected = False

    def _set_idle_presence(self):
        """Update Discord presence to indicate the player is not in a match"""
        self._presence_client.update(
            large_image = 'echo_vr_logo',
            large_text = 'Echo VR',
        )

    def _set_game_state_presence(self):
        """Update Discord presence based on current game state"""

        state = self._game_state

        is_spectating = state.find_player(username=state.client_name) == None

        match_type = "Private" if state.private_match else "Public"
        score = f"{state.blue_team.score}-{state.orange_team.score}"
        blue_team_size = len(state.blue_team.players)
        orange_team_size = len(state.orange_team.players)
        team_size = f"{blue_team_size}v{orange_team_size}"
        role = "Spectating" if is_spectating else "Playing"
        clock = state.game_clock_display

        response = self._presence_client.update(
            details = f"Arena {match_type} ({team_size}): {score}",
            state = f"{role}",
            large_image = 'echo_vr_logo',
            large_text = 'Echo Arena',
            end = round(time.time() + state.game_clock),
        )

    def _update_presence(self):
        """Refresh Discord presence"""

        self._refresh_game_client_status()
        if self._game_client_running:
            self._connect()
            if self._game_state != None:
                self._set_game_state_presence()
            else:
                self._set_idle_presence()
        else:
            self._disconnect()

    def _refresh_game_client_status(self):
        """Check if Echo VR is running and update game state"""

        try:
            self._game_state = echovr_api.fetch_state()
            self._game_client_running = True
        except ConnectionError:
            self._game_state = None
            self._game_client_running = False
        except JSONDecodeError:
            self._game_state = None
            self._game_client_running = True

    def _interruptible_sleep(self, seconds, checkInterval=1.0/60.0):
        """A sleep that aborts early if `self.isInterruptionRequested()`"""

        while seconds > 0 and not self.isInterruptionRequested():
            sleepTime = min(seconds, checkInterval)
            self.msleep(sleepTime*1000)
            seconds -= sleepTime

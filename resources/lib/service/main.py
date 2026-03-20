"""
EasyMovie background service.

Lightweight service that monitors movie playback for set awareness.
No daemon loop — just a playback monitor and abort wait.

Logging:
    Logger: 'service'
    Key events:
        - service.start (INFO): Service started
        - service.stop (INFO): Service stopping
    See LOGGING.md for full guidelines.
"""
import xbmc

from resources.lib.utils import get_logger
from resources.lib.service.playback_monitor import MoviePlaybackMonitor


def main() -> None:
    """Run the EasyMovie background service."""
    log = get_logger('service')
    log.info("EasyMovie service started", event="service.start")

    monitor = xbmc.Monitor()
    # Must keep reference to prevent garbage collection — Kodi calls
    # the Player subclass callbacks as long as the object is alive.
    _player = MoviePlaybackMonitor()

    while not monitor.abortRequested():
        if monitor.waitForAbort(1):
            break

    del _player  # Explicit cleanup before service exit
    log.info("EasyMovie service stopping", event="service.stop")

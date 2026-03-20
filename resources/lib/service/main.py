"""
EasyMovie background service.

Lightweight service that monitors movie playback for set awareness.
No daemon loop — just a playback monitor and abort wait.

Logging:
    Logger: 'service'
    Key events:
        - service.start (INFO): Service started with version, device, Kodi build
        - service.stop (INFO): Service stopping
    See LOGGING.md for full guidelines.
"""
import socket

import xbmc
import xbmcaddon

from resources.lib.utils import get_logger
from resources.lib.service.playback_monitor import MoviePlaybackMonitor


def _get_device_name() -> str:
    """Return the Kodi device friendly name, falling back to hostname."""
    try:
        name = xbmc.getInfoLabel('System.FriendlyName')
        if name:
            return name
        return socket.gethostname() or 'unknown'
    except Exception:
        return 'unknown'


def _get_kodi_version() -> str:
    """Return the Kodi build version (first word only)."""
    try:
        build = xbmc.getInfoLabel('System.BuildVersion')
        if build:
            return build.split()[0]
        return 'unknown'
    except Exception:
        return 'unknown'


def main() -> None:
    """Run the EasyMovie background service."""
    addon = xbmcaddon.Addon()
    version = addon.getAddonInfo('version')

    log = get_logger('service')
    log.info(
        "EasyMovie service started",
        event="service.start",
        version=version,
        device=_get_device_name(),
        kodi=_get_kodi_version(),
    )

    monitor = xbmc.Monitor()
    # Must keep reference to prevent garbage collection — Kodi calls
    # the Player subclass callbacks as long as the object is alive.
    _player = MoviePlaybackMonitor()

    while not monitor.abortRequested():
        if monitor.waitForAbort(1):
            break

    del _player  # Explicit cleanup before service exit
    log.info(
        "EasyMovie service stopping",
        event="service.stop",
        version=version,
        device=_get_device_name(),
    )

"""
EasyMovie Clone Creation.

Creates independent "clones" of EasyMovie with separate settings.
Useful for pre-configured instances like "Kids Movies", "Action Night", etc.

Logging:
    Logger: 'clone'
    Key events:
        - clone.create (INFO): Clone created successfully
        - clone.fail (ERROR): Clone creation failed
    See LOGGING.md for full guidelines.
"""
import json
import os
import shutil

import xbmc
import xbmcaddon

from resources.lib.utils import get_logger, notify
from resources.lib.constants import ADDON_ID, ADDON_NAME

log = get_logger('clone')


def _sanitize_filename(dirty_string: str) -> str:
    """Sanitize a string for use as an addon ID component."""
    import string as string_module
    dirty_string = dirty_string.strip()
    valid_chars = f"-_.(){string_module.ascii_letters}{string_module.digits} "
    sanitized = ''.join(c for c in dirty_string if c in valid_chars)
    sanitized = sanitized.replace(' ', '_').lower()
    return sanitized


def _replace_in_file(filepath: str, replacements: list) -> None:
    """Perform string replacements in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def create_clone() -> None:
    """Create a clone of the EasyMovie addon."""
    # Get clone name from user
    keyboard = xbmc.Keyboard('', 'Enter a name for the clone')
    keyboard.doModal()

    if not keyboard.isConfirmed():
        return

    clone_name = keyboard.getText().strip()
    if not clone_name:
        return

    sanitized = _sanitize_filename(clone_name)
    if not sanitized:
        log.error("Invalid clone name", event="clone.fail", name=clone_name)
        notify("Clone creation failed - invalid name")
        return

    clone_id = f"script.easymovie.{sanitized}"
    combined_name = f"{ADDON_NAME} - {clone_name}"

    # Get paths
    addon = xbmcaddon.Addon(ADDON_ID)
    addon_path = addon.getAddonInfo('path')
    parent_dir = os.path.dirname(addon_path)
    clone_path = os.path.join(parent_dir, clone_id)

    # Check if clone already exists
    if os.path.exists(clone_path):
        log.warning("Clone already exists", event="clone.fail",
                    clone_id=clone_id, path=clone_path)
        notify("Clone already exists")
        return

    try:
        # Copy addon files
        shutil.copytree(addon_path, clone_path,
                        ignore=shutil.ignore_patterns(
                            '.git*', '__pycache__', '*.pyc',
                            'clone.py', 'docs', 'tests',
                        ))

        # Replace addon.xml with clone template
        clone_addon_xml = os.path.join(addon_path, 'resources', 'addon_clone.xml')
        target_addon_xml = os.path.join(clone_path, 'addon.xml')
        shutil.copy2(clone_addon_xml, target_addon_xml)

        _replace_in_file(target_addon_xml, [
            ('SANNAME', sanitized),
            ('CLONENAME', clone_name),
            ('COMBNAME', combined_name),
        ])

        # Replace settings.xml with clone template
        clone_settings_xml = os.path.join(addon_path, 'resources', 'settings_clone.xml')
        target_settings_xml = os.path.join(clone_path, 'resources', 'settings.xml')
        shutil.copy2(clone_settings_xml, target_settings_xml)

        # Update section ID in clone settings
        _replace_in_file(target_settings_xml, [
            (f'section id="{ADDON_ID}"', f'section id="{clone_id}"'),
        ])

        # Update default.py to pass clone addon ID
        default_py = os.path.join(clone_path, 'default.py')
        with open(default_py, 'w', encoding='utf-8') as f:
            f.write(f'from resources.lib.ui.main import main\n\nmain(addon_id="{clone_id}")\n')

        # Remove clone-specific files from the clone
        for remove_file in ['resources/clone.py', 'resources/addon_clone.xml',
                            'resources/settings_clone.xml']:
            remove_path = os.path.join(clone_path, remove_file)
            if os.path.exists(remove_path):
                os.remove(remove_path)

        # Register the clone addon
        _register_addon(clone_id)

        log.info("Clone created", event="clone.create",
                 clone_id=clone_id, name=clone_name)
        notify(f"Clone '{clone_name}' created successfully")

    except (OSError, IOError, shutil.Error):
        log.exception("Clone creation failed", event="clone.fail",
                      clone_id=clone_id)
        notify("Clone creation failed")

        # Cleanup on failure
        if os.path.exists(clone_path):
            try:
                shutil.rmtree(clone_path)
            except OSError:
                pass


def _register_addon(addon_id: str) -> None:
    """Register a new addon with Kodi by disable/enable cycle."""
    try:
        xbmc.executeJSONRPC(json.dumps({
            "jsonrpc": "2.0",
            "method": "Addons.SetAddonEnabled",
            "id": 1,
            "params": {"addonid": addon_id, "enabled": False}
        }))
        xbmc.sleep(500)
        xbmc.executeJSONRPC(json.dumps({
            "jsonrpc": "2.0",
            "method": "Addons.SetAddonEnabled",
            "id": 1,
            "params": {"addonid": addon_id, "enabled": True}
        }))
    except Exception:
        log.exception("Failed to register clone addon",
                      event="clone.fail", addon_id=addon_id)


if __name__ == '__main__':
    create_clone()

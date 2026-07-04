"""
Skin-adaptive fonts for EasyMovie custom dialogs.

Kodi resolves a control's <font> against the active skin's font set only, with a
hard fallback to font13; addons cannot ship or register their own fonts for a
WindowXMLDialog. This module adapts our dialogs to the active skin: it parses the
skin's Font.xml, maps our anchor font names to the nearest-size font the skin
actually defines, writes font-substituted copies of the dialog XML into
addon_data, and returns a scriptPath the dialogs load from. Any failure falls
back to the shipped addon path (dialogs then render as before).

Logging:
    Logger: 'ui'
    Key events:
        - skinfont.generate (INFO): Generated adapted XML for a skin
        - skinfont.fallback (WARNING): Generation failed; using shipped path
    See LOGGING.md for full guidelines.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Dict

from resources.lib.utils import get_logger

log = get_logger('ui')

# Generated dialog XML embeds mapped font NAMES (from the skin Font.xml) as
# <font>NAME</font> via plain text substitution, so a name MUST be free of any
# XML metacharacter. Allowlist at parse time: a hostile or metacharacter-bearing
# name is dropped (never mapped), which both blocks markup/action injection and
# guarantees the generated XML stays well-formed (so the fallback invariant holds).
_VALID_FONT_NAME = re.compile(r"^[A-Za-z0-9_.]{1,64}$")  # bounded length: a
# multi-KB font name would be spliced into every <font> occurrence (font10 is
# used 48x), amplifying the generated tree to tens of MB from a sub-cap input.
# Real skin fontsets are a few KB; cap input to avoid a flat-XML resource bomb.
_MAX_FONT_XML_BYTES = 512 * 1024

# Anchor font names used in the dialog XML, keyed to their Estuary sizes (the
# target sizes we designed against).
ANCHOR_SIZES: Dict[str, int] = {
    "font36_title": 36,
    "font13": 30,
    "font12": 25,
    "font10": 23,
}


def parse_fontset(font_xml_text: str, fontset_id: str = "Default") -> Dict[str, int]:
    """Parse a skin Font.xml into {font_name: size} for the given fontset.

    Falls back to the first fontset if `fontset_id` is absent. Fonts without a
    positive integer size are skipped. Returns {} on any parse error.

    Security (input is a third-party skin's Font.xml):
    - Reject input over `_MAX_FONT_XML_BYTES` (flat-XML resource bomb).
    - Reject any DOCTYPE/ENTITY declaration (billion-laughs); stdlib ElementTree
      already does not resolve external entities (XXE) on Python 3.7.1+.
    - Allowlist font names to `_VALID_FONT_NAME`; a name carrying any XML
      metacharacter is dropped, so the downstream text substitution can neither
      be injected nor produce malformed XML (no defusedxml dependency needed).
    """
    if len(font_xml_text) > _MAX_FONT_XML_BYTES:
        return {}
    lowered = font_xml_text.lower()
    if "<!doctype" in lowered or "<!entity" in lowered:
        return {}
    try:
        root = ET.fromstring(font_xml_text)
    except ET.ParseError:
        return {}
    fontsets = root.findall("fontset")
    chosen = None
    for fs in fontsets:
        if fs.get("id") == fontset_id:
            chosen = fs
            break
    if chosen is None and fontsets:
        chosen = fontsets[0]
    if chosen is None:
        return {}
    result: Dict[str, int] = {}
    for font in chosen.findall("font"):
        name_el = font.find("name")
        size_el = font.find("size")
        if name_el is None or size_el is None:
            continue
        name = (name_el.text or "").strip()
        try:
            size = int((size_el.text or "").strip())
        except ValueError:
            continue
        if name and size > 0 and _VALID_FONT_NAME.match(name):
            result[name] = size
    return result


def build_font_map(skin_fonts: Dict[str, int],
                   anchors: Dict[str, int] = ANCHOR_SIZES) -> Dict[str, str]:
    """Map each anchor font name to the skin font whose size is nearest.

    If the skin defines the anchor name itself, it maps to itself. If the skin
    provides no usable fonts, every anchor maps to itself (identity), so the
    shipped names are kept and Kodi's own fallback applies.
    """
    font_map: Dict[str, str] = {}
    for anchor, target in anchors.items():
        if anchor in skin_fonts:
            font_map[anchor] = anchor
            continue
        if not skin_fonts:
            font_map[anchor] = anchor
            continue
        # Nearest by absolute size difference; ties break to the smaller size
        # then the name, for determinism.
        best = min(skin_fonts.items(),
                   key=lambda kv: (abs(kv[1] - target), kv[1], kv[0]))
        font_map[anchor] = best[0]
    return font_map


def substitute_fonts(xml_text: str, font_map: Dict[str, str]) -> str:
    """Replace <font>ANCHOR</font> with <font>MAPPED</font> for each anchor."""
    out = xml_text
    for anchor, mapped in font_map.items():
        if anchor != mapped:
            out = out.replace("<font>%s</font>" % anchor,
                              "<font>%s</font>" % mapped)
    return out


def cache_key(skin_id: str, skin_version: str, fontset: str,
              addon_version: str, font_mtime: int) -> str:
    """Stable identity for a generated set (invalidates on any component change).

    Includes the skin Font.xml mtime so a hand-edited or forked skin font file
    invalidates the cache without a per-open full content hash (TRADEOFF-1).
    """
    return "%s@%s|%s|addon@%s|font@%d" % (
        skin_id, skin_version, fontset, addon_version, font_mtime)

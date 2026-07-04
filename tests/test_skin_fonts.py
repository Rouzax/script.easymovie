"""Tests for skin-adaptive font mapping."""
from resources.lib.ui.skin_fonts import ANCHOR_SIZES, parse_fontset

_SAMPLE = """<?xml version="1.0"?>
<fonts>
  <fontset id="Default" unicode="true">
    <font><name>font10</name><filename>a.ttf</filename><size>23</size></font>
    <font><name>Mini</name><filename>a.ttf</filename><size>24</size></font>
    <font><name>LargeNew</name><filename>b.ttf</filename><style>bold</style><size>44</size></font>
    <font><name>Null</name><filename>a.ttf</filename><size>0</size></font>
    <font><name>NoSize</name><filename>a.ttf</filename></font>
  </fontset>
  <fontset id="Other"><font><name>x</name><size>99</size></font></fontset>
</fonts>"""


def test_anchor_sizes():
    assert ANCHOR_SIZES == {"font36_title": 36, "font13": 30, "font12": 25, "font10": 23}


def test_parse_default_fontset():
    fonts = parse_fontset(_SAMPLE, "Default")
    assert fonts == {"font10": 23, "Mini": 24, "LargeNew": 44}


def test_parse_skips_zero_and_missing_size():
    fonts = parse_fontset(_SAMPLE, "Default")
    assert "Null" not in fonts and "NoSize" not in fonts


def test_parse_named_fontset():
    assert parse_fontset(_SAMPLE, "Other") == {"x": 99}


def test_parse_unknown_fontset_falls_back_to_first():
    assert parse_fontset(_SAMPLE, "Missing") == {"font10": 23, "Mini": 24, "LargeNew": 44}


def test_parse_garbage_returns_empty():
    assert parse_fontset("not xml", "Default") == {}


def test_parse_rejects_doctype_entity():
    # A malicious skin could craft a Font.xml with entity-expansion (billion
    # laughs). Legitimate font files never declare a DOCTYPE/ENTITY; reject them.
    hostile = ('<?xml version="1.0"?><!DOCTYPE fonts [<!ENTITY a "aaaa">]>'
               '<fonts><fontset id="Default"><font><name>font10</name>'
               '<size>23</size></font></fontset></fonts>')
    assert parse_fontset(hostile, "Default") == {}


def test_parse_drops_font_names_with_metacharacters():
    # A crafted font name that would inject markup if substituted unescaped.
    # It parses as valid XML (entity-encoded), so ET.fromstring succeeds; the
    # allowlist must drop it so it can never reach the generated dialog XML.
    injected = ('<fonts><fontset id="Default">'
                '<font><name>x&lt;/font&gt;&lt;onclick&gt;RunScript(evil)'
                '&lt;/onclick&gt;&lt;font&gt;</name><size>36</size></font>'
                '<font><name>font10</name><size>23</size></font>'
                '</fontset></fonts>')
    assert parse_fontset(injected, "Default") == {"font10": 23}


def test_parse_rejects_oversized_input():
    bomb = "<fonts><fontset id='Default'>" + ("<font><name>a</name><size>1</size></font>" * 100000)
    assert len(bomb) > 512 * 1024
    assert parse_fontset(bomb, "Default") == {}


def test_shipped_templates_only_use_anchor_fonts():
    # Guards ANCHOR_SIZES <-> template drift: substitute_fonts only remaps exact
    # anchor names, so a template introducing a new/misspelled <font> would
    # silently never adapt. Run from the repo root.
    import glob
    import re as _re
    used = set()
    files = glob.glob("resources/skins/Default/1080i/*.xml")
    assert files, "no shipped dialog XML found"
    for path in files:
        with open(path, "r", encoding="utf-8") as fh:
            used |= set(_re.findall(r"<font>([^<]+)</font>", fh.read()))
    assert used <= set(ANCHOR_SIZES), (
        "templates use non-anchor fonts: %s" % (used - set(ANCHOR_SIZES)))

"""Tests for skin-adaptive font mapping."""
import resources.lib.ui.info_dialog as idlg
import resources.lib.ui.skin_fonts as sf
from resources.lib.ui.skin_fonts import (
    ANCHOR_SIZES,
    build_font_map,
    cache_key,
    parse_fontset,
    substitute_fonts,
)

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


def test_build_font_map_identity_when_anchor_present():
    # A skin that defines our anchor names maps each to itself.
    skin = {"font36_title": 36, "font13": 30, "font12": 25, "font10": 23}
    assert build_font_map(skin) == {
        "font36_title": "font36_title", "font13": "font13",
        "font12": "font12", "font10": "font10"}


def test_build_font_map_nearest_size():
    # Arctic-like: only font13 numbered, plus its own named fonts.
    skin = {"font13": 30, "Mini": 24, "Small20": 17, "LargeNew": 44, "Large": 38}
    m = build_font_map(skin)
    assert m["font36_title"] == "Large"    # 36 -> 38 (nearest, beats 44)
    assert m["font13"] == "font13"          # 30 -> 30 exact
    assert m["font12"] == "Mini"            # 25 -> 24 (nearest, beats 30)
    assert m["font10"] == "Mini"            # 23 -> 24 (nearest, beats 17)


def test_build_font_map_empty_skin_is_identity():
    assert build_font_map({}) == {
        "font36_title": "font36_title", "font13": "font13",
        "font12": "font12", "font10": "font10"}


def test_substitute_fonts_replaces_anchor_tags():
    xml = "<font>font36_title</font> x <font>font10</font> <font>font10</font>"
    out = substitute_fonts(xml, {"font36_title": "Large", "font10": "Mini"})
    assert out == "<font>Large</font> x <font>Mini</font> <font>Mini</font>"


def test_substitute_fonts_identity_leaves_text_unchanged():
    xml = "<font>font10</font>"
    assert substitute_fonts(xml, {"font10": "font10"}) == xml


def test_cache_key_stable_and_sensitive():
    a = cache_key("skin.x", "1.0", "Default", "2.0", 1000)
    assert a == cache_key("skin.x", "1.0", "Default", "2.0", 1000)
    assert a != cache_key("skin.x", "1.1", "Default", "2.0", 1000)
    assert a != cache_key("skin.y", "1.0", "Default", "2.0", 1000)
    assert a != cache_key("skin.x", "1.0", "Default", "2.0", 1001)  # Font.xml edited


def test_generate_into_writes_substituted_xml(tmp_path):
    # Arrange a fake shipped addon tree.
    ship = tmp_path / "addon"
    res = ship / "resources" / "skins" / "Default"
    (res / "1080i").mkdir(parents=True)
    (res / "media" / "common").mkdir(parents=True)
    (res / "1080i" / "script-easymovie-info.xml").write_text(
        "<window><control><font>font36_title</font></control></window>")
    (res / "media" / "common" / "white.png").write_text("PNG")

    out = tmp_path / "gen"
    font_map = {"font36_title": "LargeNew"}
    sf._generate_into(str(ship), str(out), font_map)

    gen_xml = out / "resources" / "skins" / "Default" / "1080i" / "script-easymovie-info.xml"
    assert "<font>LargeNew</font>" in gen_xml.read_text()
    # media copied
    assert (out / "resources" / "skins" / "Default" / "media" / "common" / "white.png").exists()


def test_ensure_generated_falls_back_on_error(monkeypatch):
    # A failure mid-generation returns the shipped path, never raises.
    monkeypatch.setattr(sf, "_safe_shipped", lambda addon_id: "/ship/path")
    monkeypatch.setattr(sf, "_active_skin", lambda: (_ for _ in ()).throw(OSError("no skin")))
    assert sf.ensure_generated("script.easymovie") == "/ship/path"


def test_ensure_generated_fallback_never_raises(monkeypatch):
    # Even if xbmcaddon.Addon() itself raises (malformed/unregistered id), the
    # caller gets a string, never an exception (the "never break a dialog"
    # invariant, which the fallback path must not itself violate).
    monkeypatch.setattr(sf.xbmcaddon, "Addon",
                        lambda addon_id: (_ for _ in ()).throw(RuntimeError("no addon")))
    monkeypatch.setattr(sf.xbmcvfs, "translatePath", lambda p: "/home/addons/x")
    assert sf.ensure_generated("script.easymovie") == "/home/addons/x"


def test_ensure_generated_rejects_bad_addon_id(monkeypatch):
    monkeypatch.setattr(sf, "_safe_shipped", lambda a: "/ship")
    assert sf.ensure_generated("../evil") == "/ship"


def test_show_info_dialog_uses_generated_scriptpath(monkeypatch):
    captured = {}

    class _FakeDialog:
        def __init__(self, xml, path, skin, res):
            captured["path"] = path
        def __setattr__(self, k, v):
            object.__setattr__(self, k, v)
        def doModal(self):
            pass
        result = None

    monkeypatch.setattr(idlg, "InfoDialog", _FakeDialog)
    monkeypatch.setattr(idlg, "ensure_generated", lambda addon_id: "/gen/base")
    idlg.show_info_dialog({"movieid": 1}, {"title": "T"}, "script.easymovie")
    assert captured["path"] == "/gen/base"

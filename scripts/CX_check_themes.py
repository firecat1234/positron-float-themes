"""Validate the shipped theme collection, contrast, and optional VSIX contents."""

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

from CX_build_themes import ROOT, PALETTES, contrast, composite

manifest = json.loads((ROOT / "package.json").read_text())
entries = manifest["contributes"]["themes"]
assert len(entries) == 12
assert len({e["label"] for e in entries}) == 12
assert len({e["path"] for e in entries}) == 12
assert manifest["name"] == "float-spring-positron-theme", "Keep the installed extension identity."
assert manifest["repository"]["url"] == "https://github.com/firecat1234/positron-float-themes.git"
assert "main" not in manifest and "activationEvents" not in manifest
assert {p["id"] for p in PALETTES} == {"spring", "blossom", "ash", "cappucino", "sunset-citrus", "midnight-plum"}

SPRING_HASHES = {
    "Float Spring": "ba75c980d8f7e43b63432d24518f92f1c22914fc7a25edb82347193e0c013c84",
    "Float Spring Night": "fba4af50d702da6858461a355d4f3e7578f030bbc38f600357ad48c6252730eb",
}

PAIRS = [
    ("editor.foreground", "editor.background"),
    ("sideBar.foreground", "sideBar.background"),
    ("sideBarTitle.foreground", "sideBar.background"),
    ("sideBarSectionHeader.foreground", "sideBarSectionHeader.background"),
    ("titleBar.activeForeground", "titleBar.activeBackground"),
    ("titleBar.inactiveForeground", "titleBar.inactiveBackground"),
    ("activityBar.foreground", "activityBar.background"),
    ("activityBarBadge.foreground", "activityBarBadge.background"),
    ("badge.foreground", "badge.background"),
    ("button.foreground", "button.background"),
    ("button.foreground", "button.hoverBackground"),
    ("button.secondaryForeground", "button.secondaryBackground"),
    ("button.secondaryForeground", "button.secondaryHoverBackground"),
    ("input.foreground", "input.background"),
    ("input.placeholderForeground", "input.background"),
    ("list.activeSelectionForeground", "list.activeSelectionBackground"),
    ("list.inactiveSelectionForeground", "list.inactiveSelectionBackground"),
    ("list.hoverForeground", "list.hoverBackground"),
    ("tab.activeForeground", "tab.activeBackground"),
    ("tab.inactiveForeground", "tab.inactiveBackground"),
    ("statusBar.foreground", "statusBar.background"),
    ("statusBar.debuggingForeground", "statusBar.debuggingBackground"),
    ("positronModalDialog.foreground", "positronModalDialog.background"),
    ("positronModalDialog.defaultButtonForeground", "positronModalDialog.defaultButtonBackground"),
    ("positronModalDialog.defaultButtonForeground", "positronModalDialog.defaultButtonHoverBackground"),
    ("positronConsole.foreground", "positronConsole.background"),
    ("positronConsole.errorForeground", "positronConsole.errorBackground"),
    ("positronDataExplorer.foreground", "positronDataExplorer.background"),
    ("positronVariables.foreground", "positronVariables.background"),
    ("positronVariables.activeSelectionForeground", "positronVariables.activeSelectionBackground"),
    ("positronVariables.inactiveSelectionForeground", "positronVariables.inactiveSelectionBackground"),
    ("positronPackages.foreground", "positronPackages.background"),
]

checked_contrasts = 0
for entry in entries:
    path = ROOT / entry["path"]
    theme = json.loads(path.read_text())
    colours = theme["colors"]
    night = entry["uiTheme"] == "vs-dark"
    assert theme["name"] == entry["label"]
    assert theme["type"] == ("dark" if night else "light")
    reference = json.loads((ROOT / ("themes/float-spring-night-color-theme.json" if night else "themes/float-spring-color-theme.json")).read_text())
    assert set(colours) == set(reference["colors"])
    assert len(colours) == 337
    assert len(theme["tokenColors"]) == 15
    assert set(theme["semanticTokenColors"]) == set(reference["semanticTokenColors"])
    assert [r["scope"] for r in theme["tokenColors"]] == [r["scope"] for r in reference["tokenColors"]]
    assert all(re.fullmatch(r"#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?", c) for c in colours.values())
    assert theme["semanticHighlighting"] is True
    if theme["name"] in SPRING_HASHES:
        assert hashlib.sha256(json.dumps(theme, sort_keys=True).encode()).hexdigest() == SPRING_HASHES[theme["name"]]
        continue
    palette = next(p for p in PALETTES if entry["label"] in ("Float " + p["label"], "Float " + p["label"] + " Night"))
    expected_background = "#ffffff" if palette["id"] == "blossom" and not night else palette["slots"]["veryDark" if night else "veryLight"]
    assert colours["editor.background"] == expected_background
    if palette["id"] == "blossom" and not night:
        assert colours["titleBar.activeBackground"] == "#f8def6", "Blossom uses a pale pink header."
        assert contrast(colours["activityBar.background"], "#ffffff") < 1.2, "Keep large Blossom surfaces near white."
        assert colours["tab.activeBorderTop"] == palette["slots"]["c1Med"], "Green belongs in small details."
    for fg, bg in PAIRS:
        background = composite(colours[bg], colours["editor.background"])
        ratio = contrast(colours[fg], background)
        assert ratio >= 4.5, f"{theme['name']}: {fg} on {bg}: {ratio:.2f}:1"
        checked_contrasts += 1
    for prefix in ("terminal", "positronConsole"):
        for key, colour in colours.items():
            if key.startswith(prefix + ".ansi"):
                assert contrast(colour, colours[prefix + ".background"]) >= 4.5, (theme["name"], key)
                checked_contrasts += 1
    syntax = [r["settings"]["foreground"] for r in theme["tokenColors"]]
    syntax += [r if isinstance(r, str) else r["foreground"] for r in theme["semanticTokenColors"].values()]
    for colour in syntax:
        assert contrast(colour, colours["editor.background"]) >= 4.5, (theme["name"], colour)
        checked_contrasts += 1
    # A cherry/orange accent must not turn successful output or additions red.
    assert colours["terminal.ansiGreen"] != colours["terminal.ansiRed"]

readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
for p in PALETTES:
    assert (ROOT / "assets" / f"CX_{p['id']}.png").is_file()
    assert f"assets/CX_{p['id']}.png" in readme
    for value in p["slots"].values():
        assert value[1:].upper() in readme, "Swatches need accessible hex text."

if len(sys.argv) > 1:
    with zipfile.ZipFile(sys.argv[1]) as package:
        names = set(package.namelist())
        packed_manifest = json.loads(package.read("extension/package.json"))
        assert packed_manifest == manifest
        for entry in entries:
            name = "extension/" + entry["path"].removeprefix("./")
            assert package.read(name) == (ROOT / entry["path"]).read_bytes()
        for p in PALETTES:
            name = f"extension/assets/CX_{p['id']}.png"
            assert package.read(name) == (ROOT / "assets" / f"CX_{p['id']}.png").read_bytes()
        assert not any(n.startswith(("extension/scripts/", "extension/.git/", "extension/output/")) for n in names)
    print("VSIX contents match all 12 source themes and all 6 colour cards.")

print(f"PASS: 12 themes, 337 workbench colours each, 15 TextMate rules and 23 semantic rules each; {checked_contrasts} new-theme contrast checks; original Spring themes unchanged.")

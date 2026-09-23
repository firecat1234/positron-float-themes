"""Build Float ports and README colour cards. Requires Python 3.10+ and Pillow."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTES = json.loads((ROOT / "CX_palettes.json").read_text(encoding="utf-8"))


def rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, amount):
    return "#" + "".join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(rgb(a), rgb(b)))


def luminance(value):
    def linear(channel):
        x = channel / 255
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    return sum(weight * linear(channel) for weight, channel in zip((0.2126, 0.7152, 0.0722), rgb(value)))


def contrast(a, b):
    light, dark = sorted((luminance(a), luminance(b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def composite(foreground, background):
    return mix(background, foreground[:7], int(foreground[7:9], 16) / 255) if len(foreground) == 9 else foreground


def readable(foreground, background, minimum=4.5):
    """Keep the hue where possible, adjusting only colours that need contrast."""
    foreground = composite(foreground, background)
    if contrast(foreground, background) >= minimum:
        return foreground
    endpoint = max(("#000000", "#ffffff"), key=lambda c: contrast(c, background))
    for step in range(1, 101):
        candidate = mix(foreground, endpoint, step / 100)
        if contrast(candidate, background) >= minimum:
            return candidate
    return endpoint


# The existing Spring themes define complete Positron workbench coverage.
# Map their surface roles explicitly; fail if a new, unmapped colour is added.
def colour_map(s, night):
    light, dark = s["veryLight"], s["veryDark"]
    primary, accent = s["c1Med"], s["c2Med"]
    p_light, p_dark = s["c1Light"], s["c1Dark"]
    a_light, a_dark = s["c2Light"], s["c2Dark"]
    bg = dark if night else light
    result = {
        "#ffffff": light, "#090d17": dark,
        "#630ac3": primary, "#340865": p_dark,
        "#21b228": accent, "#166d2a": a_dark,
        "#86eaa0": a_light, "#e4d9f3": p_light,
        "#0d551e": mix(a_dark, dark, 0.25),
        "#b29ed9": mix(p_light, primary, 0.3),
        "#f2eef7": mix(light, p_light, 0.35),
    }
    if night:
        result.update({
            "#000000": "#000000", "#0b1120": mix(dark, p_dark, 0.15),
            "#0e1422": mix(dark, p_light, 0.035), "#100d1c": mix(dark, p_dark, 0.23),
            "#151125": mix(dark, p_light, 0.065), "#160a2c": mix(dark, p_dark, 0.55),
            "#201139": mix(dark, primary, 0.2), "#21182f": mix(dark, p_light, 0.10),
            "#240947": mix(dark, p_dark, 0.7), "#2b213c": mix(dark, p_light, 0.15),
            "#34224d": mix(dark, primary, 0.30), "#342b43": mix(dark, p_light, 0.19),
            "#3a2b4d": mix(dark, p_light, 0.23), "#4b3761": mix(dark, p_light, 0.30),
            "#5e4a74": mix(dark, p_light, 0.38), "#665b72": mix(dark, p_light, 0.40),
            "#6b527e": mix(dark, p_light, 0.45), "#83798f": mix(dark, p_light, 0.55),
            "#9b8daa": mix(dark, p_light, 0.65), "#a99bb7": mix(dark, p_light, 0.72),
            "#b9aec7": mix(dark, p_light, 0.8), "#d4c8dc": mix(light, p_light, 0.55),
            "#78cd8d": readable(mix(a_light, accent, 0.20), bg),
            "#7d21d4": mix(primary, p_light, 0.15),
            "#8d70e0": readable(mix(primary, p_light, 0.40), bg),
            "#ad94f0": readable(mix(primary, p_light, 0.65), bg),
            "#c3aceb": readable(mix(primary, p_light, 0.75), bg),
            "#b9f5c8": mix(a_light, light, 0.4), "#d8c2ff": mix(p_light, light, 0.2),
            "#35141d": mix(dark, "#b42332", 0.22), "#332814": mix(dark, "#9a6700", 0.22),
        })
        fixed = ("#5cd6c2", "#83e4d5", "#e0aa45", "#f0c36a", "#f39a5b", "#ff6575", "#ff7b88", "#ff8b96")
    else:
        result.update({
            "#390892": readable(mix(primary, p_dark, 0.55), bg),
            "#4e0899": readable(mix(primary, p_dark, 0.3), bg),
            "#4d1684": mix(primary, p_dark, 0.4),
            "#147a32": readable(accent, bg),
            "#564e63": mix(dark, p_dark, 0.38), "#625a6c": mix(dark, light, 0.35),
            "#695073": readable(mix(p_dark, light, 0.32), bg),
            "#6c6376": mix(dark, light, 0.40), "#766e80": mix(dark, light, 0.44),
            "#988ca5": mix(dark, light, 0.53),
            "#6245bd": readable(mix(primary, p_light, 0.23), bg),
            "#8a36d8": readable(mix(primary, p_light, 0.30), bg),
            "#d1c0e6": mix(light, p_light, 0.80), "#d7c6ec": mix(light, p_light, 0.70),
            "#d8cbe8": mix(light, p_light, 0.75), "#eee9f3": mix(light, p_light, 0.45),
            "#f8f5fb": mix(light, p_light, 0.20), "#fbf9fe": mix(light, p_light, 0.10),
            "#fff0f1": mix(light, "#b42332", 0.065), "#fff8d8": mix(light, "#e0aa45", 0.12),
        })
        fixed = ("#087b71", "#0b9f90", "#8a5b00", "#9a6700", "#b42332", "#b67a00", "#b85d00", "#d23b49")
    result.update({colour: colour for colour in fixed})
    return result


def transform(value, mapping):
    if isinstance(value, dict):
        return {key: transform(item, mapping) for key, item in value.items()}
    if isinstance(value, list):
        return [transform(item, mapping) for item in value]
    if isinstance(value, str) and value.startswith("#"):
        return mapping[value[:7]] + value[7:]
    return value


def text_background(key, colours):
    """Resolve explicit foregrounds to their workbench surface for contrast QA."""
    direct = key.replace("Foreground", "Background").replace("foreground", "background")
    if direct != key and direct in colours:
        return colours[direct]
    if key.startswith("statusBarItem."):
        return colours["statusBar.background"]
    if key.startswith("input.placeholder"):
        return colours["input.background"]
    if key.startswith("tab."):
        return colours["tab.inactiveBackground"]
    prefix = key.split(".")[0]
    if prefix.startswith("editor"):
        return colours["editor.background"]
    if prefix == "sideBarTitle":
        return colours["sideBar.background"]
    if prefix == "panelTitle":
        return colours["panel.background"]
    if prefix == "commandCenter":
        return colours["titleBar.activeBackground"]
    if prefix == "list":
        return colours["sideBar.background"]
    return colours.get(prefix + ".background", colours["editor.background"])


def build_theme(palette, night):
    suffix = "-night" if night else ""
    template = json.loads((ROOT / f"themes/float-spring{suffix}-color-theme.json").read_text())
    slots = palette["slots"]
    if palette["id"] == "blossom":
        # Float's built-in Blossom legacy palette deliberately reverses the
        # structural/accent families: pink glass/chrome, green details.
        # App.css then dilutes those colours over almost-white glass surfaces.
        slots = {
            "c1Light": slots["c2Med"], "c1Med": slots["c2Dark"], "c1Dark": "#8f2967",
            "c2Light": slots["c1Light"], "c2Med": slots["c1Med"], "c2Dark": slots["c1Dark"],
            "veryLight": "#ffffff", "veryDark": slots["veryDark"],
        }
    theme = transform(template, colour_map(slots, night))
    theme["name"] = "Float " + palette["label"] + (" Night" if night else "")
    colours = theme["colors"]
    if palette["id"] == "blossom":
        if night:
            colours.update({
                "activityBar.background": "#26333a", "activityBar.foreground": "#a8f5ab",
                "titleBar.activeBackground": "#453544", "titleBar.inactiveBackground": "#34313b",
                "sideBar.background": "#223139", "sideBarSectionHeader.background": "#303b43",
                "statusBar.background": "#243c32", "statusBar.foreground": "#a8f5ab",
            })
        else:
            # Match Float's rendered proportions, not solid blocks of its raw
            # neon-green slot or the darker magenta used for small controls.
            colours.update({
                "editor.background": "#ffffff", "editor.foreground": "#24333d",
                "activityBar.background": "#fbf7fb", "activityBar.foreground": "#308047",
                "activityBar.inactiveForeground": "#738278", "activityBar.border": "#e8e3e8",
                "titleBar.activeBackground": "#f8def6", "titleBar.activeForeground": "#24333d",
                "titleBar.inactiveBackground": "#fbecfa", "titleBar.inactiveForeground": "#58665d",
                "titleBar.border": "#e5cce1", "sideBar.background": "#fcfafc",
                "sideBar.foreground": "#24333d", "sideBarTitle.foreground": "#52695a",
                "sideBarSectionHeader.background": "#f9eef8", "sideBarSectionHeader.foreground": "#52695a",
                "panel.background": "#fbfcfc", "terminal.background": "#fbfcfc",
                "positronConsole.background": "#fbfcfc", "statusBar.background": "#a8f5ab",
                "statusBar.noFolderBackground": "#a8f5ab",
                "statusBar.foreground": "#05420f", "statusBar.border": "#d9eadc",
                "button.background": "#f7bff3", "button.foreground": "#05420f",
                "button.hoverBackground": "#f3aeed", "button.secondaryBackground": "#f1f8f2",
                "button.secondaryForeground": "#28723d", "button.secondaryHoverBackground": "#e2f3e5",
                "list.activeSelectionBackground": "#f8def6", "list.activeSelectionForeground": "#24333d",
                "positronVariables.activeSelectionBackground": "#f8def6",
                "positronVariables.activeSelectionForeground": "#24333d",
                "positronActionBar.background": "#f9f5f9", "positronActionBar.foreground": "#52695a",
                "positronModalDialog.titleBarBackground": "#f8def6",
                "positronModalDialog.titleBarForeground": "#24333d",
                "positronModalDialog.defaultButtonBackground": "#f7bff3",
                "positronModalDialog.defaultButtonForeground": "#05420f",
                "positronModalDialog.defaultButtonHoverBackground": "#f3aeed",
                "editorGroupHeader.tabsBackground": "#fcfafc", "tab.inactiveBackground": "#fcfafc",
                "tab.activeForeground": "#24333d", "tab.inactiveForeground": "#657268",
                "tab.activeBorderTop": "#4aed1d", "activityBar.activeBorder": "#4aed1d",
                "panelTitle.activeBorder": "#4aed1d", "focusBorder": "#308047",
                "editorCursor.foreground": "#308047", "editorLineNumber.activeForeground": "#308047",
                "editor.lineHighlightBackground": "#fdf9fc", "icon.foreground": "#308047",
                "textLink.foreground": "#28723d", "textLink.activeForeground": "#05420f",
                "commandCenter.foreground": "#24333d", "commandCenter.border": "#d5c5d3",
            })
            # Most text stays slate; pink and green provide distinct code cues.
            syntax = ["#657b71", "#8f2967", "#28723d", "#8b557f", "#52695a", "#76536d",
                      "#24333d", "#657268", "#8f2967", "#28723d", "#76536d", "#76536d",
                      "#28723d", "#8b557f", "#b42332"]
            for rule, colour in zip(theme["tokenColors"], syntax):
                rule["settings"]["foreground"] = colour
            semantic = {
                "namespace": "#8b557f", "type": "#76536d", "class": "#76536d", "enum": "#76536d",
                "interface": "#76536d", "struct": "#76536d", "typeParameter": "#8f2967",
                "function": "#52695a", "method": "#52695a", "macro": "#8f2967", "variable": "#24333d",
                "variable.readonly": "#8b557f", "parameter": "#657268", "property": "#28723d",
                "enumMember": "#8b557f", "event": "#8f2967", "keyword": "#8f2967", "modifier": "#8f2967",
                "comment": "#657b71", "string": "#28723d", "number": "#8b557f", "regexp": "#28723d", "operator": "#8f2967",
            }
            for key, colour in semantic.items():
                if isinstance(theme["semanticTokenColors"][key], str):
                    theme["semanticTokenColors"][key] = colour
                else:
                    theme["semanticTokenColors"][key]["foreground"] = colour
    # Preserve familiar success/error semantics even in orange or cherry palettes.
    green, green_bright = ("#6fce96", "#9fe8b8") if night else ("#166d2a", "#26823d")
    for prefix in ("terminal", "positronConsole"):
        colours[prefix + ".ansiGreen"] = green
        colours[prefix + ".ansiBrightGreen"] = green_bright
    for key in ("gitDecoration.addedResourceForeground", "gitDecoration.untrackedResourceForeground", "editorGutter.addedBackground", "positronRuntime.stateIconActive", "charts.green"):
        colours[key] = green
    colours["diffEditor.insertedTextBackground"] = green + "33"
    for key, value in colours.items():
        if key.lower().endswith("foreground") or ".ansi" in key:
            background = text_background(key, colours)
            parent = colours["titleBar.activeBackground"] if key.startswith("commandCenter.") else colours["editor.background"]
            background = composite(background, parent)
            colours[key] = readable(value, background)
    # A button keeps its label colour while hovered: verify both states together.
    for prefix in ("button", "positronModalDialog.defaultButton"):
        fg_key = prefix + (".foreground" if prefix == "button" else "Foreground")
        bg_key = prefix + (".background" if prefix == "button" else "Background")
        hover_key = prefix + (".hoverBackground" if prefix == "button" else "HoverBackground")
        colours[fg_key] = max(("#000000", "#ffffff"), key=lambda ink: contrast(ink, colours[bg_key]))
        colours[hover_key] = readable(colours[hover_key], colours[fg_key])
    for rule in theme["tokenColors"]:
        rule["settings"]["foreground"] = readable(rule["settings"]["foreground"], colours["editor.background"])
    for key, value in theme["semanticTokenColors"].items():
        if isinstance(value, str):
            theme["semanticTokenColors"][key] = readable(value, colours["editor.background"])
        else:
            value["foreground"] = readable(value["foreground"], colours["editor.background"])
    return theme


def font(size, bold=False, mono=False):
    from PIL import ImageFont
    names = (["DejaVuSansMono.ttf", "C:/Windows/Fonts/consola.ttf"] if mono else
             ["DejaVuSans-Bold.ttf", "C:/Windows/Fonts/segoeuib.ttf"] if bold else
             ["DejaVuSans.ttf", "C:/Windows/Fonts/segoeui.ttf"])
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    raise RuntimeError("Install DejaVu Sans fonts to render the palette cards.")


def render_card(palette, themes):
    from PIL import Image, ImageDraw
    # Two workbench illustrations above exact, unmodified source-slot swatches.
    image = Image.new("RGB", (1120, 608), "#f8f7fa")
    draw = ImageDraw.Draw(image)
    draw.text((24, 14), "FLOAT / " + palette["label"].upper(), font=font(24, bold=True), fill="#24212c")
    draw.text((24, 49), "Light + Night  |  Workbench colour illustrations", font=font(17), fill="#615b6b")
    for index, theme in enumerate(themes):
        c = theme["colors"]
        x, y, width = 24 + index * 548, 82, 524
        draw.rounded_rectangle((x, y, x + width, y + 252), radius=10, fill=c["editor.background"])
        draw.rectangle((x, y, x + width, y + 31), fill=c["titleBar.activeBackground"])
        draw.text((x + 12, y + 5), theme["name"], font=font(16), fill=c["titleBar.activeForeground"])
        draw.rectangle((x, y + 32, x + 35, y + 230), fill=c["activityBar.background"])
        draw.rectangle((x + 36, y + 32, x + 126, y + 230), fill=c["sideBar.background"])
        draw.text((x + 45, y + 47), "FILES", font=font(13, bold=True), fill=c["sideBar.foreground"])
        draw.text((x + 45, y + 75), "notes.py", font=font(12), fill=c["sideBar.foreground"])
        draw.text((x + 141, y + 48), "# room to think", font=font(17, mono=True), fill=theme["tokenColors"][0]["settings"]["foreground"])
        for row, (text, scope) in enumerate((("import pandas as pd", 1), ("palette = '" + palette["id"] + "'", 2), ("values = [1, 2, 3]", 3), ("print(values)", 4))):
            draw.text((x + 141, y + 79 + row * 25), text, font=font(17, mono=True), fill=theme["tokenColors"][scope]["settings"]["foreground"])
        draw.rectangle((x + 127, y + 193, x + width, y + 230), fill=c["positronConsole.background"])
        draw.text((x + 141, y + 201), ">>> [1, 2, 3]", font=font(16, mono=True), fill=c["positronConsole.foreground"])
        draw.rectangle((x, y + 231, x + width, y + 252), fill=c["statusBar.background"])
        draw.text((x + 12, y + 232), "Python  |  UTF-8", font=font(12), fill=c["statusBar.foreground"])
    labels = (("c1Light", "Primary / light"), ("c1Med", "Primary / medium"), ("c1Dark", "Primary / dark"), ("veryLight", "Light surface"),
              ("c2Light", "Accent / light"), ("c2Med", "Accent / medium"), ("c2Dark", "Accent / dark"), ("veryDark", "Dark surface"))
    for index, (key, label) in enumerate(labels):
        x, y = 24 + (index % 4) * 274, 354 + (index // 4) * 118
        colour = palette["slots"][key]
        ink = max(("#000000", "#ffffff"), key=lambda c: contrast(c, colour))
        draw.rounded_rectangle((x, y, x + 250, y + 99), radius=9, fill=colour, outline=mix(colour, ink, 0.18))
        draw.text((x + 16, y + 12), label, font=font(16), fill=ink)
        draw.text((x + 16, y + 41), colour.upper(), font=font(28, mono=True), fill=ink)
    output = ROOT / "assets" / f"CX_{palette['id']}.png"
    image.save(output, optimize=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cards", action="store_true", help="Also regenerate PNG colour cards (requires Pillow).")
    args = parser.parse_args()
    for palette in PALETTES:
        themes = []
        for night in (False, True):
            suffix = "-night" if night else ""
            path = ROOT / f"themes/float-{palette['id']}{suffix}-color-theme.json"
            # Keep both released Spring themes byte-for-byte unchanged.
            if palette["id"] == "spring":
                theme = json.loads(path.read_text())
            else:
                theme = build_theme(palette, night)
                path.write_text(json.dumps(theme, indent=2) + "\n", encoding="utf-8")
            themes.append(theme)
        if args.cards:
            render_card(palette, themes)
    print("Built 10 new themes; retained the 2 original Spring themes." + (" Rendered 6 colour cards." if args.cards else ""))


if __name__ == "__main__":
    main()

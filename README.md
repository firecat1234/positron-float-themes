# Float Spring for Positron

A Positron theme based directly on Float's built-in `spring` palette.

It carries Float's palette into the full data-science workbench, including the editor, terminal, Console, Variables, Data Explorer, Plots, Packages, notebooks, dialogs, and selection states.

## Install

1. Download `float-spring-positron-theme-0.1.0.vsix` from the [latest release](https://github.com/firecat1234/positron-float-spring-theme/releases/latest).
2. In Positron, run **Extensions: Install from VSIX...** from the Command Palette and choose the downloaded file.
3. Run **Preferences: Color Theme** and select **Float Spring** or **Float Spring Night**.

From a terminal, the first two steps can also be completed with:

```powershell
positron --install-extension .\float-spring-positron-theme-0.1.0.vsix
```

## Themes

- **Float Spring** — bright white and soft-lavender surfaces with deep purple structure and pear-green accents.
- **Float Spring Night** — near-black/petrol surfaces with lavender syntax, purple structure, and mint/pear accents.

## Source palette

| Role | Color |
| --- | --- |
| Lavender | `#e4d9f3` |
| Purple | `#630ac3` |
| Deep purple | `#340865` |
| Mint green | `#86eaa0` |
| Pear green | `#21b228` |
| Deep green | `#166d2a` |
| Soft white | `#f2eef7` |
| Near black | `#090d17` |
| Petrol blue | `#0b1120` |
| Indigo | `#390892` |

## Package from source

With Node.js installed:

```powershell
npx --yes @vscode/vsce package
```

The packaged `.vsix` is attached to each GitHub release rather than committed to the source tree.

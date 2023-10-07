---
title     : Changelog
layout    : default
class     : changelog
permalink : /changelog/
---

All notable changes to VariableValues are documented in this file.
{: .lead }

<!--

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
VariableValues adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

semantic versioning: MAJOR.MINOR.PATCH
see http://keepachangelog.com/

| MAJOR | incompatible API changes                           |
| MINOR | new functionality in a backwards compatible manner |
| PATCH | backwards compatible bug fixes                     |

additional labels for pre-release and build 
as extensions to the MAJOR.MINOR.PATCH format

types of changes:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

-->


0.1.6
-----

- <span class='badge'>Added</span> Merging GlyphValidator and BatchValidator into [FontValidator].
- <span class='badge'>Added</span> Adding [VarGlyph Assistant] to edit glyph-level data in a designspace.
- <span class='badge'>Changed</span> Removing the “glyphs” tab from VarFont Assistant (use VarGlyph Assistant instead).
- <span class='badge'>Changed</span> Reorganising documentation around [Documentation System] structure.

0.1.5
-----

- <span class='badge'>Added</span> Adding reference points and description to [Measurements] tool.
- <span class='badge'>Added</span> Making Measurements tool remember choice of preview color.
- <span class='badge'>Changed</span> Improving visualisation of small measurements with larger color bands.


0.1.4
-----

- <span class='badge'>Changed</span> Rewriting [Measurements] tool around external JSON files with measurement data.
- <span class='badge'>Changed</span> Rewriting [VarFont Assistant > Measurements] around the new measurement files.
- <span class='badge'>Changed</span> Updating documentation and screenshots.


0.1.3
-----

- <span class='badge'>Added</span> Adding support for “ghost points” to measure glyph margins.
- <span class='badge'>Added</span> Adding kerning preview to VarFont Assistant.
- <span class='badge'>Added</span> Adding `kerningPairPlus` and `kerningPreview` as separate modules for command-line use.
- <span class='badge'>Added</span> Adding `variableValues.validation` with functions to compare glyph and font data.
- <span class='badge'>Added</span> Adding [GlyphValidator] and [BatchValidator] dialogs.


0.1.2
-----

- <span class='badge'>Added</span> Adding [Measurements] tool to create and visualize measurements at the font and glyph levels.
- <span class='badge'>Added</span> Adding example font (Roboto) with font- and glyph-level measurements included.


0.1.1
-----

- <span class='badge'>Added</span> Adding `measurements` module to measure distances in a font. Based on [ParamaRoundup].
- <span class='badge'>Added</span> Adding extension package and `.mechanic` file for easy installation in RoboFont.
- <span class='badge'>Changed</span> Updating documentation content and stylesheet.


0.1.0
-----

Initial public release.

- <span class='badge'>Added</span> Rebuilding documentation with Jekyll and GitHub Pages.


[Measurements]: ../dialogs/measurements
[GlyphValidator]: ../dialogs/glyph-validator
[BatchValidator]: ../dialogs/batch-validator
[FontValidator]: #
[VarFont Assistant > Measurements]: ../dialogs/varfont-assistant/#measurements
[ParamaRoundup]: http://github.com/FontBureau/Parama-roundup
[Documentation System]: http://documentation.divio.com/
[VarGlyph Assistant]: #

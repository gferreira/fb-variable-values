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


0.2.0
-----

- <span class='badge'>Added</span> Adding new `GlyphSetProofer` to create informative PDF proofs of the full glyph set of designspace sources.
- <span class='badge'>Added</span> Adding new `VarProject` tool to apply various actions to some or all sources in a designspace.
- <span class='badge'>Changed</span> Rewriting `GlyphValidator` with left/right margin checks, component equality, refresh button, mark glyph types.


0.1.9
-----

- <span class='badge'>Changed</span> Adding option to turn off preview of glyph-level measurements in `Measurements tool.
- <span class='badge'>Changed</span> Adding option to use italic angle when previewing glyph-level measurements (buggy).
- <span class='badge'>Changed</span> Changing position of glyph cell labels for glyph-level measurements.


0.1.8
-----

- <span class='badge'>Added</span> Adding new `TempGlyphs` tool to import default glyphs into a sparse source.
- <span class='badge'>Added</span> Bringing back `GlyphValidator` tool to display validation results in font and glyph windows.
- <span class='badge'>Added</span> Adding documentation for `TempGlyphs` and `TempEdit`.
- <span class='badge'>Added</span> Adding check for equal contours in glyph validation tools.
- <span class='badge'>Changed</span> Adding support for named points in font-level measurements.
- <span class='badge'>Changed</span> Various edits and improvements to the documentation.


0.1.7
-----

- <span class='badge'>Changed</span> Removing `FontValidator` check result marks from Font Overview and Glyph View (too slow).
- <span class='badge'>Changed</span> Making `FontValidator` tabs independent, glyphs tab now loads data for each selected glyph.
- <span class='badge'>Changed</span> Renaming `FontValidator` to `SourceValidator`.


0.1.6
-----

- <span class='badge'>Added</span> Merging `GlyphValidator` and `BatchValidator` into `FontValidator`.
- <span class='badge'>Added</span> Adding `VarGlyphAssistant` to edit glyph-level data in a designspace.
- <span class='badge'>Changed</span> Removing the “glyphs” tab from `VarFontAssistant` (use `VarGlyphAssistant` instead).
- <span class='badge'>Changed</span> Reorganising documentation around [Documentation System] structure.

[Documentation System]: http://documentation.divio.com/


0.1.5
-----

- <span class='badge'>Added</span> Adding reference points and description to `Measurements` tool.
- <span class='badge'>Added</span> Making `Measurements` tool remember choice of preview color.
- <span class='badge'>Changed</span> Improving visualisation of small measurements with larger color bands.


0.1.4
-----

- <span class='badge'>Changed</span> Rewriting `Measurements` tool around external JSON files with measurement data.
- <span class='badge'>Changed</span> Rewriting the Measurements tab in `VarFontAssistant` around the new measurement files.
- <span class='badge'>Changed</span> Updating documentation and screenshots.


0.1.3
-----

- <span class='badge'>Added</span> Adding support for “ghost points” to measure glyph margins.
- <span class='badge'>Added</span> Adding kerning preview to `VarFontAssistant`.
- <span class='badge'>Added</span> Adding `kerningPairPlus` and `kerningPreview` as separate modules for command-line use.
- <span class='badge'>Added</span> Adding `variableValues.validation` with functions to compare glyph and font data.
- <span class='badge'>Added</span> Adding `GlyphValidator` and `BatchValidator` dialogs.


0.1.2
-----

- <span class='badge'>Added</span> Adding `Measurements` tool to create and visualize measurements at the font and glyph levels.
- <span class='badge'>Added</span> Adding example font (Roboto) with font- and glyph-level measurements included.


0.1.1
-----

- <span class='badge'>Added</span> Adding `measurements` module to measure distances in a font. Based on [ParamaRoundup].
- <span class='badge'>Added</span> Adding extension package and `.mechanic` file for easy installation in RoboFont.
- <span class='badge'>Changed</span> Updating documentation content and stylesheet.

[ParamaRoundup]: http://github.com/FontBureau/Parama-roundup


0.1.0
-----

Initial public release.

- <span class='badge'>Added</span> Rebuilding documentation with [Jekyll] and [GitHub Pages].

[Jekyll]: http://jekyllrb.com/
[GitHub Pages]: http://pages.github.com/

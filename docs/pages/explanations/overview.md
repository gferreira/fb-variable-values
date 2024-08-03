---
title     : Introduction to VariableValues
layout    : default
permalink : /explanations/introduction/
---

<nav aria-label="breadcrumb">
  <ol class="breadcrumb small">
    <li class="breadcrumb-item"><a href="{{ site.url }}">Index</a></li>
    <li class="breadcrumb-item"><a href="{{ site.url }}/explanations">Explanations</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ page.title }}</li>
  </ol>
</nav>

VariableValues is a growing set of tools to visualize and edit data across multiple designspace sources.
{: .lead}

* Table of Contents
{:toc}

### Challenges in variable font production workflows

Developing variable fonts with large designspaces presents new technical challenges which can be difficult to solve with current font editors and production tools. Designers and developers often find themselves working on data which is spread across several font sources. The more sources are needed to be edited simultaneously, the more cumbersome it becomes to have all fonts open in the interface – navigation between sources becomes difficult, and performance suffers in terms of hardware and interaction. In short, it is wasteful to load complete fonts into the interface only to check and edit a small bit of data: a font info value, a kerning pair, the points in a single glyph, etc.

### Viewing and editing small bits of data in multiple sources

VariableValues provides ways to view and edit font-level and glyph-level data in a designspace without having to open whole fonts in the interface. For example, if we need to look into how a certain font info value is changing across various sources in a designspace, we can load that value (and only that value) into a specialized interface where we can view that value in context, edit it if necessary, and save the new value back to the source font where it belongs. The same approach can be applied to kerning pairs, or to the contours of a specific glyph: we load data from multiples sources into a custom interface, view it in context, make changes as needed, and save it back.

### Keeping data in sync across multiple sources

Variable fonts require that all glyphs from all font sources are compatible; this can take a lot of effort in the early stages of a project, when shapes and point structures are changing very often. VariableValues includes tools to visualize and compare various types of glyph data between sources, and tools to validate sources against the default (or any other font), interactively for the current font or in batch for multiple sources at once.

### Working with sparse sources

Sparse sources are sources in which glyphs which are exact duplicates of their default counterpart are left out. This reduces data duplication and file size, but it also introduces the challenge of editing partial fonts. VariableValues now includes the TempGlyphs tool to import glyphs from a default font for context while working on a sparse source. The tool makes it easy to incorporate imported glyphs into the sparse source, or to discard them after editing.

### Measuring shape variation in parametric designspaces

...



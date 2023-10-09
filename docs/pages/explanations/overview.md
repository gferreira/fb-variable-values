---
title     : Overview of VariableValues
layout    : default
permalink : /explanations/overview/
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


### Challenges in current variable font production workflows

Developing variable fonts with large designspaces poses new technical challenges which can be difficult to solve with current font editors and production tools. Designers and developers often find themselves working on data which is spread across several font sources. The more sources are needed to be edited simultaneously, the more cumbersome it becomes to have all fonts open in the interface – navigation between sources becomes difficult, and performance suffers both in terms of hardware and cognition. In short, it is wasteful to open complete fonts in the interface to check and edit just one small bit of data: a font info value, a kerning pair, the points in a single glyph, etc.

### Tools for viewing and editing small bits data in multiple fonts at once

VariableValues provides ways to view and edit font-level and glyph-level data in a designspace *without having to open whole fonts in the interface*. For example, if we need to look into how a certain font info value is changing across various sources in a designspace, we can load that value (and only that value) into a *specialized interface* where we can view that value in context, edit it if necessary, and save the new value back to the source font where it belongs. The same approach can be applied to kerning pairs, or to the contours of a specific glyph: we load data from multiples sources into a custom interface, view in context, make changes as needed, and save it back.
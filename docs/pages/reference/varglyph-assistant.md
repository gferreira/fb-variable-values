---
title     : VarGlyph Assistant
layout    : default
permalink : /reference/varglyph-assistant/
---

<nav aria-label="breadcrumb">
  <ol class="breadcrumb small">
    <li class="breadcrumb-item"><a href="{{ site.url }}">Index</a></li>
    <li class="breadcrumb-item"><a href="{{ site.url }}/reference">Reference</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ page.title }}</li>
  </ol>
</nav>

A tool to view and edit glyph-level values in multiple designspace sources.
{: .lead}

* Table of Contents
{:toc}


Designspace
-----------

Use the **designspace** tab to define which designspaces and font sources to look into.

![]({{ site.url }}/images/VarGlyphAssistant-designspace.png){: .img-fluid}

designspaces
: Drag one or more `.designspace` files into the list.

axes
: ^
  A list of axes in the selected designspace.  
  Drag the items to change the sorting order of the list of sources.


sources
: ^
  A list of all sources in the selected designspace.  
  Select which sources to collect values from in the next tabs.  
  Double-click a source to open the font in the UI.


Glyph sets
----------

Use the **glyph sets** tab to define which glyphs to look into in the selected sources.

![]({{ site.url }}/images/VarGlyphAssistant-glyphsets.png){: .img-fluid}

glyph set files
: Drag one or more `.roboFontSets` files into the list.

glyph sets
: ^
  A list of glyph sets in the selected glyph sets file.  
  Select one or more glyph sets to update the glyph names list.

glyph names
: A list of glyph names in the selected glyph sets.


Attributes
----------

Use the **attributes** tab to visualize and edit glyph attributes in the selected glyphs of selected sources.

![]({{ site.url }}/images/VarGlyphAssistant-attributes.png){: .img-fluid}

load
: Click on the button to collect values from the fonts and display them in the UI.

glyphs
: A list of glyph names for inspection in the selected sources.

attributes
: ^
  Values for various glyph attributes for the selected glyphs across all selected sources.  
  Click on the column headers to sort the list based on a specific attribute.


Compatibility
-------------

Use the **compatibility** tab to visualize and edit contour segments in the selected glyphs of selected sources.

![]({{ site.url }}/images/VarGlyphAssistant-compatibility.png){: .img-fluid}

load
: Click on the button to collect values from the fonts and display them in the UI.

glyphs
: A list of glyph names for inspection in the selected sources.

segments
: ^
  A list of segments in the selected glyphs across all selected sources.  
  The letter codes mean: **L** line segment / **C** cubic segment / **Q** quadratic segment

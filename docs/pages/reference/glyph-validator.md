---
title     : GlyphValidator
layout    : default
permalink : /reference/glyph-validator
---

<nav aria-label="breadcrumb">
  <ol class="breadcrumb small">
    <li class="breadcrumb-item"><a href="{{ site.url }}">Index</a></li>
    <li class="breadcrumb-item"><a href="{{ site.url }}/reference">Reference</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ page.title }}</li>
  </ol>
</nav>

A tool to validate glyphs in the current font against glyphs from another font.
{: .lead}

* Table of Contents
{:toc}


Options
-------

<div class='row'>
<div class='col' markdown='1'>
![]({{ site.url }}/images/GlyphValidator.png){: .img-fluid}
</div>
<div class='col' markdown='1'>
get default…
: Open a dialog to select the default source to check the current font against.

glyph tests
: Click to select which glyph attributes to check and report on.

font window
: Show/hide check results in the Font Overview’s glyph cells.

glyph window
: Show/hide check results in the Glyph View.

</div>
</div>


Check results
-------------

##### Font window

Labels with check results are shown in the Font Overview’s glyph cells if the option *font window* is activated.

![]({{ site.url }}/images/GlyphValidator_font-window.png){: .img-fluid}

##### Glyph window

Labels with check results are shown in the Glyph View if the option *glyph window* is activated.

![]({{ site.url }}/images/GlyphValidator_glyph-window.png){: .img-fluid}


Validation details
------------------

##### Glyph checks

Different glyph attributes are checked for compatibility.  
Check results are identified by the attribute's initial letter.  
Different checks are performed depending on which glyph attribute is tested.  

<table class='table table-hover'>
<tr>
<th>label</th>
<th>glyph attribute</th>
<th>conditions</th>
</tr>
<tr>
<td>W</td>
<td>width</td>
<td markdown='1'>
- same advance width
</td>
</tr>
<tr>
<td>P</td>
<td>points</td>
<td markdown='1'>
- same number of contours
- same number of segments
- same segment types
- same number of points (implied)
- same point positions\*
</td>
</tr>
<tr>
<td>C</td>
<td>components</td>
<td markdown='1'>
- same number of components
- same component names
- same component order
</td>
</tr>
<tr>
<td>A</td>
<td>Anchors</td>
<td markdown='1'>
- same number of anchors
- same anchor names
- same anchor order
</td>
</tr>
<tr>
<td>U</td>
<td>Unicodes</td>
<td markdown='1'>
- same unicode value(s)
</td>
</tr>
</table>

##### Color codes

Check results are displayed as a string of colored labels. Label colors have the following meaning:

| color                                                 | meaning        |
|-------------------------------------------------------|----------------|
| <span style='color:red;'>red</span>                   | not compatible |
| <span style='color:rgba(0, 216.75, 0);'>green</span>  | compatible     |
| <span style='color:rgba(0, 114.75, 255);'>blue</span> | equal\*        |
{: .table .table-hover }

\* The blue label is available only for *points* check: a blue P means that glyph points are not only compatible, but also all point positions match.


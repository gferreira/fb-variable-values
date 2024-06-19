---
title     : GlyphSetProofer
layout    : default
permalink : /reference/glyphset-proofer
---

<nav aria-label="breadcrumb">
  <ol class="breadcrumb small">
    <li class="breadcrumb-item"><a href="{{ site.url }}">Index</a></li>
    <li class="breadcrumb-item"><a href="{{ site.url }}/reference">Reference</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ page.title }}</li>
  </ol>
</nav>

A tool to create informative PDF glyphset proofs of designspace sources.
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


Colors
------

Check results are displayed as a string of colored labels. Label colors have the following meaning:

| color                                                 | meaning        |
|-------------------------------------------------------|----------------|
| <span style='color:red;'>red</span>                   | not compatible |
| <span style='color:rgba(0, 216.75, 0);'>green</span>  | compatible     |
| <span style='color:rgba(0, 114.75, 255);'>blue</span> | equal\*        |
{: .table .table-hover }

\* The blue label is available only for *points* check: a blue P means that glyph points are not only compatible, but also all point positions match.


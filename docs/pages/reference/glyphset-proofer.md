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

![]({{ site.url }}/images/GlyphSetProofer.png){: .img-fluid}


designspaces
: Open a dialog to select the default source to check the current font against.

sources
: Click to select which glyph attributes to check and report on.

make proof
: Show/hide check results in the Font Overview’s glyph cells.

save PDF…
: Show/hide check results in the Glyph View.


Validation details
------------------

##### Check colors

see [Glyph Validator > Validation details > Color codes](glyph-validator)

##### Cell colors

| background color | meaning                                        | 
|------------------|------------------------------------------------|
| blue             | contours only, equal to default                |
| white            | contours only, different from default          |
| light orange     | components only, equal to default              |
| dark orange      | components only, different from default        |
| red              | nested components, or mixed contour/components |
{: .table }

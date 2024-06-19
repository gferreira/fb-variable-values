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
: Drag one or more `.designspace` files into the list.

sources
: A list of all sources\* in the selected designspace. Select one or more sources to proof.

make proof
: Make a proof document for the selected sources, with one source per page.

save PDF…
: Save the current proof as a PDF file.

\* The default source is always shown in the first page of the proof, and is not included in the sources list.  



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

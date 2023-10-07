---
title     : FontValidator
layout    : default
permalink : /reference/font-validator/
---

<nav aria-label="breadcrumb">
  <ol class="breadcrumb small">
    <li class="breadcrumb-item"><a href="{{ site.url }}">Index</a></li>
    <li class="breadcrumb-item"><a href="../../../reference">Reference</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ page.title }}</li>
  </ol>
</nav>

A tool to validate glyphs from one or more fonts against glyphs from another font.
{: .lead}

* Table of Contents
{:toc}


Fonts
-----

Define a reference font and a set of font sources to be checked against it.

![]({{ site.url }}/images/FontValidator-fonts.png){: .img-fluid}

reference font
: ^
  Drag one or more `.ufo` sources into the list.  
  Select one reference font against which the other sources will be checked.

other fonts
: ^
  Drag one or more `.ufo` sources into the list.
  Select which sources to check against the reference font.  

preview
: ^
  Show check results in the current font.

font
: Show check results in the Font Overview of the current font.

glyph
: Show check results in the Glyph Editor of the current font.

marks
: Show/hide marks for individual checks.


<div class="alert alert-warning" role="alert" markdown='1'>
<i class="bi bi-exclamation-circle me-1"></i> Showing marks in the Font Overview is currently very slow. An update using [representations](http://robofont.com/documentation/topics/defcon-representations/) is underway.
{: .card-text }
</div>


Glyphs
------

View check results for all glyphs in the selected fonts.

![]({{ site.url }}/images/FontValidator-glyphs.png){: .img-fluid}

glyphs
: A list of all glyphs in the reference font.

check results
: ^
  A list of color-coded check results for the current glyph in each selected source.  

  🟢 matching  
  🔴 not matching  
  ⚪ missing  

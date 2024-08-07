---
title     : GlyphGauge
layout    : default
permalink : /reference/glyph-gauge
---

<nav aria-label="breadcrumb">
  <ol class="breadcrumb small">
    <li class="breadcrumb-item"><a href="{{ site.url }}">Index</a></li>
    <li class="breadcrumb-item"><a href="{{ site.url }}/reference">Reference</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ page.title }}</li>
  </ol>
</nav>

A tool to to display and validate parametric measurements in the current glyph window.
{: .lead }

* Table of Contents
{:toc }


Options
-------

<div class='row'>
<div class='col-4' markdown='1'>
![]({{ site.url }}/images/GlyphGauge.png){: .img-fluid }
</div>
<div class='col-8' markdown='1'>
get default…
: Open a dialog to select the source to check against the _current font_.

reload default
: Reload the selected source from disk (in case it has changed).

measurements…
: Open a dialog to select a measurements file and load its data into the UI.

reload measurements
: Reload the selected measurements file from disk (in case it has changed).

parent value
: Compare glyph measurements with their font-level parent value (instead of default).

per mille
: Show measurements in per mille values instead of in font units.

tolerance
: Adjust threshold value for valid/invalid measurements (green/red).

display
: Show/hide the measurements visualization in the Glyph View.

</div>
</div>


Check results
-------------

##### Glyph window

![]({{ site.url }}/images/GlyphGauge_glyph-window.png){: .img-fluid}



Validation details
------------------

##### Color codes

Measurements are displayed using the same colors as [Glyph Validator checks](glyph-validator#color-codes), with the following meanings:

| color                                                 | meaning                       |
|-------------------------------------------------------|-------------------------------|
| <span style='color:rgba(0, 114.75, 255);'>blue</span> | equal value                   |
| <span style='color:rgba(0, 216.75, 0);'>green</span>  | different but within treshold |
| <span style='color:red;'>red</span>                   | different and beyond treshold |
| <span style='color:black;'>black</span>               | no value to compare with      |
{: .table .table-hover }


---
title     : Measurements
layout    : default
permalink : /dialogs/measurements/
---

<nav aria-label="breadcrumb">
  <ol class="breadcrumb small">
    <li class="breadcrumb-item"><a href="{{ site.url }}">Index</a></li>
    <li class="breadcrumb-item"><a href="../../dialogs">dialogs</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ page.title }}</li>
  </ol>
</nav>

A tool to create and visualize font- and glyph-level measurements.
{: .lead}


* Table of Contents
{:toc}


Font measurements
-----------------

Create and edit font-level measurements.

![]({{ site.url }}/images/Measurements-1.png){: .img-fluid}

new
: Click on the button to add a new empty font-level measurement to the list.

<div class="alert alert-primary" role="alert" markdown='1'>
For more information about each column see [Measurements format > Font-level measurements](../../measurements-format/#font-level-measurements).
{: .card-text }
</div>


Glyph measurements
------------------

Create and edit glyph-level measurements.

![]({{ site.url }}/images/Measurements-2.png){: .img-fluid}

new
: Select two points and click on the button to add a new empty glyph-level measurement to the list.

color
: The color of measurement lines and captions in the Glyph View display.

<div class="alert alert-primary" role="alert" markdown='1'>
For more information about each column see [Measurements format > Glyph-level measurements](../../measurements-format/#glyph-level-measurements).
{: .card-text }
</div>


Glyph measurements preview
--------------------------

![]({{ site.url }}/images/Measurements-2-preview.png){: .img-fluid}

The Glyph View displays a visualization of the measurements in the current glyph.

- Dotted lines indicate a measurement between pairs of points.
- Select a measurement in the dialog to highlight it and show its name, direction and distance.


Loading and saving
------------------

Reading and writing measurement data to external files.

load…
: Load measurement data from an external JSON file into the UI.

save
: Save the current measurement data to an external JSON file.


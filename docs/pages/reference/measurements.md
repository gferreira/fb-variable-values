---
title     : Measurements
layout    : default
permalink : /reference/measurements/
---

<nav aria-label="breadcrumb">
  <ol class="breadcrumb small">
    <li class="breadcrumb-item"><a href="{{ site.url }}">Index</a></li>
    <li class="breadcrumb-item"><a href="{{ site.url }}/reference">Reference</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ page.title }}</li>
  </ol>
</nav>

A tool to create and visualize font- and glyph-level measurements.
{: .lead}


* Table of Contents
{:toc}


Font measurements
-----------------

Use the **font** tab to create and edit font-level measurements.

![]({{ site.url }}/images/Measurements-1.png){: .img-fluid}

new
: Click to add a new empty font-level measurement to the list.  
  Double-click the new item's cells to edit its content.

<div class="alert alert-primary" role="alert" markdown='1'>
For more information about each column see [Measurements format > Font-level measurements](../../measurements-format/#font-level-measurements).
{: .card-text }
</div>


Glyph measurements
------------------

Use the **glyph** tab to create and edit glyph-level measurements.

![]({{ site.url }}/images/Measurements-2.png){: .img-fluid}

new
: Select two points and click on the button to add a new empty glyph-level measurement to the list.

color
: Choose a color for the measurement lines and captions in the Glyph Editor preview.

flip
: Invert the direction of selected measurements by swapping point indexes 1 and 2.

<div class="alert alert-primary" role="alert" markdown='1'>
For more information about each column see [Measurements format > Glyph-level measurements](../../measurements-format/#glyph-level-measurements).
{: .card-text }
</div>


Glyph measurements preview
--------------------------

![]({{ site.url }}/images/Measurements-2-preview.png){: .img-fluid}

The Glyph View displays a visualization of the measurements in the current glyph.

- Dotted lines indicate a measurement between pairs of points.
- Select one or more measurements in the dialog to highlight and show their name, direction and distance.


Loading and saving
------------------

Reading and writing measurement data to external files.

load…
: Load measurement data from an external JSON file into the UI.

save…
: Save the current measurement data to an external JSON file.


---
title     : VarFont Assistant
layout    : default
permalink : /reference/dialogs/varfont-assistant/
---

<nav aria-label="breadcrumb">
  <ol class="breadcrumb small">
    <li class="breadcrumb-item"><a href="{{ site.url }}">Index</a></li>
    <li class="breadcrumb-item"><a href="../../../reference">Reference</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ page.title }}</li>
  </ol>
</nav>

A tool to view and edit font-level values in multiple designspace sources.
{: .lead}

* Table of Contents
{:toc}


Designspace
-----------

Define which designspaces and font sources to look into.

![]({{ site.url }}/images/VarFontAssistant-1.png){: .img-fluid}

designspaces
: Drag one or more `.designspace` files into the list.

axes
: ^
  A list of axes in the selected designspace.  

sources
: ^
  A list of all sources in the selected designspace.  
  Select which sources to collect values from.
  Click on the column headers to change the sorting order.


Font values
-----------

Visualize and edit font values in selected sources.

![]({{ site.url }}/images/VarFontAssistant-2.png){: .img-fluid}

load
: Click the button to collect values from the fonts and display them in the UI.

attributes
: A list of font attributes for which to display collected values.

values
: ^
  Values and visualization of the selected font attribute across all selected sources.  
  Double-click individual values to edit.

save
: Click the button to save the edited values back into the fonts.


Glyph values
------------

Visualize and edit glyph-level values.

![]({{ site.url }}/images/VarFontAssistant-3.png){: .img-fluid}

load
: Click the button to collect values from the fonts and display them in the UI.

glyphs
: A list of all glyphs in all selected sources.

attributes
: A list of glyph attributes to collect values from.

values
: ^
  Values and visualization of the selected glyph attribute across all selected sources.  
  Double-click individual values to edit.

save
: Click the button to save the edited values back into the fonts.


kerning
-------

Visualize and edit kerning values in selected sources.

![]({{ site.url }}/images/VarFontAssistant-4.png){: .img-fluid}

load
: Click the button to collect values from the fonts and display them in the UI.

pairs
: A list of all kerning pairs in all selected sources.

preview
: A visual preview of the selected kerning pair in all selected sources.

values
: ^
  Values and visualization of the selected kerning pair across all selected sources.  
  Double-click individual values to edit.

save
: Click the button to save the edited values back into the fonts.



measurements
------------

Collect custom measurements from the selected sources.

![]({{ site.url }}/images/VarFontAssistant-5.png){: .img-fluid}

measurement files
: Drag one or more `.json` files containing [measurement definitions] into the list.

load
: Click the button to collect values from the fonts and display them in the UI.

measurements
: ^
  A list of measurement definitions contained in the selected file.  
  Select one measurement to display its values.

values
: ^
  Values and visualization of the selected measurement across all selected sources.  

[measurement definitions]: ../../measurements-format/
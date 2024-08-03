---
title     : Gauging measurements in parametric designspaces
layout    : default
permalink : /explanations/gauging-parametric-measurements/
---

<nav aria-label="breadcrumb">
  <ol class="breadcrumb small">
    <li class="breadcrumb-item"><a href="{{ site.url }}">Index</a></li>
    <li class="breadcrumb-item"><a href="{{ site.url }}/explanations">Explanations</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ page.title }}</li>
  </ol>
</nav>

VariableValues is a growing set of tools to visualize and edit data across multiple designspace sources.
{: .lead}

* Table of Contents
{:toc}


Uses of parametric measurements
-------------------------------

- building parametric designspace (measurements as locations in parametric axes)
- visualizing and understanding glyph shape variation
- quality assurance, consistency, control


Types of measurement
--------------------

#### Between 2 points

A measurement between two points can be horizontal, vertical, or angled (straight).

| direction | description                            |
|-----------|----------------------------------------|
| x         | horizontal distance between two points |
| y         | vertical distance between two points   |
| a         | straight distance between two points   |
{: .table .table-hover }

#### Between 1 point and 1 intersection

*not implemented yet*


Types of measurement points
----------------------------

| type                | reference by               | description                                              | data type |
|---------------------|----------------------------|----------------------------------------------------------|-----------|
| curve point         | point index                | flat index number of the point                           | `int`     |
| glyph margins       | point index (out of range) | flat index number representing the left or right margin  | `int`     |
| vertical dimensions | short key                  | letter representing a vertical font dimension            | `str`     |
{: .table .table-hover }


#### Curve point

Curve points are references by their flat index number, an index number that runs through all on- and off-curve points of a glyph without resetting at a new contour.

To display flat point indexes in RoboFont’s Glyph Editor, go to the [Preferences Editor](#) and set the value of the key `indexesShouldFollowContour` to `0`.
{: .alert .alert-note }

#### Glyph margins

-

#### Vertical dimensions

...


Types of scale
--------------

#### Parent scale (p-scale)

The **p-scale** (`A÷B`) is the scale of a font-level measurement (`A`) in relation to its parent measurement (`B`).

Example:

| ref.    | description                   | name   | glyph | source  |
|---------|-------------------------------|--------|-------|---------|
| `A`     | font-level measurement        | `XOLC` | `n`   | current |
| `B`     | parent font-level measurement | `XOPQ` | `H`   | current |
| `A÷B`   | p-scale                       |        |       |         |
{: .table .table-hover }

#### Font scale (f-scale)

The **f-scale** (`A÷B`) is the scale of a glyph-level measurement (`A`) in relation to the font-level value of the same name (`B`).

Example:

| ref.    | description             | name   | glyph | source  |
|---------|-------------------------|--------|-------|---------|
| `A`     | glyph-level measurement | `XOLC` | `u`   | current |
| `B`     | font-level measurement  | `XOLC` | `n`   | current |
| `A÷B`   | f-scale                 |        |       |         |
{: .table .table-hover }

#### Default scale (d-scale)

The **d-scale** (`A÷B`) is the scale of a glyph-level measurement (`A`) in relation to the same measurement in the default font (`B`).

Example:

| ref.    | description             | name   | glyph | source  |
|---------|-------------------------|--------|-------|---------|
| `A`     | glyph-level measurement | `XOLC` | `u`   | current |
| `B`     | glyph-level measurement | `XOLC` | `u`   | default |
| `A÷B`   | d-scale                 |        |       |         |
{: .table .table-hover }


Measurement validation
----------------------

| scale   | treshold   | validation against            |
|---------|------------|-------------------------------|
| p-scale | p-treshold | parent font-level measurement |
| f-scale | f-treshold | font-level measurement        |
| d-scale | d-treshold | default glyph measurement     |
{: .table .table-hover }

Scale values can be used to validate glyph-level measurements against different types of reference values.

Each scale has a corresponding treshold value. Based on this value, a measurement can be considered either:

- *equal to*
- *different within treshold*
- *different outside treshold*


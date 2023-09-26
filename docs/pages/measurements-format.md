---
title     : Measurements format
layout    : default
permalink : /measurements-format/
---

A data format to store definitions of font-level and glyph-level measurements.
{: .lead}


* Table of Contents
{:toc}


Data structure
--------------

A measurement establishes a link between two points and allows us to calculate the distance between them.

The order of the points determine if the measurement is positive or negative.

### Font-level measurements

- A font may contain multiple font-level measurements.
- Font measurement names must be unique.

| attribute | description                                            |
|-----------|--------------------------------------------------------|
| name      | name of the measurement                                |
| glyph 1   | name of the glyph containing the 1st measurement point |
| point 1   | index of the 1st measurement point                     |
| glyph 2   | name of the glyph containing the 2nd measurement point |
| point 2   | index of the 2nd measurement point                     |
| direction | direction of measurement                               |
| parent    | parent measurement (optional)                          |
{: .table .table-hover }

### Glyph-level measurements

- A glyph may contain multiple glyph-level measurements.
- Glyph measurement names are usually related to font-level measurements.
- Glyph measurement names must **not** be unique.
- Glyph measurement identifiers are created from the point indexes.

| attribute | description                                            |
|-----------|--------------------------------------------------------|
| name      | name of the measurement                                |
| point 1   | index of the 1st measurement point                     |
| point 2   | index of the 2nd measurement point                     |
| direction | direction of measurement                               |
| parent    | parent measurement (optional)                          |
{: .table .table-hover }

### Special points

Two special “ghost points” at the glyph’s left edge (origin) and right edge (advance width) are available.

| point       | index                                      | example |
|-------------|--------------------------------------------|---------|
| left edge   | smaller than zero                          | -1      |
| right edge  | larger than the total point count in glyph | 99      |
{: .table .table-hover }


Python example
--------------

The key for font-level measurements is the name of the measurement.

```python
fontMeasurements = {
    'XTUC' : {
        'glyph 1'   : 'H',
        'point 1'   : 11,
        'glyph 2'   : 'H',
        'point 2'   : 8,
        'direction' : 'x',
        'parent'    : 'XTRA',
    },
    # more font-level measurements here ...
}
```

The key for glyph-level measurements is an identifier created from the two point indexes.

```python
glyphMeasurements = {
    "a" : {
      f'{ptIndex1} {ptIndex2}' : {
          'name'      : 'XTRA',
          'direction' : 'x',
      },
      # more glyph-level measurements here ...
    },
    # more glyphs here ...
}
```


JSON example
------------

Measurements can also be stored in standalone JSON files. This makes it easier to use the same measurement definitions for all sources in a designspace.

```json
{
  "font": {
    "XTUC": {
      "direction": "x",
      "glyph 1": "H",
      "point 1": "11",
      "glyph 2": "H",
      "point 2": "8",
      "parent": "XTRA"
    },
    /* more font-level measurements here ... */
  },
  "glyphs": {
    "n": {
      "0 20": {
        "direction": "x",
        "name": "XOLC"
      },
      "11 12": {
        "direction": "x",
        "name": "XOLC"
      },
      "13 19": {
        "direction": "x",
        "name": "XTLC"
      },
      /* more glyph-level measurements here ... */
    },
    /* more glyphs here ... */
  },    
}
```


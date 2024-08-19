# from importlib import reload
# import variableValues.dialogs.RF4.DesignSpaceSelector
# reload(variableValues.dialogs.RF4.DesignSpaceSelector)

from mojo.roboFont import OpenWindow, OpenFont
from variableValues.dialogs.RF4.DesignSpaceSelector import DesignSpaceSelector_EZUI


class VarGlyphAssistant_EZUI(DesignSpaceSelector_EZUI):

    title = 'VarGlyph Assistant'

    columnLeft     = 160
    columnFontName = 240
    columnValue    = 50

    content = DesignSpaceSelector_EZUI.content
    content += '''
    * Tab: glyphs        @glyphsTab
    >= VerticalStack

    >> glyphset files
    >> |-files------|
    >> | file name  |    @glyphsetFiles
    >> |------------|

    >>= HorizontalStack
    >>>= VerticalStack
    >>>> glyph sets
    >>>> |-----------|
    >>>> |           |   @glyphSets
    >>>> |-----------|

    >>>= VerticalStack   @glyphNamesStack
    >>>> glyph names
    >>>> [[_a b c A B C one two three_]] @glyphNames

    >= HorizontalStack
    >> ( load )          @loadGlyphSetsButton

    * Tab: attributes    @attributesTab
    >= HorizontalStack

    >>= VerticalStack
    >>> glyphs
    >>> |-----------|
    >>> |           |    @attributesGlyphs
    >>> |-----------|

    >>= VerticalStack
    >>> values
    >>> |-----------|--------|------|-------|----------|----------|--------|---------|------------|
    >>> | file name | width  | left | right | contours | segments | points | anchors | components |  @attributesValues
    >>> |-----------|--------|------|-------|----------|----------|--------|---------|------------|

    >= HorizontalStack
    >> ( load )          @loadAttributesButton

    * Tab: segments      @segmentsTab
    >= HorizontalStack

    >>= VerticalStack
    >>> glyphs
    >>> |-----------|
    >>> |           |    @segmentsGlyphs
    >>> |-----------|

    >>= VerticalStack
    >>> values
    >>> |-----------|
    >>> |           |    @segmentsValues
    >>> |-----------|

    >= HorizontalStack
    >> ( load )          @loadSegmentsButton

    * Tab: measurements  @measurementsTab
    >= VerticalStack

    >> measurement files
    >> |-files------|
    >> | file name  |    @measurementFiles
    >> |------------|

    >>= HorizontalStack
    >>>= VerticalStack
    >>>> glyphs
    >>>> |-----------|
    >>>> |           |   @measurementGlyphs
    >>>> |-----------|

    >>>= VerticalStack   @glyphMeasurementsStack
    >>>> measurements
    >>>> |------|-----|-----|-----|
    >>>> | name | dir | pt1 | pt2 | @glyphMeasurements
    >>>> |------|-----|-----|-----|

    >>>= VerticalStack   @glyphMeasurementValuesStack
    >>>> values
    >>>> |-----------|-------|---------|
    >>>> | file name | units | permill | @glyphMeasurementValues
    >>>> |-----------|-------|---------|

    >= HorizontalStack
    >> ( load )          @loadGlyphMeasurementsButton
    '''

    buttonWidth = DesignSpaceSelector_EZUI.buttonWidth

    descriptionData = DesignSpaceSelector_EZUI.descriptionData.copy()
    descriptionData.update(dict(
        # glyphs
        glyphsetFiles=dict(
            alternatingRowColors=True,
            height=100,
            itemType="dict",
            acceptedDropFileTypes=[".roboFontSets"],
            allowsDropBetweenRows=True,
            allowsInternalDropReordering=True,
            allowsMultipleSelection=False,
            columnDescriptions=[
                dict(
                    identifier="path",
                    title="path",
                    cellClassArguments=dict(
                        showFullPath=True
                    )
                ),
            ],
        ),
        glyphSets=dict(
            alternatingRowColors=True,
            width=columnLeft,
        ),
        glyphNamesStack=dict(
            distribution="fill",
        ),
        glyphNames=dict(
            editable=True,
            height='fill',
        ),
        loadGlyphSetsButton=dict(
            width=buttonWidth,
        ),
        # attributes
        attributesGlyphs=dict(
            alternatingRowColors=True,
            width=columnLeft,
        ),
        attributesValues=dict(
            alternatingRowColors=True,
            columnDescriptions=[
                dict(
                    identifier="fileName",
                    title="file name",
                    width=columnFontName,
                    minWidth=columnFontName*0.9,
                    maxWidth=columnFontName*2,
                ),
                dict(
                    identifier="width",
                    title="W",
                    width=columnValue,
                ),
                dict(
                    identifier="left",
                    title="L",
                    width=columnValue,
                ),
                dict(
                    identifier="right",
                    title="R",
                    width=columnValue,
                ),
                dict(
                    identifier="contours",
                    title="C",
                    width=columnValue,
                ),
                dict(
                    identifier="segments",
                    title="S",
                    width=columnValue,
                ),
                dict(
                    identifier="points",
                    title="P",
                    width=columnValue,
                ),
                dict(
                    identifier="anchors",
                    title="A",
                    width=columnValue,
                ),
                dict(
                    identifier="components",
                    title="C",
                    width=columnValue,
                ),
            ]
        ),
        loadAttributesButton=dict(
            width=buttonWidth,
        ),
       # segments
        segmentsGlyphs=dict(
            alternatingRowColors=True,
            width=columnLeft,
        ),
        segmentsValues=dict(
            alternatingRowColors=True,
        ),
        loadSegmentsButton=dict(
            width=buttonWidth,
        ),
        # measurements
        measurementFiles=dict(
            alternatingRowColors=True,
            height=100,
            itemType="dict",
            acceptedDropFileTypes=[".measurements"],
            allowsDropBetweenRows=True,
            allowsInternalDropReordering=True,
            allowsMultipleSelection=False,
            columnDescriptions=[
                dict(
                    identifier="path",
                    title="path",
                    cellClassArguments=dict(
                        showFullPath=True
                    )
                ),
            ],
        ),
        measurementGlyphs=dict(
            alternatingRowColors=True,
            width=columnLeft,
        ),
        glyphMeasurementsStack=dict(
            distribution="fill",
        ),
        glyphMeasurements=dict(
            alternatingRowColors=True,
            width=columnLeft*1.5,
            columnDescriptions=[
                dict(
                    identifier="name",
                    title="name",
                    width=columnValue*1.2,
                ),
                dict(
                    identifier="direction",
                    title="dir",
                    width=columnValue*0.5,
                ),
                dict(
                    identifier="pt1",
                    title="pt1",
                    width=columnValue*0.6,
                ),
                dict(
                    identifier="pt2",
                    title="pt2",
                    width=columnValue*0.6,
                ),
            ],
        ),
        glyphMeasurementValuesStack=dict(
            distribution="fill",
        ),
        glyphMeasurementValues=dict(
            alternatingRowColors=True,
            columnDescriptions=[
                dict(
                    identifier="fileName",
                    title="file name",
                    width=columnFontName,
                    minWidth=columnFontName*0.9,
                    maxWidth=columnFontName*2,
                ),
                dict(
                    identifier="units",
                    title="units",
                    width=columnValue,
                ),
                dict(
                    identifier="permill",
                    title="permill",
                    width=columnValue,
                ),
            ],
        ),
        loadGlyphMeasurementsButton=dict(
            width=buttonWidth,
        ),
    ))


if __name__ == '__main__':

    OpenWindow(VarGlyphAssistant_EZUI)

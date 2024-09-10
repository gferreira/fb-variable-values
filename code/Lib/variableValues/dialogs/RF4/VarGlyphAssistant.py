from importlib import reload
import variableValues.dialogs.RF4.DesignSpaceSelector
reload(variableValues.dialogs.RF4.DesignSpaceSelector)

import os
from defcon import Font
from mojo.roboFont import OpenWindow, OpenFont
from mojo.smartSet import readSmartSets
from variableValues.dialogs.RF4.DesignSpaceSelector import DesignSpaceSelector_EZUI


class VarGlyphAssistant_EZUI(DesignSpaceSelector_EZUI):

    title = 'VarGlyph Assistant'

    columnLeft       = 160
    columnFontName   = 240
    columnValue      = 40
    columnValueAttrs = 40

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

    * Tab: attributes    @attributesTab
    >= HorizontalStack

    >>= VerticalStack
    >>> glyphs
    >>> |-----------|
    >>> |           |    @attributesGlyphs
    >>> |-----------|

    >>= VerticalStack
    >>> values
    >>> |-----------|---|---|---|---|---|---|---|---|
    >>> | file name | C | S | P | A | C | L | R | W |  @attributesValues
    >>> |-----------|---|---|---|---|---|---|---|---|

    >= HorizontalStack
    >> ( load )          @loadAttributesButton

    * Tab: points        @pointsTab
    >= HorizontalStack

    >>= VerticalStack
    >>> glyphs
    >>> |-----------|
    >>> |           |    @pointsGlyphs
    >>> |-----------|

    >>= VerticalStack
    >>> values
    >>> |-----------|
    >>> |           |    @pointsValues
    >>> |-----------|

    >= HorizontalStack
    >> ( load )          @loadPointsButton

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
    >>>> |------------------|-----------|-----|-----|
    >>>> | measurement name | direction | pt1 | pt2 | @glyphMeasurements
    >>>> |------------------|-----------|-----|-----|

    >>>= VerticalStack   @glyphMeasurementValuesStack
    >>>> values
    >>>> |-----------|-------|---------|
    >>>> | file name | units | permill | @glyphMeasurementValues
    >>>> |-----------|-------|---------|

    >= HorizontalStack
    >> ( load )          @loadGlyphMeasurementsButton
    '''

    buttonWidth = DesignSpaceSelector_EZUI.buttonWidth

    _tables  = DesignSpaceSelector_EZUI._tables.copy()
    _tables += ['glyphsetFiles', 'glyphSets', 'attributesGlyphs', 'attributesValues']

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
            allowsMultipleSelection=False,
            width=columnLeft,
        ),
        attributesValues=dict(
            alternatingRowColors=True,
            allowsSorting=True,
            columnDescriptions=[
                dict(
                    identifier="fileName",
                    title="file name",
                    width=columnFontName,
                    minWidth=columnFontName*0.9,
                    maxWidth=columnFontName*2,
                    sortable=True,
                ),
                dict(
                    identifier="contours",
                    title="C",
                    width=columnValueAttrs,
                    sortable=True,
                ),
                dict(
                    identifier="segments",
                    title="S",
                    width=columnValueAttrs,
                    sortable=True,
                ),
                dict(
                    identifier="points",
                    title="P",
                    width=columnValueAttrs,
                    sortable=True,
                ),
                dict(
                    identifier="anchors",
                    title="A",
                    width=columnValueAttrs,
                    sortable=True,
                ),
                dict(
                    identifier="components",
                    title="C",
                    width=columnValueAttrs,
                    sortable=True,
                ),
                dict(
                    identifier="left",
                    title="L",
                    width=columnValueAttrs,
                    sortable=True,
                ),
                dict(
                    identifier="right",
                    title="R",
                    width=columnValueAttrs,
                    sortable=True,
                ),
                dict(
                    identifier="width",
                    title="W",
                    width=columnValueAttrs,
                    sortable=True,
                ),
            ]
        ),
        loadAttributesButton=dict(
            width=buttonWidth,
        ),
       # points
        pointsGlyphs=dict(
            alternatingRowColors=True,
            width=columnLeft,
        ),
        pointsValues=dict(
            alternatingRowColors=True,
        ),
        loadPointsButton=dict(
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

    _glyphSets   = {}
    _glyphAttrs  = {}
    _glyphPoints = {}

    # ---------
    # callbacks
    # ---------

    # glyph sets

    def glyphsetFilesCreateItemsForDroppedPathsCallback(self, sender, paths):
        items = []
        for path in paths:
            item = dict(path=path)
            items.append(item)
        return items

    def glyphsetFilesSelectionCallback(self, sender):

        glyphsetFilesTable = self.w.getItem("glyphsetFiles")
        glyphsetFilesSelection = glyphsetFilesTable.getSelectedItems()

        if not glyphsetFilesSelection:
            return

        selectedGlyphsetFile = glyphsetFilesSelection[0]
        glyphsetFilePath = selectedGlyphsetFile['path']

        assert os.path.exists(glyphsetFilePath)
        smartSets = readSmartSets(glyphsetFilePath, useAsDefault=False, font=None)

        self._glyphSets = {}
        for smartSet in smartSets:
            for group in smartSet.groups:
                self._glyphSets[group.name] = group.glyphNames

        glyphSetsTable = self.w.getItem("glyphSets")
        glyphSetsTable.set(self._glyphSets.keys())

    def glyphSetsSelectionCallback(self, sender):

        glyphSets  = self.w.getItem('glyphSets')
        glyphNames = self.w.getItem('glyphNames')

        selectedGlyphSets = glyphSets.getSelectedItems()

        if not selectedGlyphSets:
            glyphNames.set([])
            return

        _glyphNames = []
        for glyphSet in selectedGlyphSets:
            _glyphNames += self._glyphSets[glyphSet]

        glyphNames.set(' '.join(_glyphNames))

    # attributes

    def loadAttributesButtonCallback(self, sender):
        # load glyph names
        glyphNames = self.w.getItem('glyphNames').get().split()
        self.w.getItem('attributesGlyphs').set(glyphNames)

        # collect glyph values into dict
        selectedSources = self.w.getItem('sources').getSelectedItems()
        selectedSourceNames = [src['name'] for src in selectedSources]

        glyphAttributeIDs = ['width', 'left', 'right', 'contours', 'segments', 'points', 'anchors', 'components']
        self._glyphAttrs = {}

        for srcName in selectedSourceNames:
            if srcName in self.sources:
                srcPath = self.sources[srcName]
                font = Font(srcPath)
                self._glyphAttrs[srcName] = {}
                for glyphName in glyphNames:
                    if glyphName not in font:
                        continue
                    glyph = font[glyphName]
                    self._glyphAttrs[srcName][glyphName] = {}
                    for attr in glyphAttributeIDs:
                        if attr == 'width':
                            value = glyph.width
                        elif attr == 'left':
                            value = glyph.leftMargin
                        elif attr == 'right':
                            value = glyph.rightMargin
                        elif attr == 'contours':
                            value = len(glyph)
                        elif attr == 'segments':
                            value = 0
                            for contour in glyph:
                                value += len(contour.segments)
                        elif attr == 'points':
                            value = 0
                            for contour in glyph:
                                value += len(contour)
                        elif attr == 'anchors':
                            value = len(glyph.anchors)
                        elif attr == 'components':
                            value = len(glyph.components)
                        self._glyphAttrs[srcName][glyphName][attr] = value

                font.close()

        if len(glyphNames):
            self.w.getItem('attributesGlyphs').setSelectedIndexes([0])
            self.attributesGlyphsSelectionCallback(None)

    def attributesGlyphsSelectionCallback(self, sender):
        selection = self.w.getItem('attributesGlyphs').getSelectedItems()
        if not len(selection):
            return

        glyphName = selection[0]
        listItems = []
        for srcName in self._glyphAttrs:
            listItem = { 'fileName' : srcName }
            if glyphName in self._glyphAttrs[srcName]:
                for attr in self._glyphAttrs[srcName][glyphName]:
                    listItem[attr] = self._glyphAttrs[srcName][glyphName][attr]
            else:
                for attr in self._glyphAttrsLabels:
                    listItem[attr] = ''
            listItems.append(listItem)

        self.w.getItem('attributesValues').set(listItems)

    # points

    def loadPointsButtonCallback(self, sender):
        # load glyph names
        glyphNames = self.w.getItem('glyphNames').get().split()
        self.w.getItem('pointsGlyphs').set(glyphNames)

        # collect glyph points into dict
        selectedSources = self.w.getItem('sources').getSelectedItems()
        selectedSourceNames = [src['name'] for src in selectedSources]

        self._glyphPoints = {}
        for srcName in selectedSourceNames:
            if srcName in self.sources:
                srcPath = self.sources[srcName]
                font = Font(srcPath)
                self._glyphPoints[srcName] = {}
                for glyphName in glyphNames:
                    if glyphName not in font:
                        continue
                    glyph = font[glyphName]
                    points = [p.segmentType for c in glyph for p in c]
                    self._glyphPoints[srcName][glyphName] = points

                font.close()

        if len(glyphNames):
            self.w.getItem('pointsGlyphs').setSelectedIndexes([0])
            self.pointsGlyphsSelectionCallback(None)

    def pointsGlyphsSelectionCallback(self, sender):
        selection = self.w.getItem('pointsGlyphs').getSelectedItems()
        if not len(selection):
            return

        glyphName = selection[0]

        pMax = 0
        for srcName in self._glyphPoints:
            pts = self._glyphPoints[srcName][glyphName]
            try:
                if len(pts) > pMax:
                    pMax = len(pts)
            except:
                pass
        print(pMax)

        pointsTable = self.w.getItem('pointsGlyphs')
        print(pointsTable)
        print(pointsTable.getPosSize())
        print(dir(pointsTable))

        # glyphName = selection[0]
        # listItems = []
        # for srcName in self._glyphPoints:
        #     listItem = { 'fileName' : srcName }
        #     if glyphName in self._glyphPoints[srcName]:
        #         for attr in self._glyphPoints[srcName][glyphName]:
        #             listItem[attr] = self._glyphAttrs[srcName][glyphName][attr]


        #     listItems.append(listItem)

        # self.w.getItem('attributesValues').set(listItems)


if __name__ == '__main__':

    OpenWindow(VarGlyphAssistant_EZUI)


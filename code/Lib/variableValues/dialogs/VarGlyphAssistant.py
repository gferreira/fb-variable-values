from importlib import reload
import variableValues.dialogs.DesignSpaceSelector
reload(variableValues.dialogs.DesignSpaceSelector)

import AppKit
import os, sys
import plistlib
from vanilla import  Window, EditText, TextBox, Box, List, Button, Tabs, LevelIndicatorListCell
from mojo.roboFont import OpenWindow, OpenFont
from mojo.smartSet import readSmartSets
from variableValues.dialogs.DesignSpaceSelector import DesignSpaceSelector


def getSegmentTypes(glyph):
    segments = []
    for ci, c in enumerate(glyph.contours):
        for si, s in enumerate(c.segments):
            if s.type == 'curve':
                segmentType = 'C' # △ 
            elif s.type == 'qcurve':
                segmentType = 'Q' # □
            else:
                segmentType = 'L' # ◯ 
            segments.append(segmentType)
    return segments


class VarGlyphAssistant(DesignSpaceSelector):
    
    title = 'VarGlyph Assistant'
    key   = 'com.fontBureau.varGlyphAssistant'

    _tabsTitles = ['designspace', 'glyph sets', 'attributes', 'segments']

    _glyphAttrs = {}
    _glyphAttrsLabels = [
        'width',
        'left',
        'right',
        'contours',
        'segments',
        'points',
        'anchors',
        'components',
    ]
    _glyphCompatibility = {}

    _glyphSetsFiles = {}
    _glyphSets = {}

    def __init__(self):
        self.w = Window(
                (self.width, self.height), title=self.title,
                minSize=(self.width, 360))

        x = y = p = self.padding
        self.w.tabs = Tabs((x, y, -p, -p), self._tabsTitles)

        self.initializeDesignspacesTab()
        self.initializeGlyphsTab()
        self.initializeAttributesTab()
        self.initializeCompatibilityTab()

        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

    # initialize UI

    def initializeGlyphsTab(self):

        tab = self._tabs['glyph sets']

        x = p = self.padding
        y = p/2
        x2 = x + self._colLeft + p

        tab.glyphSetsFilesLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'glyph set files')

        y += self.lineHeight + p/2
        tab.glyphSetsFiles = List(
                (x, y, -p, self.lineHeight*3),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                enableDelete=True,
                selectionCallback=self.selectGlyphSetsFileCallback,
                otherApplicationDropSettings=dict(
                    type=AppKit.NSFilenamesPboardType,
                    operation=AppKit.NSDragOperationCopy,
                    callback=self.dropGlyphSetsFilesCallback),
                )

        y += self.lineHeight*3 + p
        tab.glyphSetsLabel = TextBox(
                (x, y, self._colLeft, self.lineHeight),
                'glyph sets')

        tab.glyphNamesLabel = TextBox(
                (x2, y, -p, self.lineHeight),
                'glyph names')

        y += self.lineHeight + p/2
        tab.glyphSets = List(
                (x, y, self._colLeft, -self.lineHeight-p*2),
                [],
                allowsMultipleSelection=True,
                allowsEmptySelection=False,
                selectionCallback=self.selectGlyphSetCallback,
            )

        tab.glyphNames = EditText(
                (x2, y, -p, -self.lineHeight-p*2),
                '',
            )

        y = -(self.lineHeight + p)
        tab.updateGlyphs = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'load',
                # callback=self.updateMeasurementsCallback,
            )

    def initializeAttributesTab(self):

        tab = self._tabs['attributes']

        x = p = self.padding
        y = p/2
        tab.glyphsLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'glyphs')

        y += self.lineHeight + p/2
        tab.glyphs = List(
                (x, y, self._colLeft, -(self.lineHeight + p*2)),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                selectionCallback=self.selectGlyphAttrsCallback,
            )

        y = p/2
        x2 = x + self._colLeft + p
        tab.glyphAttributesLabel = TextBox(
                (x2, y, -p, self.lineHeight),
                'attributes')

        y += self.lineHeight + p/2
        tab.glyphAttributes = List(
                (x2, y, -p, -(self.lineHeight + p*2)),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=True,
                columnDescriptions=[{"title": t, 'width': self._colFontName*1.5, 'minWidth': self._colFontName} if ti == 0 else {"title": t, 'width': self._colValue*1.25} for ti, t in enumerate(['file name'] + self._glyphAttrsLabels)],
            )

        y = -(self.lineHeight + p)
        tab.updateValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'load',
                callback=self.updateAttributesCallback,
            )

    def initializeCompatibilityTab(self):

        tab = self._tabs['segments']

        x = p = self.padding
        y = p/2
        tab.glyphsLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'glyphs')

        y += self.lineHeight + p/2
        tab.glyphs = List(
                (x, y, self._colLeft, -(self.lineHeight + p*2)),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                selectionCallback=self.selectGlyphCompatibilityCallback,
            )

        y = p/2
        x2 = x + self._colLeft + p
        tab.segmentsLabel = TextBox(
                (x2, y, -p, self.lineHeight),
                'segments')

        y += self.lineHeight + p/2
        tab.segments = List(
                (x2, y, -p, -(self.lineHeight + p*2)),
                [],
            )

        y = -(self.lineHeight + p)
        tab.updateValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'load',
                callback=self.updateCompatibilityCallback,
            )

    # -------------
    # dynamic attrs
    # -------------

    @property
    def selectedGlyphSetsFile(self):
        tab = self._tabs['glyph sets']
        selection = tab.glyphSetsFiles.getSelection()
        glyphSetsFiles = tab.glyphSetsFiles.get()
        selectedGlyphSetsFiles = [gs for i, gs in enumerate(glyphSetsFiles) if i in selection]
        if not len(selectedGlyphSetsFiles):
            return
        return selectedGlyphSetsFiles[0]

    @property
    def selectedGlyphSetsFilePath(self):
        if not self.selectedGlyphSetsFile:
            return
        return self._glyphSetsFiles[self.selectedGlyphSetsFile]

    @property
    def selectedGlyphSets(self):
        tab = self._tabs['glyph sets']
        selection = tab.glyphSets.getSelection()
        glyphSets = tab.glyphSets.get()
        selectedGlyphSets = [gs for i, gs in enumerate(glyphSets) if i in selection]
        if not len(selectedGlyphSets):
            return
        return selectedGlyphSets

    @property
    def selectedGlyphAttributes(self):
        tab = self._tabs['attributes']
        selection = tab.glyphs.getSelection()
        glyphs = tab.glyphs.get()
        selectedGlyphs = [a for i, a in enumerate(glyphs) if i in selection]
        if not len(selectedGlyphs):
            return
        return selectedGlyphs[0]

    @property
    def selectedGlyphCompatibility(self):
        tab = self._tabs['segments']
        selection = tab.glyphs.getSelection()
        glyphs = tab.glyphs.get()
        selectedGlyphs = [a for i, a in enumerate(glyphs) if i in selection]
        if not len(selectedGlyphs):
            return
        return selectedGlyphs[0]

    # ---------
    # callbacks
    # ---------

    # glyph sets

    def dropGlyphSetsFilesCallback(self, sender, dropInfo):
        isProposal = dropInfo["isProposal"]
        existingPaths = sender.get()

        paths = dropInfo["data"]
        paths = [path for path in paths if path not in existingPaths]
        paths = [path for path in paths if os.path.splitext(path)[-1] == '.roboFontSets']

        if not paths:
            return False

        if not isProposal:
            tab = self._tabs['glyph sets']
            for path in paths:
                label = os.path.split(path)[-1]
                self._glyphSetsFiles[label] = path
                tab.glyphSetsFiles.append(label)
                tab.glyphSetsFiles.setSelection([0])

        return True

    def selectGlyphSetsFileCallback(self, sender):

        tab = self._tabs['glyph sets']

        if not self.selectedGlyphSetsFile:
            tab.glyphSets.set([])
            tab.glyphNames.set('')
            return

        assert os.path.exists(self.selectedGlyphSetsFilePath)

        # load smart sets data into dict
        smartSets = readSmartSets(self.selectedGlyphSetsFilePath, useAsDefault=False, font=None)

        self._glyphSets = {}

        for smartSet in smartSets:
            for group in smartSet.groups:
                self._glyphSets[group.name] = group.glyphNames

        tab.glyphSets.set(self._glyphSets.keys())

    def selectGlyphSetCallback(self, sender):
        tab = self._tabs['glyph sets']

        if not self.selectedGlyphSets:
            tab.glyphNames.set([])
            return

        glyphNames = []
        for glyphSet in self.selectedGlyphSets:
            glyphNames += self._glyphSets[glyphSet]

        tab.glyphNames.set(' '.join(glyphNames))

    # attributes

    def updateAttributesCallback(self, sender):
        
        if not self.selectedSources:
            return

        tab = self._tabs['attributes']
        glyphNames = self._tabs['glyph sets'].glyphNames.get().split(' ')

        # collect glyph values into dict
        self._glyphAttrs = {}
        for source in self.selectedSources:
            sourceFileName = source['file name']
            sourcePath = self._sources[sourceFileName]
            f = OpenFont(sourcePath, showInterface=False)

            self._glyphAttrs[sourceFileName] = {}
            for glyphName in glyphNames:
                if glyphName in f:
                    g = f[glyphName]
                    self._glyphAttrs[sourceFileName][glyphName] = {}
                    for attr in self._glyphAttrsLabels:
                        if attr == 'width':
                            value = g.width
                        elif attr == 'left':
                            value = g.leftMargin
                        elif attr == 'right':
                            value = g.rightMargin
                        elif attr == 'contours':
                            value = len(g.contours)
                        elif attr == 'segments':
                            value = 0
                            for c in g.contours:
                                value += len(c)
                        elif attr == 'points':
                            value = 0
                            for c in g.contours:
                                value += len(c.points)
                        elif attr == 'anchors':
                            value = len(g.anchors)
                        elif attr == 'components':
                            value = len(g.components)
                        self._glyphAttrs[sourceFileName][glyphName][attr] = value

            f.close()

        tab.glyphs.set(glyphNames)
        tab.glyphs.setSelection([0])
        self.selectGlyphAttrsCallback(None)

    def selectGlyphAttrsCallback(self, sender):
        tab = self._tabs['attributes']
        glyphName = self.selectedGlyphAttributes

        listItems = []
        for sourceFileName in self._glyphAttrs:
            listItem = { 'file name' : sourceFileName }
            if glyphName in self._glyphAttrs[sourceFileName]:
                for attr in self._glyphAttrs[sourceFileName][glyphName]:
                    listItem[attr] = self._glyphAttrs[sourceFileName][glyphName][attr]
            else:
                for attr in self._glyphAttrsLabels:
                    listItem[attr] = ''

            listItems.append(listItem)

        tab.glyphAttributes.set(listItems)

    # compatibility

    def updateCompatibilityCallback(self, sender):

        if not self.selectedSources:
            return

        tab = self._tabs['segments']
        glyphNames = self._tabs['glyph sets'].glyphNames.get().split(' ')

        # collect glyph compatibility data into dict
        self._glyphCompatibility = {}
        for source in self.selectedSources:
            sourceFileName = source['file name']
            sourcePath = self._sources[sourceFileName]
            f = OpenFont(sourcePath, showInterface=False)

            self._glyphCompatibility[sourceFileName] = {}
            for glyphName in glyphNames:
                if glyphName in f:
                    g = f[glyphName]
                    segments = getSegmentTypes(g)
                else:
                    segments = None
                self._glyphCompatibility[sourceFileName][glyphName] = segments

            # f.close()

        tab.glyphs.set(glyphNames)
        tab.glyphs.setSelection([0])
        self.selectGlyphCompatibilityCallback(None)

    def selectGlyphCompatibilityCallback(self, sender):

        tab = self._tabs['segments']
        glyphName = self.selectedGlyphCompatibility

        segmentsPosSize = tab.segments.getPosSize()
        del tab.segments

        sMax = 0
        for sourceFileName in self._glyphCompatibility:
            segmentsGlyph = self._glyphCompatibility[sourceFileName][glyphName]
            try:
                if len(segmentsGlyph) > sMax:
                    sMax = len(segmentsGlyph)
            except:
                pass

        listItems = []
        segmentsGlyphs = []
        for sourceFileName in self._glyphCompatibility:
            listItem = { 'file name' : sourceFileName }
            segmentsGlyph = self._glyphCompatibility[sourceFileName][glyphName]
            if segmentsGlyph:
                for si, segment in enumerate(segmentsGlyph):
                    listItem[str(si)] = segment
            else:
                for i in range(sMax):
                    listItem[str(i)] = ''
            listItems.append(listItem)
            segmentsGlyphs.append(segmentsGlyph)

        # for S in segmentsGlyphs:
        #     print(S)

        segmentsDescriptions  = [{'title': 'file name', 'minWidth': self._colFontName, 'width': self._colFontName*1.5}]
        segmentsDescriptions += [{'title': str(i), 'width': 20} for i in range(sMax)]

        # create list UI with sources
        tab.segments = List(
                segmentsPosSize, listItems,
                columnDescriptions=segmentsDescriptions,
                allowsMultipleSelection=True,
                enableDelete=False,
                allowsEmptySelection=False,
            )



if __name__ == '__main__':

    OpenWindow(VarGlyphAssistant)


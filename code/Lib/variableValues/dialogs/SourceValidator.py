from importlib import reload
import variableValues.validation
reload(variableValues.validation)

import os
import AppKit
from vanilla import *
from fontTools.ufoLib.glifLib import GlyphSet
from fontParts.world import OpenFont
from mojo.UI import OutputWindow
from mojo.roboFont import OpenWindow, CurrentFont, RGlyph
from variableValues.validation import validateFonts, checkCompatibility, checkEquality
from defcon import Font, Glyph


class SourceValidator:

    title        = 'SourceValidator'
    key          = 'com.fontBureau.variableValues.sourceValidator'
    padding      = 10
    lineHeight   = 22
    buttonWidth  = 100
    width        = 123*5
    height       = 640
    _tabsTitles  = ['fonts', 'glyphs']
    _checks      = {
        'width'         : False,
        'left'          : False,
        'right'         : False,
        'points'        : True,
        'components'    : True,
        'anchors'       : True,
        'unicodes'      : True,
    }
    
    _colLeft     = 123
    _colValue    = 20
    _colFontName = 160
    colorTrue    = 0, 1, 0
    colorFalse   = 1, 0, 0
    _sourcePaths = {}
    _targetPaths = {}
    _targetFonts = {}
    results      = {}
    verbose      = True

    def __init__(self):
        self.w = Window(
                (self.width, self.height), title=self.title,
                minSize=(self.width, 360))

        x = y = p = self.padding
        self.w.tabs = Tabs((x, y, -p, -p), self._tabsTitles)

        self.initializeFontsTab()
        self.initializeGlyphsTab()

        self.w.bind("close", self.closeCallback)
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

    # initialize UI

    @property
    def _tabs(self):
        tabsDict = {}
        for tabTitle in self._tabsTitles:
            tabIndex = self._tabsTitles.index(tabTitle)
            tabsDict[tabTitle] = self.w.tabs[tabIndex]
        return tabsDict

    def initializeFontsTab(self):

        tab = self._tabs['fonts']

        x = p = self.padding
        y = p / 2
        x2 = -(self._colLeft + p)

        tab.checksLabel = TextBox(
                (x2 + p * 1.5, y, -p, self.lineHeight),
                'checks')

        y += self.lineHeight
        for check, value in self._checks.items():
            checkbox = CheckBox(
                (x2 + p * 1.5, y, -p, self.lineHeight),
                check, value=value)
            setattr(tab, check, checkbox)
            y += self.lineHeight

        y = p / 2
        tab.sourcesLabel = TextBox(
                (x, y, x2, self.lineHeight),
                'reference font')

        y += self.lineHeight + p / 2
        tab.sources = List(
                (x, y, x2, self.lineHeight*3),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                enableDelete=True,
                otherApplicationDropSettings=dict(
                    type=AppKit.NSFilenamesPboardType,
                    operation=AppKit.NSDragOperationCopy,
                    callback=self.dropSourcesCallback),
                doubleClickCallback=self.openFontCallback)

        y += self.lineHeight * 3 + p
        tab.targetsLabel = TextBox(
                (x, y, x2, self.lineHeight),
                'other fonts')

        y += self.lineHeight + p / 2
        tab.targets = List(
                (x, y, x2, -(self.lineHeight + p*2)),
                [],
                allowsMultipleSelection=True,
                allowsEmptySelection=False,
                enableDelete=True,
                otherApplicationDropSettings=dict(
                    type=AppKit.NSFilenamesPboardType,
                    operation=AppKit.NSDragOperationCopy,
                    callback=self.dropTargetsCallback),
                doubleClickCallback=self.openFontCallback)

        y = -(self.lineHeight + p)
        tab.validateButton = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'validate',
                callback=self.batchValidateFontsCallback)

    def initializeGlyphsTab(self):

        tab = self._tabs['glyphs']

        x = p = self.padding
        y = p / 2
        x2 = x + self._colLeft + p

        tab.glyphsLabel = TextBox(
                (x, y, self._colLeft, self.lineHeight),
                'glyphs')

        y += self.lineHeight + p / 2
        tab.glyphs = List(
                (x, y, self._colLeft, -(self.lineHeight + p * 2)),
                [],
                selectionCallback=self.selectGlyphCallback,
            )

        columnDescriptions = [{ "title": "source", 'width': self._colFontName * 2, 'minWidth': self._colFontName }]
        for check in self._checks:
            columnDescriptions.append({ "title": check[0].upper(), "width": self._colValue })

        y = p/2
        tab.resultsLabel = TextBox(
                (x2, y, -p, self.lineHeight),
                'check results')

        y += self.lineHeight + p / 2
        tab.results = List(
                (x2, y, -p, -(self.lineHeight + p * 2)),
                [],
                columnDescriptions=columnDescriptions,
                doubleClickCallback=self.openFontCallback)

        y = -(self.lineHeight + p)
        tab.loadButton = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'load',
                callback=self.loadGlyphsCallback)

        # tab.editButton = Button(
        #         (x2, y, self.buttonWidth, self.lineHeight),
        #         'edit',
        #         callback=self.editGlyphsCallback)

    # -------------
    # dynamic attrs
    # -------------

    @property
    def sourcesList(self):
        return self._tabs['fonts'].sources

    @property
    def sourceFontName(self):
        sourceSelection = self.sourcesList.getSelection()
        if not sourceSelection:
            return
        sourceItems = self.sourcesList.get()
        return sourceItems[sourceSelection[0]]

    @property
    def sourceFontPath(self):
        if not self.sourceFontName:
            return
        return self._sourcePaths[self.sourceFontName]

    @property
    def sourceFont(self):
        return OpenFont(self.sourceFontPath, showInterface=False)

    @property
    def targetsList(self):
        return self._tabs['fonts'].targets

    @property
    def targetFontNames(self):
        targetSelection = self.targetsList.getSelection()
        targetItems = self.targetsList.get()
        targetFontNames = []
        for i, targetFontName in enumerate(targetItems):
            if i not in targetSelection:
                continue
            if targetFontName == self.sourceFontName:
                continue
            targetFontNames.append(targetFontName)
        return targetFontNames

    @property
    def targetFontPaths(self):
        return [self._targetPaths[targetFont] for targetFont in self.targetFontNames]

    @property
    def selectedGlyph(self):
        tab = self._tabs['glyphs']
        selection = tab.glyphs.getSelection()
        glyphs = tab.glyphs.get()
        selectedGlyphs = [g for i, g in enumerate(glyphs) if i in selection]
        if not len(selectedGlyphs):
            return
        return selectedGlyphs[0]

    @property
    def selectedSourceNames(self):
        tab = self._tabs['glyphs']
        sourcesSelection = self.results.getSelection()
        sourcesItems = self.results.get()
        sourcesFontNames = []
        for i, sourceFontName in enumerate(sourcesItems):
            if i not in sourcesSelection:
                continue
            sourcesFontNames.append(sourceFontName)
        return sourcesFontNames

    @property
    def selectedSourcePaths(self):
        return [self._targetPaths[targetFont] for targetFont in self.selectedSourceNames]

    @property
    def markFont(self):
        return self._tabs['fonts'].markFont.get()

    @property
    def markGlyph(self):
        return self._tabs['fonts'].markGlyph.get()

    @property
    def showMarks(self):
        tab = self._tabs['fonts']
        return [check for check in self._checks if getattr(tab, check).get()]

    # ---------
    # callbacks
    # ---------

    def dropSourcesCallback(self, sender, dropInfo):
        isProposal = dropInfo["isProposal"]
        existingSources = sender.get()

        sources = dropInfo["data"]
        sources = [source for source in sources if source not in existingSources]
        sources = [source for source in sources if os.path.splitext(source)[-1].lower() == '.ufo']

        if not sources:
            return False

        if not isProposal:
            for source in sources:
                sourceName = os.path.splitext(os.path.split(source)[-1])[0]
                self._sourcePaths[sourceName] = source
                self.sourcesList.append(sourceName)
                self.sourcesList.setSelection([0])

        return True

    def dropTargetsCallback(self, sender, dropInfo):
        isProposal = dropInfo["isProposal"]
        existingTargets = sender.get()

        targets = dropInfo["data"]
        targets = [target for target in targets if target not in existingTargets]
        targets = [target for target in targets if os.path.splitext(target)[-1].lower() == '.ufo']

        if not targets:
            return False

        if not isProposal:
            for target in targets:
                targetName = os.path.splitext(os.path.split(target)[-1])[0]
                self._targetPaths[targetName] = target
                self.targetsList.append(targetName)
                self.targetsList.setSelection([0])

        return True

    def openFontCallback(self, sender):
        selection = sender.getSelection()

        if not selection:
            return

        selection = selection[0]
        items = sender.get()
        item  = items[selection]

        if item == self.sourceFontName:
            ufoPath = self.sourceFontPath
        else:
            ufoPath = self._targetPaths.get(item)
            if ufoPath is None:
                return

        OpenFont(ufoPath, showInterface=True)

    def batchValidateFontsCallback(self, sender):

        options = { check: check in self.showMarks for check in self._checks }

        # -----------------
        # assert conditions
        # -----------------

        # no source font
        if not self.sourceFontName:
            print('no source font selected.\n')
            return

        # no target fonts selected
        targetFontNames = self.targetFontNames
        if not len(targetFontNames):
            print('no target fonts selected.\n')

        # --------------
        # batch validate
        # --------------

        txt = 'batch validating fonts...\n\n'
        for check in self.showMarks:
            txt += f'\t- {check}\n'
        txt += '\n'

        # get source font
        sourceFont = self.sourceFont
        txt += f'\tsource font: {self.sourceFontName}\n\n'

        # get target fonts
        targetFonts = []
        for targetFontName in targetFontNames:
            if targetFontName in self._targetFonts:
                targetFonts.append(self._targetFonts[targetFontName])
            else:
                targetFont = OpenFont(self._targetFonts[targetFontName], showInterface=False)
                self._targetFonts[targetFontName] = targetFont
                targetFonts.append(targetFont)

        txt += validateFonts(targetFonts, sourceFont, options)
        txt += '...done.\n\n'

        O = OutputWindow()
        O.clear()
        O.write(txt)
        O.show()

    def loadGlyphsCallback(self, sender):
        tab = self._tabs['glyphs']
        tab.glyphs.set(self.sourceFont.glyphOrder)

    def selectGlyphCallback(self, sender):
        if not self.selectedGlyph:
            return

        tab = self._tabs['glyphs']

        options = { check: True for check in self._checks.keys() }

        sourceFont  = Font(self.sourceFontPath)
        sourceGlyph = sourceFont[self.selectedGlyph]
        sourceGlyph = RGlyph(sourceGlyph)

        items = []
        for targetFontPath in self.targetFontPaths:
            targetName = os.path.splitext(os.path.split(targetFontPath)[-1])[0]
            if targetName in self._targetFonts:
                targetFont = self._targetFonts[targetName]
            else:
                targetFont = Font(targetFontPath)
                self._targetFonts[targetName] = targetFont

            item = {}
            item['source'] = targetName

            if self.selectedGlyph not in targetFont: # targetGlyphSet:
                for checkName in options.keys():
                    item[checkName] = '⚪'
            else:
                targetGlyph = targetFont[self.selectedGlyph]
                targetGlyph = RGlyph(targetGlyph)

                resultsCompatibility = checkCompatibility(sourceGlyph, targetGlyph)
                resultsEquality      = checkEquality(sourceGlyph, targetGlyph)

                for checkName in options.keys():
                    isCompatible = resultsCompatibility.get(checkName)
                    isEqual = resultsEquality.get(checkName)
                    _checkName = checkName[0].upper()
                    if isCompatible and isEqual:
                        item[_checkName] = '🔵'
                    elif isCompatible or isEqual:
                        item[_checkName] = '🟢'
                    else:
                        item[_checkName] = '🔴'

            items.append(item)

        tab.results.set(items)

    def editGlyphsCallback(self, sender):
        pass

    def closeCallback(self, sender):
        font = CurrentFont()
        if font is None:
            return

# ----
# test
# ----

if __name__ == '__main__':

    OpenWindow(SourceValidator)

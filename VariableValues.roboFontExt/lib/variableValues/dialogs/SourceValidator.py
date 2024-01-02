from importlib import reload
import variableValues.validation
reload(variableValues.validation)

import os
import AppKit
from vanilla import *
from fontTools.ufoLib.glifLib import GlyphSet
from mojo import drawingTools as ctx
from mojo.UI import UpdateCurrentGlyphView, GetFile, OutputWindow
from mojo.events import addObserver, removeObserver
from mojo.roboFont import OpenFont, OpenWindow, CurrentFont, RGlyph
from variableValues.validation import validateGlyph, validateFonts
from defcon import Glyph


class SourceValidator:

    title        = 'SourceValidator'
    key          = 'com.fontBureau.variableValues.sourceValidator'
    padding      = 10
    lineHeight   = 22
    buttonWidth  = 100
    width        = 123*5
    height       = 640
    _tabsTitles  = ['fonts', 'glyphs']
    _checks      = ['width', 'points', 'components', 'anchors', 'unicodes']
    _colLeft     = 123
    _colValue    = 70
    _colFontName = 160
    colorTrue    = 0, 1, 0
    colorFalse   = 1, 0, 0
    _sources     = {}
    _targets     = {}
    results      = {}
    verbose      = True

    def __init__(self):
        self.w = Window(
                (self.width, self.height), title=self.title,
                minSize=(self.width, 360))

        x = y = p = self.padding
        self.w.tabs = Tabs((x, y, -p, -p), self._tabsTitles)

        self.initializeSetupTab()
        self.initializeResultTab()

        self.w.bind("close", self.closeCallback)
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

        # registerRepresentationFactory(Glyph, f"{self.key}.preview", glyphChecksFactory)
        # addObserver(self, "drawLabelsCell",    "glyphCellDrawBackground")
        # addObserver(self, "drawLabelsGlyph",   "drawBackground")

    # initialize UI

    @property
    def _tabs(self):
        tabsDict = {}
        for tabTitle in self._tabsTitles:
            tabIndex = self._tabsTitles.index(tabTitle)
            tabsDict[tabTitle] = self.w.tabs[tabIndex]
        return tabsDict

    def initializeSetupTab(self):

        tab = self._tabs['fonts']

        x = p = self.padding
        y = p/2
        x2 = -(self._colLeft + p)

        tab.checksLabel = TextBox(
                (x2 + p*1.5, y, -p, self.lineHeight),
                'checks')

        y += self.lineHeight
        for check in self._checks:
            checkbox = CheckBox(
                (x2 + p*1.5, y, -p, self.lineHeight),
                check, value=True)
            setattr(tab, check, checkbox)
            y += self.lineHeight

        y = p/2
        tab.sourcesLabel = TextBox(
                (x, y, x2, self.lineHeight),
                'reference font')

        y += self.lineHeight + p/2
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
                )

        y += self.lineHeight*3 + p
        tab.targetsLabel = TextBox(
                (x, y, x2, self.lineHeight),
                'other fonts')

        y += self.lineHeight + p/2
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
                )

        y = -(self.lineHeight + p)
        tab.validateButton = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'validate',
                callback=self.batchValidateFontsCallback)

    def initializeResultTab(self):

        tab = self._tabs['glyphs']

        x = p = self.padding
        y = p/2
        x2 = x + self._colLeft + p

        tab.glyphsLabel = TextBox(
                (x, y, self._colLeft, self.lineHeight),
                'glyphs')

        y += self.lineHeight + p/2
        tab.glyphs = List(
                (x, y, self._colLeft, -(self.lineHeight + p*2)),
                [],
                selectionCallback=self.selectGlyphCallback,
            )

        columnDescriptions = [{ "title": "source", 'width': self._colFontName*1.5, 'minWidth': self._colFontName  }]
        for check in self._checks:
            columnDescriptions.append({ "title": check, "width": self._colValue })

        y = p/2
        tab.resultsLabel = TextBox(
                (x2, y, -p, self.lineHeight),
                'check results')

        y += self.lineHeight + p/2
        tab.results = List(
                (x2, y, -p, -(self.lineHeight + p*2)),
                [],
                columnDescriptions=columnDescriptions)

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
        return self._sources[self.sourceFontName]

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
        return [self._targets[targetFont] for targetFont in self.targetFontNames]

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
        return [self._targets[targetFont] for targetFont in self.selectedSourceNames]

    @property
    def markFont(self):
        return self._tabs['fonts'].markFont.get()

    @property
    def markGlyph(self):
        return self._tabs['fonts'].markGlyph.get()

    @property
    def showMarks(self):
        tab = self._tabs['fonts']
        return [ check for check in self._checks if getattr(tab, check).get()]

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
                self._sources[sourceName] = source
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
                self._targets[targetName] = target
                self.targetsList.append(targetName)
                self.targetsList.setSelection([0])

        return True

    def batchValidateFontsCallback(self, sender):

        options = { check: check in self.showMarks for check in self._checks }

        #-------------------
        # assert conditions
        #-------------------

        # no source font
        if not self.sourceFontName:
            print('no source font selected.\n')
            return

        # no target fonts selected
        targetFontNames = self.targetFontNames
        if not len(targetFontNames):
            print('no target fonts selected.\n')

        #---------------
        # batch validate
        #---------------

        txt = 'batch validating fonts...\n\n'
        for check in self.showMarks:
            txt += f'\t- {check}\n'
        txt += '\n'

        # get source font
        sourceFont = self.sourceFont
        txt += f'\tsource font: {self.sourceFontName}\n\n'

        # get target fonts
        targetFonts = [OpenFont(targetFontPath, showInterface=False) for targetFontPath in self.targetFontPaths]

        txt += validateFonts(targetFonts, sourceFont, width=options['width'], points=options['points'], components=options['components'], anchors=options['anchors'], unicodes=options['unicodes'])
        txt += '...done.\n'

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

        sourceGlyphsFolder = os.path.join(self.sourceFontPath, 'glyphs')
        sourceGlyphSet = GlyphSet(sourceGlyphsFolder)
        sourceGlyph = Glyph()
        # sourceGlyph.lib = {}
        sourceGlyphSet.readGlyph(self.selectedGlyph, glyphObject=sourceGlyph)

        items = []
        for targetFontPath in self.targetFontPaths:
            targetGlyphsFolder = os.path.join(targetFontPath, 'glyphs')
            targetGlyphSet = GlyphSet(targetGlyphsFolder)

            targetName = os.path.splitext(os.path.split(targetFontPath)[-1])[0]
            item = {}
            item['source'] = targetName

            if self.selectedGlyph not in targetGlyphSet:
                item['width']      = '⚪'
                item['points']     = '⚪'
                item['components'] = '⚪'
                item['anchors']    = '⚪'
                item['unicodes']   = '⚪'
            else:
                targetGlyph = Glyph()
                # targetGlyph.lib = {}
                targetGlyphSet.readGlyph(self.selectedGlyph, glyphObject=targetGlyph)
                # sourceGlyph = RGlyph(sourceGlyph)
                # targetGlyph = RGlyph(targetGlyph)
                results = validateGlyph(sourceGlyph, targetGlyph)
                item['width']      = '🟢' if results['width']      else '🔴'
                item['points']     = '🟢' if results['points']     else '🔴'
                item['components'] = '🟢' if results['components'] else '🔴'
                item['anchors']    = '🟢' if results['anchors']    else '🔴'
                item['unicodes']   = '🟢' if results['unicodes']   else '🔴'

            items.append(item)

        tab.results.set(items)

    def editGlyphsCallback(self, sender):
        pass

    def closeCallback(self, sender):
        font = CurrentFont()
        if font is None:
            return
        # removeObserver(self, "glyphCellDrawBackground")
        # removeObserver(self, "drawBackground")
        # removeObserver(self, "currentGlyphChanged")
        # unregisterRepresentationFactory(Glyph, f"{self.key}.preview")
        # self.updateGlyphViewCallback(sender)
        # self.updateFontViewCallback(sender)

# ----
# test
# ----

if __name__ == '__main__':

    OpenWindow(SourceValidator)

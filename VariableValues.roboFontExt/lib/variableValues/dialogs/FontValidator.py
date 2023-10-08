from importlib import reload
import variableValues.validation
reload(variableValues.validation)

import os
import AppKit
from vanilla import *
from random import random
from mojo import drawingTools as ctx
from mojo.UI import UpdateCurrentGlyphView, GetFile, OutputWindow
from mojo.events import addObserver, removeObserver
from mojo.roboFont import OpenFont, OpenWindow, CurrentFont, RGlyph
from variableValues.validation import *
from defcon import Glyph, registerRepresentationFactory, unregisterRepresentationFactory


def glyphChecksFactory(glyph, referenceGlyph):
    glyph = RGlyph(glyph)
    return {
        'width'      : validateWidth(glyph, referenceGlyph),
        'points'     : validateContours(glyph, referenceGlyph),
        'components' : validateComponents(glyph, referenceGlyph),
        'anchors'    : validateAnchors(glyph, referenceGlyph),
        'unicodes'   : validateUnicodes(glyph, referenceGlyph),
    }


class FontValidator:

    title        = 'FontValidator'
    key          = 'com.fontBureau.variableValues.fontValidator'
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
        self.w.tabs = Tabs((x, y, -p, -(self.lineHeight + p*2)), self._tabsTitles)

        self.initializeSetupTab()
        self.initializeResultTab()

        y = -(self.lineHeight + p)
        self.w.validateButton = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'validate',
                callback=self.batchValidateFontsCallback)

        self.w.bind("close", self.closeCallback)
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()
        registerRepresentationFactory(Glyph, f"{self.key}.preview", glyphChecksFactory)
        # addObserver(self, "updateGlyphChecks", "currentGlyphChanged")
        addObserver(self, "drawLabelsCell",    "glyphCellDrawBackground")
        addObserver(self, "drawLabelsGlyph",   "drawBackground")

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

        tab.previewLabel = TextBox(
                (x2 + p*2, y, -p, self.lineHeight),
                'preview')

        y += self.lineHeight #+ p/2
        tab.markFont = CheckBox(
                (x2 + p*1.5, y, -p, self.lineHeight),
                'font',
                value=False,
                callback=self.updateFontViewCallback)

        y += self.lineHeight
        tab.markGlyph = CheckBox(
                (x2 + p*1.5, y, -p, self.lineHeight),
                'glyph',
                value=False,
                callback=self.updateGlyphViewCallback)

        y += self.lineHeight + p
        tab.checksLabel = TextBox(
                (x2 + p*1.5, y, -p, self.lineHeight),
                'marks')

        y += self.lineHeight #+ p/2
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

        print('batch validating fonts...\n')

        # for check, value in self.checks.items():
        #     print(f'- {check}: {value}')
        # print()

        # get source font
        sourceFont = self.sourceFont # OpenFont(self.sourceFontPath, showInterface=False)
        print(f'\tsource font: {self.sourceFontName}\n')

        # get target fonts
        targetFonts = [OpenFont(targetFontPath, showInterface=False) for targetFontPath in self.targetFontPaths]

        # load glyphs into UI
        tab = self._tabs['glyphs']
        tab.glyphs.set(sourceFont.glyphOrder)

        self.results = validateFonts2(targetFonts, sourceFont, width=options['width'], points=options['points'], components=options['components'], anchors=options['anchors'], unicodes=options['unicodes'])

        # print report to the console
        # report = validateFonts(targetFonts, sourceFont, width=options['width'], points=options['points'], components=options['components'], anchors=options['anchors'], unicodes=options['unicodes'])
        # O = OutputWindow()
        # O.clear()
        # O.write(report)
        # O.show()

        # done
        print('...done.\n')

    def selectGlyphCallback(self, sender):
        if not self.selectedGlyph:
            return 

        tab = self._tabs['glyphs']

        items = []
        for fontName, data in self.results.items():
            item = {}
            item['source'] = fontName
            glyphData = data.get(self.selectedGlyph)
            if glyphData is None:
                item['width']      = '⚪'
                item['points']     = '⚪'
                item['components'] = '⚪'
                item['anchors']    = '⚪'
                item['unicodes']   = '⚪'
            else:
                item['width']      = '🟢' if glyphData['width']      else '🔴'
                item['points']     = '🟢' if glyphData['points']     else '🔴'
                item['components'] = '🟢' if glyphData['components'] else '🔴'
                item['anchors']    = '🟢' if glyphData['anchors']    else '🔴'
                item['unicodes']   = '🟢' if glyphData['unicodes']   else '🔴'

            items.append(item)

        tab.results.set(items)

    def updateGlyphViewCallback(self, sender):
        UpdateCurrentGlyphView()

    def updateFontViewCallback(self, sender):
        font = CurrentFont()
        if font is None:
            return
        for g in font:
            g.changed()

    def closeCallback(self, sender):
        font = CurrentFont()
        if font is None:
            return
        removeObserver(self, "glyphCellDrawBackground")
        removeObserver(self, "drawBackground")
        # removeObserver(self, "currentGlyphChanged")
        unregisterRepresentationFactory(Glyph, f"{self.key}.preview")
        self.updateGlyphViewCallback(sender)
        self.updateFontViewCallback(sender)

    # ---------
    # observers
    # ---------

    def drawLabelsCell(self, notification):

        if self.sourceFont is None:
            return

        if not self.markFont:
            return

        g1 = notification['glyph']
        
        if g1 is None:
            return

        if g1.name not in self.sourceFont:
            return

        g2 = self.sourceFont[g1.name]

        # get result
        resultsGlyph = g1.getRepresentation(f"{self.key}.preview", referenceGlyph=g2)

        if not len(resultsGlyph):
            return

        ctx.save()
        ctx.font('Menlo-Bold')
        ctx.fontSize(11)
        ctx.translate(3, 3)
        for check in resultsGlyph.keys():
            if check not in self.showMarks:
                continue
            if resultsGlyph[check]:
                ctx.fill(*self.colorTrue)
            else:
                ctx.fill(*self.colorFalse)
            label = check[0].upper()
            w, h = ctx.textSize(label)
            ctx.text(label, (0, -4))
            ctx.translate(w + 2, 0)
        ctx.restore()

    def drawLabelsGlyph(self, notification):

        if self.sourceFont is None:
            return

        if not self.markGlyph:
            return

        g1 = notification['glyph']
        scale = notification['scale']
        
        if g1 is None:
            return

        if g1.name not in self.sourceFont:
            return

        g2 = self.sourceFont[g1.name]

        # get result
        resultsGlyph = g1.getRepresentation(f"{self.key}.preview", referenceGlyph=g2)

        ctx.save()
        ctx.font('Menlo-Bold')
        ctx.fontSize(12 * scale)
        for check in resultsGlyph.keys():
            if check not in self.showMarks:
                continue
            if resultsGlyph[check]:
                ctx.fill(*self.colorTrue)
            else:
                ctx.fill(*self.colorFalse)
            label = check[0].upper()
            ctx.text(label, (4, 4))
            w, h = ctx.textSize(label)
            ctx.translate(w + 2 * scale, 0)
        ctx.restore()


# ----
# test
# ----

if __name__ == '__main__':

    OpenWindow(FontValidator)

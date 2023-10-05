from importlib import reload
import variableValues.validation
reload(variableValues.validation)

import os
import AppKit
from vanilla import *
from mojo import drawingTools as ctx
from mojo.UI import UpdateCurrentGlyphView, GetFile, OutputWindow
from mojo.events import addObserver, removeObserver
from mojo.roboFont import OpenFont, OpenWindow, CurrentFont
from variableValues.validation import *


class FontValidator:

    title        = 'FontValidator'
    padding      = 10
    lineHeight   = 22
    buttonWidth  = 100
    _tabsTitles  = ['fonts', 'glyphs']
    _checks      = ['width', 'points', 'components', 'anchors', 'unicodes']
    _colLeft     = 123
    _colValue    = 20
    colorTrue    = 0, 1, 0
    colorFalse   = 1, 0, 0
    _sources     = {}
    _targets     = {}
    results      = {}
    resultsGlyph = {}
    verbose      = True

    def __init__(self):
        self.w = FloatingWindow((800, 600), minSize=(580, 400), title=self.title)

        x = y = p = self.padding
        self.w.tabs = Tabs((x, y, -p, -p), self._tabsTitles)

        self.initializeSetupTab()
        self.initializeResultTab()

        self.w.bind("close", self.closeCallback)
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

        addObserver(self, "updateGlyphChecks", "currentGlyphChanged")
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
        x2 = x + self._colLeft + p

        tab.previewLabel = TextBox(
                (x, y, self._colLeft, self.lineHeight),
                'preview')

        y += self.lineHeight #+ p/2
        tab.markFont = CheckBox(
                (x, y, self._colLeft, self.lineHeight),
                'font',
                value=False,
                # callback=self.updateFontViewCallback
                )

        y += self.lineHeight
        tab.markGlyph = CheckBox(
                (x, y, self._colLeft, self.lineHeight),
                'glyph',
                value=False,
                callback=self.updateGlyphViewCallback)

        y += self.lineHeight + p
        tab.checksLabel = TextBox(
                (x, y, self._colLeft, self.lineHeight),
                'marks')

        y += self.lineHeight #+ p/2
        for check in self._checks:
            checkbox = CheckBox(
                (x, y, self._colLeft, self.lineHeight),
                check, value=True)
            setattr(tab, check, checkbox)
            y += self.lineHeight

        y = p/2
        tab.sourcesLabel = TextBox(
                (x2, y, -p, self.lineHeight),
                'reference font')

        y += self.lineHeight + p/2
        tab.sources = List(
                (x2, y, -p, self.lineHeight*3),
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
                (x2, y, -p, self.lineHeight),
                'other fonts')

        y += self.lineHeight + p/2
        tab.targets = List(
                (x2, y, -p, -(self.lineHeight + p*2)),
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
                (x2, y, self.buttonWidth, self.lineHeight),
                'validate',
                callback=self.batchValidateFontsCallback,
                sizeStyle='small')

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

        columnDescriptions = [{ "title": "source", "width": self._colValue*8, "maxWidth": self._colValue*12  }]
        for check in self._checks:
            columnDescriptions.append({ "title": check[0].upper(), "width": self._colValue })

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
                item['W'] = '✖️'
                item['P'] = '✖️'
                item['C'] = '✖️'
                item['A'] = '✖️'
                item['U'] = '✖️'
            else:
                item['W'] = '🟢' if glyphData['width']      else '🔴'
                item['P'] = '🟢' if glyphData['points']     else '🔴'
                item['C'] = '🟢' if glyphData['components'] else '🔴'
                item['A'] = '🟢' if glyphData['anchors']    else '🔴'
                item['U'] = '🟢' if glyphData['unicodes']   else '🔴'

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
        removeObserver(self, "currentGlyphChanged")
        self.updateGlyphViewCallback(sender)
        # self.updateFontViewCallback(sender)

    # ---------
    # observers
    # ---------

    def updateGlyphChecks(self, notification):
        glyph = notification['glyph']
        if not glyph:
            return
        self.checkGlyph(glyph)

    def drawLabelsCell(self, notification):

        if not self.sourceFont:
            return

        if not self.markFont:
            return

        glyph = notification['glyph']
        
        self.checkGlyph(glyph)

        # if not len(self.checks):
        #     return

        ctx.save()
        ctx.font('Menlo-Bold')
        ctx.fontSize(10)
        ctx.translate(3, 3)
        for check in self.resultsGlyph.keys():
            if check not in self.showMarks:
                continue
            if self.resultsGlyph[check]:
                ctx.fill(*self.colorTrue)
            else:
                ctx.fill(*self.colorFalse)
            label = check[0].upper()
            ctx.text(label, (0, -3))
            w, h = ctx.textSize(label)
            ctx.translate(w + 2, 0)
        ctx.restore()

    def drawLabelsGlyph(self, notification):

        if not self.sourceFont:
            return

        if not self.markGlyph:
            return

        glyph = notification['glyph']
        scale = notification['scale']

        self.checkGlyph(glyph)

        ctx.save()
        ctx.font('Menlo-Bold')
        ctx.fontSize(12 * scale)
        for check in self.resultsGlyph.keys():
            if check not in self.showMarks:
                continue
            if self.resultsGlyph[check]:
                ctx.fill(*self.colorTrue)
            else:
                ctx.fill(*self.colorFalse)
            label = check[0].upper()
            ctx.text(label, (4, 4))
            w, h = ctx.textSize(label)
            ctx.translate(w + 2 * scale, 0)
        ctx.restore()

    # -------
    # methods
    # -------

    def checkGlyph(self, g1):
        if g1 is None:
            return

        if self.sourceFont is None:
            if self.verbose:
                print('no reference font selected.')
            return

        if g1.name not in self.sourceFont:
            if self.verbose:
                print(f"glyph '{g1.name}' not in reference font.")
            return

        g2 = self.sourceFont[g1.name]

        self.resultsGlyph = {
            'width'      : validateWidth(g1, g2),
            'points'     : validateContours(g1, g2),
            'components' : validateComponents(g1, g2),
            'anchors'    : validateAnchors(g1, g2),
            'unicodes'   : validateUnicodes(g1, g2),
        }


# ----
# test
# ----

if __name__ == '__main__':

    OpenWindow(FontValidator)

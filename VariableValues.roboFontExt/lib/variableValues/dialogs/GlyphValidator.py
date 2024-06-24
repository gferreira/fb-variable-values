from importlib import reload
import variableValues.validation
reload(variableValues.validation)

from vanilla import FloatingWindow, Button, TextBox, CheckBox
from mojo import drawingTools as ctx
from mojo.UI import UpdateCurrentGlyphView, GetFile
from mojo.events import addObserver, removeObserver
from mojo.roboFont import OpenWindow, CurrentFont
from variableValues.validation import *


class GlyphValidator:

    title       = "validator"
    width       = 123
    padding     = 10
    lineHeight  = 20
    verbose     = False
    
    defaultPath = None
    defaultFont = None

    measurementPath = None
    measurementFont = None

    colorCheckTrue   = 0.00, 0.85, 0.00
    colorCheckFalse  = 1.00, 0.00, 0.00
    colorCheckEqual  = 0.00, 0.33, 1.00

    checks = {
        'width'      : True,
        'left'       : False,
        'right'      : False,
        'points'     : True,
        'components' : True,
        'anchors'    : True,
        'unicodes'   : True,
    }
    checkResults = {}

    def __init__(self):
        self.height  = len(self.checks) * self.lineHeight
        self.height += self.lineHeight * 7
        self.height += self.padding * 5.5
        self.w = FloatingWindow((self.width, self.height), self.title)

        x = y = p = self.padding
        self.w.getDefaultButton = Button(
                (x, y, -p, self.lineHeight),
                'get default...',
                callback=self.getDefaultCallback,
                sizeStyle='small',
            )

        y += self.lineHeight + p/2
        self.w.reloadDefaultButton = Button(
                (x, y, -p, self.lineHeight),
                'reload ↺',
                callback=self.reloadDefaultCallback,
                sizeStyle='small',
            )

        y += self.lineHeight + p
        self.w.checksLabel = TextBox(
                (x, y, -p, self.lineHeight),
                "checks",
                sizeStyle='small')

        y += self.lineHeight
        for checkName, checkValue in self.checks.items():
            checkbox = CheckBox(
                (x, y, -p, self.lineHeight),
                checkName,
                value=checkValue,
                callback=self.updateFontViewCallback,
                sizeStyle='small')
            setattr(self.w, checkName, checkbox)
            y += self.lineHeight

        y += p
        self.w.displayLabel = TextBox(
                (x, y, -p, self.lineHeight),
                "display",
                sizeStyle='small')

        y += self.lineHeight
        self.w.labelsCells = CheckBox(
                (x, y, -p, self.lineHeight),
                "font window",
                value=True,
                callback=self.updateFontViewCallback,
                sizeStyle='small')

        y += self.lineHeight
        self.w.labelsGlyphs = CheckBox(
                (x, y, -p, self.lineHeight),
                "glyph window",
                value=True,
                callback=self.updateGlyphViewCallback,
                sizeStyle='small')

        y += self.lineHeight + p
        self.w.markGlyphs = Button(
                (x, y, -p, self.lineHeight),
                'mark glyphs',
                callback=self.markColorsCallback,
                sizeStyle='small',
            )


        self.w.bind("close", self.closeCallback)
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

        addObserver(self, "updateGlyphChecks", "currentGlyphChanged")
        addObserver(self, "drawLabelsCell",    "glyphCellDrawBackground")
        addObserver(self, "drawLabelsGlyph",   "drawBackground")

    # methods

    def checkGlyph(self, g1):

        self.checkResults = {
            'compatibility' : {},
            'equality'      : {},
        }

        if g1 is None:
            return

        if self.defaultFont is None:
            if self.verbose:
                print('no default source selected.')
            return

        if g1.name not in self.defaultFont:
            if self.verbose:
                print(f"glyph '{g1.name}' not in default source.")
            return

        g2 = self.defaultFont[g1.name]
        self.checkResults['compatibility'] = checkCompatibility(g1, g2)
        self.checkResults['equality']      = checkEquality(g1, g2)

    # callbacks

    def getDefaultCallback(self, sender):
        self.defaultPath = GetFile(message='Get default source…', title=self.title)
        self.defaultFont = OpenFont(defaultPath, showInterface=False)
        self.updateGlyphViewCallback(sender)
        self.updateFontViewCallback(sender)

    def reloadDefaultCallback(self, sender):
        if self.defaultFont is None:
            return
        self.defaultFont = OpenFont(self.defaultPath, showInterface=False)

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
        self.updateFontViewCallback(sender)

    # observers

    def updateGlyphChecks(self, notification):
        glyph = notification['glyph']
        self.checkGlyph(glyph)

    def drawLabelsCell(self, notification):
        if not self.w.labelsCells.get():
            return

        glyph = notification['glyph']

        self.checkGlyph(glyph)

        if not len(self.checks) or not self.checkResults['compatibility'] or not self.checkResults['equality']:
            return

        ctx.save()
        ctx.font('Menlo-Bold')
        ctx.fontSize(10)
        ctx.translate(3, 3)
        for checkName in self.checks.keys():
            checkbox = getattr(self.w, checkName)
            # check is hidden
            if not checkbox.get():
                continue
            isCompatible = self.checkResults['compatibility'].get(checkName)
            isEqual      = self.checkResults['equality'].get(checkName)
            if isCompatible and isEqual:
                ctx.fill(*self.colorCheckEqual)
            elif isCompatible or isEqual:
                ctx.fill(*self.colorCheckTrue)
            else:
                ctx.fill(*self.colorCheckFalse)
            # draw check label
            label = checkName[0].upper()
            ctx.text(label, (0, -3))
            w, h = ctx.textSize(label)
            ctx.translate(w + 2, 0)
        ctx.restore()

    def drawLabelsGlyph(self, notification):
        if not self.w.labelsGlyphs.get():
            return

        glyph = notification['glyph']
        scale = notification['scale']

        self.checkGlyph(glyph)

        x, y = 4, 4

        ctx.save()
        ctx.font('Menlo-Bold')
        ctx.fontSize(12 * scale)

        ctx.save()
        for checkName in self.checks.keys():
            checkbox = getattr(self.w, checkName)
            # check is hidden
            if not checkbox.get():
                continue
            isCompatible = self.checkResults['compatibility'].get(checkName)
            isEqual      = self.checkResults['equality'].get(checkName)
            if isCompatible and isEqual:
                ctx.fill(*self.colorCheckEqual)
            elif isCompatible or isEqual:
                ctx.fill(*self.colorCheckTrue)
            else:
                ctx.fill(*self.colorCheckFalse)
            # draw check label
            label = checkName[0].upper()
            ctx.text(label, (x, y))
            w, h = ctx.textSize(label)
            ctx.translate(w + 2 * scale, 0)
        ctx.restore()
        
        ctx.restore()

    def markColorsCallback(self, sender):

        currentFont = CurrentFont()
        defaultFont = self.defaultFont

        if currentFont is None or defaultFont is None:
            return

        applyValidationColors(currentFont, defaultFont)


if __name__ == '__main__':

    OpenWindow(GlyphValidator)

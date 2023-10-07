from vanilla import FloatingWindow, Button, TextBox, CheckBox
from mojo import drawingTools as ctx
from mojo.UI import UpdateCurrentGlyphView, GetFile
from mojo.events import addObserver, removeObserver
from mojo.roboFont import OpenWindow, CurrentFont
from variableValues.validation import *


### DEPRECATED : use FontValidator ###


class GlyphValidator:

    title       = "validate"
    width       = 123
    padding     = 10
    lineHeight  = 20
    verbose     = False
    defaultFont = None

    colorTrue   = 0, 1, 0
    colorFalse  = 1, 0, 0

    checks = [
        'width',
        'points',
        'components',
        'anchors',
        'unicodes',
    ]
    checkResults = {}

    def __init__(self):
        self.height = (len(self.checks) + 5) * self.lineHeight + self.padding * 4
        self.w = FloatingWindow((self.width, self.height), self.title)

        x = y = p = self.padding
        self.w.getDefaultButton = Button(
                (x, y, -p, self.lineHeight),
                'get default...',
                callback=self.getDefaultCallback,
                sizeStyle='small',
            )

        y += self.lineHeight + p
        self.w.checksLabel = TextBox(
                (x, y, -p, self.lineHeight),
                "glyph checks",
                sizeStyle='small')

        y += self.lineHeight # + p
        for check in self.checks:
            checkbox = CheckBox(
                (x, y, -p, self.lineHeight),
                check,
                value=True,
                callback=self.updateFontViewCallback,
                sizeStyle='small')
            setattr(self.w, check, checkbox)
            y += self.lineHeight

        y += p
        self.w.markLabel = TextBox(
                (x, y, -p, self.lineHeight),
                "show marks",
                sizeStyle='small')

        y += self.lineHeight
        self.w.markCells = CheckBox(
                (x, y, -p, self.lineHeight),
                "font window",
                value=True,
                callback=self.updateFontViewCallback,
                sizeStyle='small')

        y += self.lineHeight
        self.w.markGlyphs = CheckBox(
                (x, y, -p, self.lineHeight),
                "glyph window",
                value=True,
                callback=self.updateGlyphViewCallback,
                sizeStyle='small')


        self.w.bind("close", self.closeCallback)
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

        addObserver(self, "updateGlyphChecks", "currentGlyphChanged")
        addObserver(self, "drawLabelsCell",    "glyphCellDrawBackground")
        addObserver(self, "drawLabelsGlyph",   "drawBackground")

    # methods

    def checkGlyph(self, g1):
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

        self.checkResults = {
            'width'      : validateWidth(g1, g2),
            'points'     : validateContours(g1, g2),
            'components' : validateComponents(g1, g2),
            'anchors'    : validateAnchors(g1, g2),
            'unicodes'   : validateUnicodes(g1, g2),
        }

    # callbacks

    def getDefaultCallback(self, sender):
        defaultPath = GetFile(message='Get default source…', title=self.title)
        self.defaultFont = OpenFont(defaultPath, showInterface=False)
        self.updateGlyphViewCallback(sender)
        self.updateFontViewCallback(sender)

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
        if not self.w.markCells.get():
            return

        glyph = notification['glyph']
        
        self.checkGlyph(glyph)

        if not len(self.checks):
            return

        ctx.save()
        ctx.font('Menlo-Bold')
        ctx.fontSize(10)
        ctx.translate(3, 3)
        for check in self.checkResults.keys():
            checkbox = getattr(self.w, check)
            if not checkbox.get():
                continue
            if self.checkResults[check]:
                ctx.fill(*self.colorTrue)
            else:
                ctx.fill(*self.colorFalse)
            label = check[0].upper()
            ctx.text(label, (0, -3))
            w, h = ctx.textSize(label)
            ctx.translate(w + 2, 0)
        ctx.restore()

    def drawLabelsGlyph(self, notification):
        if not self.w.markGlyphs.get():
            return

        glyph = notification['glyph']
        scale = notification['scale']

        self.checkGlyph(glyph)

        ctx.save()
        ctx.font('Menlo-Bold')
        ctx.fontSize(12 * scale)
        for check in self.checkResults.keys():
            checkbox = getattr(self.w, check)
            if not checkbox.get():
                continue
            if self.checkResults[check]:
                ctx.fill(*self.colorTrue)
            else:
                ctx.fill(*self.colorFalse)
            label = check[0].upper()
            ctx.text(label, (4, 4))
            w, h = ctx.textSize(label)
            ctx.translate(w + 2 * scale, 0)
        ctx.restore()


if __name__ == '__main__':

    OpenWindow(GlyphValidator)

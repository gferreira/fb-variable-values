from vanilla import FloatingWindow, Button, CheckBox
from mojo import drawingTools as ctx
from mojo.UI import UpdateCurrentGlyphView, GetFile
from mojo.events import addObserver, removeObserver
from mojo.roboFont import OpenWindow
from variableValues.validation import *


class GlyphValidator:

    title = "GlyphValidator"
    defaultSource = None
    padding = 10
    textHeight = 20

    checks = {}

    def __init__(self):
        h = self.textHeight*2 + self.padding*3
        self.w = FloatingWindow((200, h), self.title)

        x = y = p = self.padding
        self.w.getDefaultButton = Button(
                (x, y, -p, self.textHeight),
                'get default source...',
                callback=self.getDefaultCallback,
                sizeStyle='small',
            )
        y += self.textHeight + p
        self.w.showPreview = CheckBox(
                (x, y, -p, self.textHeight),
                "show test results",
                value=True,
                callback=self.updatePreviewCallback,
                sizeStyle='small')

        self.w.bind("close", self.closeCallback)
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

        addObserver(self, "drawCell",      "glyphCellDrawBackground")
        addObserver(self, "drawCallback",  "drawBackground")
        addObserver(self, "glyphChanged",  "currentGlyphChanged")

    def glyphChanged(self, notification):
        glyph = notification['glyph']        
        self.checkGlyph(glyph)
        
    def checkGlyph(self, g1):
        if g1 is None:
            return
        if self.defaultSource is None:
            print('no default source selected.')
            return
        if g1.name not in self.defaultSource:
            print(f"glyph '{g1.name}' not in default source.")
            return

        g2 = self.defaultSource[g1.name]

        self.checks = {
            'width'      : validateWidth(g1, g2),
            'points'     : validateContours(g1, g2),
            'components' : validateComponents(g1, g2),
            'anchors'    : validateAnchors(g1, g2),
            'unicodes'   : validateUnicodes(g1, g2),
        }

    def drawCell(self, info):
        if not self.w.showPreview.get():
            return

        glyph = info['glyph']
        
        self.checkGlyph(glyph)

        if not len(self.checks):
            return

        ctx.save()
        ctx.font('Menlo-Bold')
        ctx.fontSize(10)
        ctx.translate(3, 3)
        for check in self.checks.keys():
            if self.checks[check]:
                ctx.fill(0, 1, 0)
            else:
                ctx.fill(1, 0, 0)
            ctx.text(check[0].upper(), (0, -3))
            w, h = ctx.textSize(check[0].upper())
            ctx.translate(w+2, 0)
        ctx.restore()

    def drawCallback(self, notification):
        if not self.w.showPreview.get():
            return

        glyph = notification['glyph']
        scale = notification['scale']

        font = glyph.font

        self.checkGlyph(glyph)

        ctx.save()
        ctx.fontSize(12*scale)
        for check in self.checks.keys():
            if self.checks[check] is True:
                ctx.fill(0, 1, 0.2)
            else:
                ctx.fill(1, 0, 0)
            ctx.text(check[0].upper(), (4, 4))
            w, h = ctx.textSize(check[0].upper())
            ctx.translate(w+2*scale, 0)    
        ctx.restore()

    def updatePreviewCallback(self, sender):
        UpdateCurrentGlyphView()

    def getDefaultCallback(self, sender):
        defaultPath = GetFile(message='Get default source…', title=self.title)
        self.defaultSource = OpenFont(defaultPath, showInterface=False)

    def closeCallback(self, sender):
        font = CurrentFont()
        if font is None:
            return
        removeObserver(self, "glyphCellDrawBackground")
        removeObserver(self, "drawBackground")
        removeObserver(self, "currentGlyphChanged")


if __name__ == '__main__':

    OpenWindow(GlyphValidator)

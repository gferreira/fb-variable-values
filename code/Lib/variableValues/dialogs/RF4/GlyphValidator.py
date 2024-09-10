import ezui
from defcon import Glyph, registerRepresentationFactory, unregisterRepresentationFactory
from mojo import drawingTools as ctx
from mojo.UI import UpdateCurrentGlyphView, GetFile
from mojo.roboFont import OpenFont, CurrentFont, RGlyph, OpenWindow
from mojo.events import addObserver, removeObserver
from variableValues.validation import *

'''
Partial upgrade to EZUI + representations.

TO-DO: upgrade to Subscriber + Merz

'''


def checkResultsFactory(glyph, defaultGlyph=None):
    if defaultGlyph is None:
        defaultGlyph = RGlyph()
    glyph = glyph.asFontParts()
    checkResults = {
        'compatibility' : checkCompatibility(glyph, defaultGlyph),
        'equality'      : checkEquality(glyph, defaultGlyph),
    }
    return checkResults


class GlyphValidator_EZUI(ezui.WindowController):

    title = 'validator'
    key   = 'com.fontBureau.glyphValidator'
    width = 123

    defaultPath = None
    defaultFont = None

    colorCheckTrue  = 0.00, 0.85, 0.00
    colorCheckFalse = 1.00, 0.00, 0.00
    colorCheckEqual = 0.00, 0.33, 1.00

    content = """
    ( get default… )   @getDefaultButton
    ( reload ↺ )       @reloadButton

    checks
    [X] width          @widthCheck
    [ ] left           @leftCheck
    [ ] right          @rightCheck
    [X] points         @pointsCheck
    [X] components     @componentsCheck
    [X] anchors        @anchorsCheck
    [X] unicodes       @unicodesCheck

    display
    [X] font overview  @displayFontOverview
    [X] glyph window   @displayGlyphWindow

    ( mark glyphs )    @markGlyphsButton
    """

    descriptionData = dict(
        content=dict(
            sizeStyle="small",
        ),
        getDefaultButton=dict(
            width='fill',
        ),
        reloadButton=dict(
            width='fill',
        ),
        markGlyphsButton=dict(
            width='fill',
        ),
    )

    def build(self):
        self.w = ezui.EZPanel(
            title=self.title,
            content=self.content,
            descriptionData=self.descriptionData,
            controller=self,
            size=(self.width, 'auto'),
        )

    def started(self):
        registerRepresentationFactory(Glyph, f"{self.key}.checkResults", checkResultsFactory)
        # addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
        addObserver(self, "drawCheckResultsFontOverview", "glyphCellDrawBackground")
        addObserver(self, "drawCheckResultsGlyphEditor", "drawBackground")
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

    def destroy(self):
        unregisterRepresentationFactory(Glyph, f"{self.key}.checkResults")
        # removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "glyphCellDrawBackground")
        removeObserver(self, "drawBackground")
        self.updateGlyphViewCallback(None)
        self.updateFontViewCallback(None)

    # dynamic attrs

    @property
    def checks(self):
        checkNames = ['width', 'left', 'right', 'points', 'components', 'anchors', 'unicodes']
        checksDisplay = {}
        for checkName in checkNames:
            checkBoxName = f'{checkName}Check' 
            checkBox = self.w.getItem(checkBoxName)
            checksDisplay[checkName] = checkBox.get()
        return checksDisplay

    # callbacks

    def getDefaultButtonCallback(self, sender):
        self.defaultPath = GetFile(message='Get default source…', title=self.title)
        self.defaultFont = OpenFont(self.defaultPath, showInterface=False)
        self.updateGlyphViewCallback(sender)
        self.updateFontViewCallback(sender)

    def reloadButtonCallback(self, sender):
        if self.defaultFont is None:
            return
        self.defaultFont = OpenFont(self.defaultPath, showInterface=False)

    def markGlyphsButtonCallback(self, sender):
        currentFont = CurrentFont()
        defaultFont = self.defaultFont

        if currentFont is None or defaultFont is None:
            return

        applyValidationColors(currentFont, defaultFont)

    def updateFontViewCallback(self, sender):
        font = CurrentFont()
        if font is None:
            return
        for g in font:
            g.changed()

    def updateGlyphViewCallback(self, sender):
        UpdateCurrentGlyphView()

    def widthCheckCallback(self, sender):
        self.updateFontViewCallback(sender)
        self.updateGlyphViewCallback(sender)

    def leftCheckCallback(self, sender):
        self.updateFontViewCallback(sender)
        self.updateGlyphViewCallback(sender)

    def rightCheckCallback(self, sender):
        self.updateFontViewCallback(sender)
        self.updateGlyphViewCallback(sender)

    def pointsCheckCallback(self, sender):
        self.updateFontViewCallback(sender)
        self.updateGlyphViewCallback(sender)

    def componentsCheckCallback(self, sender):
        self.updateFontViewCallback(sender)
        self.updateGlyphViewCallback(sender)

    def anchorsCheckCallback(self, sender):
        self.updateFontViewCallback(sender)
        self.updateGlyphViewCallback(sender)

    def unicodesCheckCallback(self, sender):
        self.updateFontViewCallback(sender)
        self.updateGlyphViewCallback(sender)

    def displayFontOverviewCallback(self, sender):
        self.updateFontViewCallback(sender)

    def displayGlyphWindowCallback(self, sender):
        self.updateGlyphViewCallback(sender)

    # drawing

    def drawCheckResultsFontOverview(self, notification):
        if not self.w.getItem("displayFontOverview"):
            return

        if self.defaultFont is None:
            return

        glyph = notification['glyph']

        if glyph.name not in self.defaultFont:
            return

        defaultGlyph = self.defaultFont[glyph.name]
        checkResults = glyph.getRepresentation(f"{self.key}.checkResults", defaultGlyph=defaultGlyph)

        if not len(self.checks) or not checkResults['compatibility'] or not checkResults['equality']:
            return

        ctx.save()
        ctx.font('LucidaGrande-Bold')
        ctx.fontSize(10)
        ctx.translate(3, 5)
        for checkName, checkDisplay in self.checks.items():
            # check is hidden
            if not checkDisplay:
                continue
            isCompatible = checkResults['compatibility'].get(checkName)
            isEqual      = checkResults['equality'].get(checkName)
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

    def drawCheckResultsGlyphEditor(self, notification):
        if not self.w.getItem("displayGlyphWindow"):
            return

        if self.defaultFont is None:
            return

        glyph = notification['glyph']
        scale = notification['scale']

        if glyph.name not in self.defaultFont:
            return

        defaultGlyph = self.defaultFont[glyph.name]
        checkResults = glyph.getRepresentation(f"{self.key}.checkResults", defaultGlyph=defaultGlyph)

        if not len(self.checks) or not checkResults['compatibility'] or not checkResults['equality']:
            return

        x, y = 3, 3

        ctx.save()
        ctx.font('LucidaGrande-Bold')
        ctx.fontSize(12 * scale)

        ctx.save()
        for checkName, checkDisplay in self.checks.items():
            if not checkDisplay:
                continue
            isCompatible = checkResults['compatibility'].get(checkName)
            isEqual      = checkResults['equality'].get(checkName)
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



if __name__ == '__main__':

    OpenWindow(GlyphValidator_EZUI)

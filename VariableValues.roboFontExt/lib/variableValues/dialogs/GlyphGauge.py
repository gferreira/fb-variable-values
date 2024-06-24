from importlib import reload
import variableValues.validation
reload(variableValues.validation)

from vanilla import FloatingWindow, Button, TextBox, CheckBox #, Slider
from drawBot import FormattedString
from mojo import drawingTools as ctx
from mojo.UI import UpdateCurrentGlyphView, CurrentGlyphWindow, GetFile
from mojo.events import addObserver, removeObserver
from mojo.roboFont import OpenWindow, CurrentFont
from hTools3.dialogs.misc.numberEditText001 import NumberEditText_001
from variableValues.linkPoints import readMeasurements
from variableValues.measurements import Measurement


class GlyphGauge:

    title       = "gauge"
    width       = 123
    padding     = 10
    lineHeight  = 20
    verbose     = False

    defaultPath = None
    defaultFont = None

    measurementPath = None
    measurementFont = None

    fontMeasurements  = {}
    glyphMeasurements = {}

    colorCheckTrue   = 0.00, 0.85, 0.00
    colorCheckFalse  = 1.00, 0.00, 0.00
    colorCheckEqual  = 0.00, 0.33, 1.00

    settings = {
        'scale' : 0.10,
    }

    def __init__(self):
        self.height  = self.lineHeight*8
        self.height += self.padding*7
        self.w = FloatingWindow((self.width, self.height), self.title)

        x = y = p = self.padding
        self.w.getDefaultButton = Button(
                (x, y, -p, self.lineHeight),
                'get default...',
                callback=self.getDefaultCallback,
                sizeStyle='small')

        y += self.lineHeight + p/2
        self.w.reloadDefaultButton = Button(
                (x, y, -p, self.lineHeight),
                'reload ↺',
                callback=self.reloadDefaultCallback,
                sizeStyle='small')

        y += self.lineHeight + p
        self.w.getMeasurementsButton = Button(
                (x, y, -p, self.lineHeight),
                'measurements...',
                callback=self.getMeasurementsCallback,
                sizeStyle='small')

        y += self.lineHeight + p/2
        self.w.reloadMeasurementsButton = Button(
                (x, y, -p, self.lineHeight),
                'reload ↺',
                callback=self.reloadMeasurementsCallback,
                sizeStyle='small')

        y += self.lineHeight + p
        self.w.permille = CheckBox(
                (x, y, -p, self.lineHeight),
                "per mille",
                value=False,
                callback=self.updateGlyphViewCallback,
                sizeStyle='small')

        y += self.lineHeight + p
        self.w.gaugeToleranceLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'tolerance',
                sizeStyle='small')
        y += self.lineHeight
        self.w.gaugeTolerance = NumberEditText_001(
                (x, y, -p, self.lineHeight),
                text=self.settings['scale'],
                callback=self.updateGlyphViewCallback,
                sizeStyle='small')

        y += self.lineHeight + p
        self.w.display = CheckBox(
                (x, y, -p, self.lineHeight),
                "display",
                value=True,
                callback=self.updateGlyphViewCallback,
                sizeStyle='small')

        self.w.bind("close", self.closeCallback)
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

        addObserver(self, "drawBackground", "drawBackground")

    # methods

    def gaugeGlyph(self, g1):
        pass

    def loadMeasurements(self):
        measurements = readMeasurements(self.measurementsPath)
        self.fontMeasurements  = measurements['font']
        self.glyphMeasurements = measurements['glyphs']

    # callbacks

    def getDefaultCallback(self, sender):
        self.defaultPath = GetFile(message='Get default source…', title=self.title)
        self.defaultFont = OpenFont(self.defaultPath, showInterface=False)
        self.updateGlyphViewCallback(sender)

    def reloadDefaultCallback(self, sender):
        if self.defaultFont is None:
            return
        defaultPath = self.defaultFont.path
        self.defaultFont = OpenFont(defaultPath, showInterface=False)

    def getMeasurementsCallback(self, sender):
        self.measurementsPath = GetFile(message='Get measurements file…', title=self.title)
        self.loadMeasurements()
        self.updateGlyphViewCallback(sender)

    def reloadMeasurementsCallback(self, sender):
        if self.measurementsPath is None:
            return
        self.loadMeasurements()
        self.updateGlyphViewCallback(sender)

    def updateGlyphViewCallback(self, sender):
        UpdateCurrentGlyphView()

    def closeCallback(self, sender):
        font = CurrentFont()
        if font is None:
            return
        removeObserver(self, "drawBackground")
        self.updateGlyphViewCallback(sender)

    # observers

    def drawBackground(self, notification):
        font = CurrentFont()
        if font is None:
            return

        if not self.w.display.get():
            return

        glyph = notification['glyph']
        scale = notification['scale']

        glyphMeasurements = self.glyphMeasurements.get(glyph.name)

        if not glyphMeasurements:
            return

        window = CurrentGlyphWindow()
        x, y, w, h = window.getVisibleRect()

        t = self.w.gaugeTolerance.get()
        permille = self.w.permille.get()

        fs, lh = 12*scale, 14*scale

        ctx.save()
        ctx.fill(0)
        ctx.font('Menlo-Bold')
        ctx.fontSize(fs)
        ctx.lineHeight(lh)

        _x = x + glyph.width + 6*scale
        _y = font.info.capHeight - 12*scale

        # draw table header
        if not permille:
            txt = f"{'name'.ljust(4, ' ')} {'units'.rjust(5, ' ')} {'deflt'.rjust(5, ' ')} {'scale'.rjust(5, ' ')}"
        else:
            txt = f"{'name'.ljust(4, ' ')} {'perml'.rjust(5, ' ')} {'deflt'.rjust(5, ' ')} {'scale'.rjust(5, ' ')}"
        ctx.fill(*self.colorCheckEqual)
        ctx.text(txt, (_x, _y))
        _y -= lh
        ctx.text(f"{'-'*len(txt)}", (_x, _y))
        _y -= lh

        txtMeasurements = []
        for key in glyphMeasurements.keys():
            parts = key.split()

            # get point indexes
            if len(parts) == 2:
                index1, index2 = parts
            else:
                continue
            try:
                index1 = int(index1)
            except:
                pass
            try:
                index2 = int(index2)
            except:
                pass

            # setup measurement
            measurementName = glyphMeasurements[key].get('name')
            M = Measurement(
                measurementName,
                glyphMeasurements[key].get('direction'),
                glyph.name, index1,
                glyph.name, index2,
                glyphMeasurements[key].get('parent'))

            # measure font
            valueUnits = M.measure(font)
            if valueUnits is None:
                valueUnits = valuePermill = '-'
            elif valueUnits == 0:
                valuePermill = 0
            else:
                valuePermill = round(valueUnits*1000 / font.info.unitsPerEm)

            # measure default
            defaultUnits = M.measure(self.defaultFont)
            if defaultUnits is None:
                defaultUnits = defaultPermille = '-'
            elif defaultUnits == 0:
                defaultPermille = 0
            else:
                defaultPermille = round(defaultUnits*1000 / self.defaultFont.info.unitsPerEm)

            # draw table item
            c = 0,

            fontMeasurements = self.fontMeasurements
            if measurementName in fontMeasurements:
                index1 = fontMeasurements[measurementName].get('point 1')
                index2 = fontMeasurements[measurementName].get('point 2')

                try:
                    index1 = int(index1)
                except:
                    pass
                try:
                    index2 = int(index2)
                except:
                    pass

                # calculate scale factor
                if valueUnits == defaultUnits:
                    scaleValue = 1.0
                    c = self.colorCheckEqual
                elif valueUnits == 0 or defaultUnits == 0:
                    scaleValue = '-'
                else:
                    scaleValue = valueUnits / defaultUnits
                    if (1.0 - t) < scaleValue < (1.0 + t):
                        c = self.colorCheckTrue
                    else:
                        c = self.colorCheckFalse
                if not isinstance(scaleValue, str):
                    scaleValue = f"{scaleValue:.2f}"

            else:
                defaultUnits = '-'
                scaleValue = '-'

            if not permille:
                txt = f"{measurementName.ljust(4, ' ')} {str(valueUnits).rjust(5, ' ')} {str(defaultUnits).rjust(5, ' ')} {scaleValue.rjust(5, ' ')}"
            else:
                txt = f"{measurementName.ljust(4, ' ')} {str(valuePermill).rjust(5, ' ')} {str(defaultPermille).rjust(5, ' ')} {scaleValue.rjust(5, ' ')}"

            ctx.fill(*c)
            ctx.text(txt, (_x, _y))
            _y -= lh

        ctx.restore()



if __name__ == '__main__':

    OpenWindow(GlyphGauge)

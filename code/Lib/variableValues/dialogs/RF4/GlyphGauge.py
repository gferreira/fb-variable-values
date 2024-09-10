import ezui
from mojo.UI import GetFile
from mojo.roboFont import OpenWindow, OpenFont
from mojo.subscriber import Subscriber, registerSubscriberEvent, roboFontSubscriberEventRegistry, registerGlyphEditorSubscriber, unregisterGlyphEditorSubscriber
from mojo.events import postEvent
from variableValues.linkPoints import readMeasurements
from variableValues.measurements import Measurement


class GlyphGauge_EZUI(ezui.WindowController):

    title   = 'gauge'
    key     = 'com.fontBureau.glyphGauge'
    width   = 123
    margins = 10

    defaultPath = None
    defaultFont = None

    measurementsPath = None
    measurementsData = None

    content = """
    ( get default… )   @getDefaultButton
    ( reload ↺ )       @reloadDefaultButton

    ( measurements… )  @getMeasurementsButton
    ( reload ↺ )       @reloadMeasurementsButton

    [ ] parent value   @parent
    [ ] per mille      @permille

    tolerance
    [__](±)            @toleranceValue

    [X] display        @display
    """

    colorCheckTrue  = 0.00, 0.85, 0.00, 1.00
    colorCheckFalse = 1.00, 0.00, 0.00, 1.00
    colorCheckEqual = 0.00, 0.33, 1.00, 1.00

    descriptionData = dict(
        content=dict(
            sizeStyle="small",
        ),
        getDefaultButton=dict(
            width='fill',
        ),
        reloadDefaultButton=dict(
            width='fill',
        ),
        getMeasurementsButton=dict(
            width='fill',
        ),
        reloadMeasurementsButton=dict(
            width='fill',
        ),
        toleranceValue=dict(
            callback='settingsChangedCallback',
            valueType="float",
            value=0.10,
            minValue=0.0,
            maxValue=2.0,
            valueIncrement=0.01,
        ),
        display=dict(
            callback='settingsChangedCallback',
        ),
    )

    def build(self):
        self.w = ezui.EZPanel(
            title=self.title,
            content=self.content,
            descriptionData=self.descriptionData,
            controller=self,
            margins=self.margins,
            size=(self.width, 'auto'),
        )
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

    def started(self):
        GlyphGaugeSubscriberGlyphEditor.controller = self
        registerGlyphEditorSubscriber(GlyphGaugeSubscriberGlyphEditor)
        self.settingsChangedCallback(None)

    def destroy(self):
        print('destroy > unregister subscriber')
        unregisterGlyphEditorSubscriber(GlyphGaugeSubscriberGlyphEditor)
        GlyphGaugeSubscriberGlyphEditor.controller = None

    # callbacks

    def getDefaultButtonCallback(self, sender):
        self.defaultPath = GetFile(message='Get default source…', title=self.title)
        self.defaultFont = OpenFont(self.defaultPath, showInterface=False)
        self.settingsChangedCallback(None)

    def reloadButtonCallback(self, sender):
        if self.defaultFont is None:
            return
        self.defaultFont = OpenFont(self.defaultPath, showInterface=False)
        self.settingsChangedCallback(None)

    def getMeasurementsButtonCallback(self, sender):
        self.measurementsPath = GetFile(message='Get measurements file…', title=self.title)
        self.measurementsData = readMeasurements(self.measurementsPath)
        self.settingsChangedCallback(None)

    def reloadMeasurementsButtonCallback(self, sender):
        if self.measurementsPath is None:
            return
        self.measurementsData = readMeasurements(self.measurementsPath)
        self.settingsChangedCallback(None)

    def parentCallback(self, sender):
        self.settingsChangedCallback(None)

    def permilleCallback(self, sender):
        self.settingsChangedCallback(None)

    def settingsChangedCallback(self, sender):
        print('settingsChangedCallback')
        postEvent(f"{self.key}.changed")


class GlyphGaugeSubscriberGlyphEditor(Subscriber):

    controller = None

    def build(self):
        glyphEditor = self.getGlyphEditor()
        container = glyphEditor.extensionContainer(
            identifier=f"{self.controller.key}.foreground",
            location="foreground",
        )
        self.displayLayer = container.appendBaseSublayer()

    def destroy(self):
        print('destroy > clear sublayers')
        self.displayLayer.clearSublayers()

    def glyphEditorDidSetGlyph(self, info):
        self.glyph = info["glyph"]
        self._drawGlyphGauge()

    def glyphEditorGlyphDidChange(self, info):
        self._drawGlyphGauge()

    def glyphGaugeDidChange(self, info):
        self._drawGlyphGauge()

    def _drawGlyphGauge(self):
        self.displayLayer.clearSublayers()

        if self.controller.defaultFont is None:
            return

        if self.glyph.name not in self.controller.defaultFont:
            return

        defaultGlyph = self.controller.defaultFont[self.glyph.name]

        r = 16
        with self.displayLayer.sublayerGroup():
            for ci, c in enumerate(self.glyph):
                for pi, p in enumerate(c.points):
                    p2 = defaultGlyph.contours[ci].points[pi]
                    if p.x == p2.x and p.y == p2.y:
                        color = self.controller.colorCheckTrue
                    else:
                        color = self.controller.colorCheckFalse
                    self.displayLayer.appendOvalSublayer(
                        position=(p.x-r, p.y-r),
                        size=(r*2, r*2),
                        fillColor=color,
                        strokeColor=None,
                    )


eventName = f"{GlyphGauge_EZUI.key}.changed"

if eventName not in roboFontSubscriberEventRegistry:
    registerSubscriberEvent(
        subscriberEventName=eventName,
        methodName="glyphGaugeDidChange",
        lowLevelEventNames=[eventName],
        documentation="Send when the GlyphGauge window changes its parameters.",
        dispatcher="roboFont",
        delay=0,
        debug=True
    )


if __name__ == '__main__':

    OpenWindow(GlyphGauge_EZUI)

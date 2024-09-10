import ezui
from mojo.UI import GetFile
from mojo.roboFont import OpenWindow, OpenFont
from mojo.subscriber import Subscriber, registerSubscriberEvent, roboFontSubscriberEventRegistry, registerGlyphEditorSubscriber, unregisterGlyphEditorSubscriber
from mojo.events import postEvent


class VarGlyphViewer(ezui.WindowController):

    title   = 'varglyph'
    key     = 'com.fontBureau.varGlyphViewer'
    width   = 123
    margins = 10

    defaultPath = None
    defaultFont = None

    content = """
    ( get default… )  @getDefaultButton
    ( reload ↺ )      @reloadDefaultButton
    --X-----          @pointSize
    [X] display       @display
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
        pointSize=dict(
            callback='settingsChangedCallback',
            minValue=10,
            maxValue=24,
            value=16,
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
        VarGlyphViewerSubscriberGlyphEditor.controller = self
        registerGlyphEditorSubscriber(VarGlyphViewerSubscriberGlyphEditor)
        self.settingsChangedCallback(None)

    def destroy(self):
        unregisterGlyphEditorSubscriber(VarGlyphViewerSubscriberGlyphEditor)
        VarGlyphViewerSubscriberGlyphEditor.controller = None

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

    def pointSizeCallback(self, sender):
        self.settingsChangedCallback(None)

    def settingsChangedCallback(self, sender):
        postEvent(f"{self.key}.changed")


class VarGlyphViewerSubscriberGlyphEditor(Subscriber):

    controller = None

    def build(self):
        glyphEditor = self.getGlyphEditor()
        container = glyphEditor.extensionContainer(
            identifier=f"{self.controller.key}.foreground",
            location="foreground",
        )
        self.displayLayer = container.appendBaseSublayer()

    def destroy(self):
        self.displayLayer.clearSublayers()

    def glyphEditorDidSetGlyph(self, info):
        self.glyph = info["glyph"]
        self._drawVarGlyphViewer()

    def glyphEditorGlyphDidChange(self, info):
        self._drawVarGlyphViewer()

    def varGlyphViewerDidChange(self, info):
        self._drawVarGlyphViewer()

    def _drawVarGlyphViewer(self):
        self.displayLayer.clearSublayers()

        if self.controller.defaultFont is None:
            return

        if self.glyph.name not in self.controller.defaultFont:
            return

        defaultGlyph = self.controller.defaultFont[self.glyph.name]
        r = self.controller.w.getItem('pointSize').get()

        defaultLayer = self.displayLayer.appendPathSublayer(
            fillColor=self.controller.colorCheckTrue,
            strokeColor=None,
            opacity=0.3,
        )
        glyphPath = defaultGlyph.getRepresentation("merz.CGPath")
        defaultLayer.setPath(glyphPath)

        with self.displayLayer.sublayerGroup():
            for ci, c in enumerate(self.glyph):
                for pi, p in enumerate(c.points):
                    p2 = defaultGlyph.contours[ci].points[pi]
                    # draw default point
                    color = self.controller.colorCheckTrue
                    self.displayLayer.appendOvalSublayer(
                        position=(p2.x-r, p2.y-r),
                        size=(r*2, r*2),
                        fillColor=color,
                        strokeColor=None,
                    )
                    # point is different than default
                    if not (p.x == p2.x and p.y == p2.y):
                        color = self.controller.colorCheckFalse
                        dash = (2, 2) if p.type == 'offcurve' else None
                        self.displayLayer.appendLineSublayer(
                            startPoint=(p.x, p.y),
                            endPoint=(p2.x, p2.y),
                            strokeWidth=1,
                            strokeColor=color,
                            strokeDash=dash,
                        )
                        self.displayLayer.appendOvalSublayer(
                            position=(p.x-r, p.y-r),
                            size=(r*2, r*2),
                            fillColor=color,
                            strokeColor=None,
                        )

eventName = f"{VarGlyphViewer.key}.changed"

if eventName not in roboFontSubscriberEventRegistry:
    registerSubscriberEvent(
        subscriberEventName=eventName,
        methodName="varGlyphViewerDidChange",
        lowLevelEventNames=[eventName],
        documentation="Send when the VarGlyphViewer window changes its parameters.",
        dispatcher="roboFont",
        delay=0,
        debug=True
    )


if __name__ == '__main__':

    OpenWindow(VarGlyphViewer)

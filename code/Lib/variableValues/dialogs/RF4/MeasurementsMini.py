import AppKit
import ezui
from math import hypot
from mojo.roboFont import OpenWindow
from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber, unregisterGlyphEditorSubscriber, registerSubscriberEvent, roboFontSubscriberEventRegistry
from mojo.events import postEvent


'''
a simple demo tool to define measurements between pairs of points

- open any glyph in the Glyph Editor, select two points
- click on the + button to define a new measurement
- select one or more measurements from the list to display their distance
- click on the color button to choose another display color

'''


DEFAULT_KEY = 'com.measurements.mini'


def getPointAtIndex(glyph, index):
    indexFlat = 0
    pointsFlat = {}
    for contouIndex, contour in enumerate(glyph.contours):
        for pointIndex, point in enumerate(contour.points):
            pointsFlat[indexFlat] = contouIndex, pointIndex
            indexFlat += 1
    if index not in pointsFlat:
        return
    contouIndex, pointIndex = pointsFlat[index]
    return glyph.contours[contouIndex].points[pointIndex]


def getIndexForPoint(glyph, aPoint):
    indexFlat = 0
    for contouIndex, contour in enumerate(glyph.contours):
        for pointIndex, point in enumerate(contour.points):
            if point == aPoint:
                return indexFlat
            indexFlat += 1


class MiniMeasurementsWindowController(ezui.WindowController):

    def build(self):
        content = """
        |-------------------------|
        | point1 | point2 | units | @measurements
        |--------|--------|-------|
        |        |        |       |
        |-------------------------|
        > (+-)                      @measurementsAddRemoveButton
        > * ColorWell               @colorButton
        """
        descriptionData = dict(
            measurements=dict(
                columnDescriptions=[
                    dict(
                        identifier="point1",
                        title="point 1",
                        editable=True,
                        width=60,
                        cellDescription=dict(
                            cellType='TextField',
                            valueType='integer',
                        ),
                    ),
                    dict(
                        identifier="point2",
                        title="point 2",
                        editable=True,
                        width=60,
                        cellDescription=dict(
                            cellType='TextField',
                            valueType='integer',
                        ),
                    ),
                    dict(
                        identifier="units",
                        title="units",
                        editable=False,
                        width=60,
                        cellDescription=dict(
                            cellType='TextField',
                            valueType='integer',
                        ),
                    ),
                ],
                itemPrototype=dict(
                    point1=0,
                    point2=1,
                    units=None,
                ),
            ),
            colorButton=dict(
                width=80,
                color=(1, 0.2, 0, 0.8),
            ),
        )
        self.w = ezui.EZPanel(
            title='measurements',
            content=content,
            descriptionData=descriptionData,
            controller=self,
            size=(300, 400),
        )
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.getItem("measurements").getNSTableView().setRowHeight_(17)
        self.w.open()

    def started(self):
        MiniMeasurements.controller = self
        registerGlyphEditorSubscriber(MiniMeasurements)

    def destroy(self):
        unregisterGlyphEditorSubscriber(MiniMeasurements)
        MiniMeasurements.controller = None

    def measurementsAddRemoveButtonAddCallback(self, sender):
        glyph = CurrentGlyph()

        if glyph is None or len(glyph.selectedPoints) != 2:
            return

        table = self.w.getItem("measurements")

        pt1 = glyph.selectedPoints[0]
        pt2 = glyph.selectedPoints[1]

        ptIndex1 = getIndexForPoint(glyph, pt1)
        ptIndex2 = getIndexForPoint(glyph, pt2)

        item = table.makeItem(point1=ptIndex1, point2=ptIndex2)
        table.appendItems([item])

        postEvent(f"{DEFAULT_KEY}.changed")

    def measurementsAddRemoveButtonRemoveCallback(self, sender):
        table = self.w.getItem("measurements")
        table.removeSelectedItems()
        postEvent(f"{DEFAULT_KEY}.changed")

    def measurementsSelectionCallback(self, sender):
        postEvent(f"{DEFAULT_KEY}.changed")

    def measurementsEditCallback(self, sender):
        postEvent(f"{DEFAULT_KEY}.changed")

    def colorButtonCallback(self, sender):
        postEvent(f"{DEFAULT_KEY}.changed")


class MiniMeasurements(Subscriber):

    controller = None
    debug = True

    measurements = {}

    def build(self):
        glyphEditor = self.getGlyphEditor()
        container = glyphEditor.extensionContainer(
            identifier=DEFAULT_KEY,
            location="foreground",
        )
        self.measurementsLayer = container.appendBaseSublayer()
        self.glyph = CurrentGlyph()
        self._drawMeasurements()

    def destroy(self):
        glyphEditor = self.getGlyphEditor()
        container = glyphEditor.extensionContainer(DEFAULT_KEY)
        container.clearSublayers()

    def measurementsDidChange(self, info):
        self.glyph = self.getGlyphEditor().getGlyph().asFontParts()
        measurements = self.controller.w.getItem("measurements").get()
        self.measurements[self.glyph.name] = measurements
        self._updateMeasurements()
        self._drawMeasurements()

    def glyphEditorDidSetGlyph(self, info):
        glyph = info["glyph"]
        if glyph != self.glyph:
            self.glyph = glyph
            measurements = self.measurements.get(glyph.name, [])
            self.controller.w.getItem("measurements").set(measurements)
            self._updateMeasurements()
            self._drawMeasurements()

    def glyphEditorGlyphDidChangeOutline(self, info):
        # glyph = info["glyph"]
        self._updateMeasurements()
        self._drawMeasurements()

    def _updateMeasurements(self):
        if not self.controller:
            return

        table = self.controller.w.getItem("measurements")
        items = table.get()

        needReload = []
        for itemIndex, item in enumerate(items):
            pt1_index = item['point1']
            pt2_index = item['point2']

            pt1 = getPointAtIndex(self.glyph, pt1_index)
            pt2 = getPointAtIndex(self.glyph, pt2_index)

            if pt1 is None or pt2 is None:
                distance = None
            else:
                distance = hypot(pt2.x - pt1.x, pt2.y - pt1.y)
            item['units'] = int(distance)
            needReload.append(itemIndex)

        table.reloadData(needReload)

    def _drawMeasurements(self):

        if not self.controller:
            return

        table = self.controller.w.getItem("measurements")
        items = table.get()
        selectedItems = table.getSelectedItems()
        color = self.controller.w.getItem("colorButton").get()

        self.measurementsLayer.clearSublayers()

        with self.measurementsLayer.sublayerGroup():
            for item in items:
                pt1_index = item['point1']
                pt2_index = item['point2']

                pt1 = getPointAtIndex(self.glyph, pt1_index)
                pt2 = getPointAtIndex(self.glyph, pt2_index)

                if pt1 is None or pt2 is None:
                    continue

                lineDash = (1, 4) if item not in selectedItems else None

                self.measurementsLayer.appendLineSublayer(
                    startPoint=(pt1.x, pt1.y),
                    endPoint=(pt2.x, pt2.y),
                    strokeColor=color,
                    strokeWidth=2,
                    strokeCap='round',
                    strokeDash=lineDash,
                )

                if item in selectedItems:
                    cx = pt1.x + (pt2.x - pt1.x) * 0.5
                    cy = pt1.y + (pt2.y - pt1.y) * 0.5
                    distance = item['units']
                    self.measurementsLayer.appendTextLineSublayer(
                        position=(cx, cy),
                        backgroundColor=color,
                        text=f"{distance}",
                        font="system",
                        weight="bold",
                        pointSize=11,
                        padding=(4, 0),
                        cornerRadius=4,
                        fillColor=(1, 1, 1, 1),
                        horizontalAlignment='center',
                        verticalAlignment='center',
                    )


if __name__ == '__main__':

    measurementsEvent = f"{DEFAULT_KEY}.changed"

    if measurementsEvent not in roboFontSubscriberEventRegistry:
        registerSubscriberEvent(
            subscriberEventName=measurementsEvent,
            methodName="measurementsDidChange",
            lowLevelEventNames=[measurementsEvent],
            documentation="Send when the measurements window changes its parameters.",
            dispatcher="roboFont",
            delay=0,
            debug=True
        )

    OpenWindow(MiniMeasurementsWindowController)

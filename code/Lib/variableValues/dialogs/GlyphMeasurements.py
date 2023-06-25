from importlib import reload
import variableValues.measurements
reload(variableValues.measurements)
import variableValues.linkPoints
reload(variableValues.linkPoints)

import os
from math import sqrt
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import *
from mojo.UI import UpdateCurrentGlyphView
from mojo import drawingTools as ctx
from mojo.roboFont import *
from mojo.events import addObserver, removeObserver
from variableValues.measurements import *
from variableValues.linkPoints import *


'''
A tool to measure the distance between specific pairs of points and save them into the lib.

f'{ptIndex1} {ptIndex2}' : {
    'name'      : 'XTRA',
    'direction' : 'x',
}

f'{ptIndex1} {ptIndex2}' : {
    'name'      : 'YTRA',
    'direction' : 'y',
}

f'{ptIndex1}' : {
    'name'      : 'XXXX',
    'direction' : 'a',
    'side'      : 0,
}

'''

class GlyphMeasurements(BaseWindowController):
    
    title        = 'GlyphMeasurements'
    key          = 'com.fontBureau.glyphMeasurements'

    width        = 123*5
    height       = 640
    padding      = 10
    lineHeight   = 22
    verbose      = True
    buttonWidth  = 100

    _colGlyphs   = 140
    _colFontName = 240
    _colValue    = 80

    measurementParameters = ['name', 'direction', 'point 1', 'point 2']

    _dataFolder = '/Users/sergiogonzalez/Desktop/hipertipo/tools/VariableValues/example/relationships'
    assert os.path.exists(_dataFolder)

    _fonts = {}

    def __init__(self):
        self.w = FloatingWindow(
                (self.width, self.height), title=self.title,
                minSize=(self.width*0.9, 360))

        p = self.padding
        x, y = p, p/2
        self.w.measurementsLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'measurements')

        y += self.lineHeight + p/2

        _columnDescriptions  = [{"title": self.measurementParameters[0], 'width': self._colGlyphs*1.5, 'minWidth': self._colGlyphs, 'editable': True}]
        _columnDescriptions += [{"title": t, 'width': self._colValue, 'editable': True} for i, t in enumerate(self.measurementParameters[1:])]
        # _columnDescriptions += [{"title": self.measurementParameters[-1], 'width': self._colValue, 'editable': False}]

        self.w.measurements = List(
                (x, y, -p, -(self.lineHeight + p*2)),
                [],
                allowsMultipleSelection=True,
                allowsEmptySelection=True,
                selectionCallback=self.updatePreviewCallback,
                editCallback=self.editMeasurementCallback,
                enableDelete=True,
                columnDescriptions=_columnDescriptions,
            )

        y = -(self.lineHeight + p)
        self.w.newMeasurement = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'new',
                callback=self.newMeasurementCallback,
            )

        self.setUpBaseWindowBehavior()
        addObserver(self, 'loadMeasurements', 'currentGlyphChanged')
        addObserver(self, "backgroundPreview", "drawBackground")

        self.loadMeasurements(None)
        self.updatePreviewCallback(None)

        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

    # -------------
    # dynamic attrs
    # -------------

    @property
    def selectedMeasurements(self):
        items = self.w.measurements.get()
        selection = self.w.measurements.getSelection()
        if not selection:
            return
        return [items[i] for i in selection]

    def selectedMeasurementIDs(self, glyph):
        if not self.selectedMeasurements:
            return
        return [f"{m['point 1']} {m['point 2']}" for m in self.selectedMeasurements]

    # ---------
    # callbacks
    # ---------

    def windowCloseCallback(self, sender):
        '''
        Removes observers from the dialog after the window is closed.

        '''
        super().windowCloseCallback(sender)
        removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "drawBackground")

    def updatePreviewCallback(self, sender):
        UpdateCurrentGlyphView()

    def newMeasurementCallback(self, sender):
        '''
        Create a link between two selected points, and save it in the glyph lib.

        '''
        g = CurrentGlyph()
        if not g:
            return

        linkPoints(g)

        self.loadMeasurements(None)

    def editMeasurementCallback(self, sender):
        g = CurrentGlyph()
        if not g:
            return

        items = self.w.measurements.get()

        deleteAllLinks(g)

        for item in items:       
            if item['point 1'] is None:
                continue

            name = item.get('name')
            direction = item.get('direction')
            pt1 = getPointAtIndex(g, int(item['point 1']))
            pt2 = getPointAtIndex(g, int(item['point 2']))
            L = makeLink(g, pt1, pt2)
            if str(name) != '<null>' and str(direction) == '<null>':
                if name[0] == 'X':
                    direction = 'x'
                    item['direction'] = 'x'
                if name[0] == 'Y':
                    direction = 'y'
                    item['direction'] = 'y'
            saveLinkToLib(g, L, name=name, direction=direction, verbose=False)

    def loadMeasurements(self, sender):

        g = CurrentGlyph()
        if not g:
            self.w.measurements.set([])
            return

        measurements = getLinks(g)

        listItems = []
        for key in measurements.keys():
            index1, index2 = key.split()
            listItem = {
                'name'      : measurements[key].get('name'),
                'direction' : measurements[key].get('direction'), 
                'point 1'   : int(index1),
                'point 2'   : int(index2), 
            }
            listItems.append(listItem)

        self.w.measurements.set(listItems)

    # ---------
    # observers
    # ---------

    def backgroundPreview(self, notification):
        g = notification['glyph']
        s = notification['scale']
        if g is None:
            return
        self.drawPreview(g, s)

    # -------
    # methods
    # -------

    def drawPreview(self, glyph, previewScale):

        # if not self.selectedMeasurementIDs(glyph):
        #     return

        ctx.save()

        links = getLinks(glyph)

        if not len(links):
            return

        captionFontSize = 9 * previewScale

        def _drawLinkMeasurement(p1, p2, name, direction):
            if direction == 'x':
                value = p2[0] - p1[0]
            elif direction == 'y':
                value = p2[1] - p1[1]
            else:
                value = sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

            value = abs(value)
            
            if type(value) is int:
                txt = str(value)
            else:
                txt = '%.2f' % value if not value.is_integer() else str(int(value))

            txt = f'{name}={txt}'
            w, h = ctx.textSize(txt)
            x = p1[0] + (p2[0] - p1[0]) * 0.5
            y = p1[1] + (p2[1] - p1[1]) * 0.5
            x -= w * 0.5
            y -= h * 0.4

            ctx.textBox(txt, (x, y, w, h), align='center')

        selectedMeasurementIDs = self.selectedMeasurementIDs(glyph)

        for linkID, L in links.items():

            index1, index2 = linkID.split()
            pt1 = getPointAtIndex(glyph, int(index1))
            pt2 = getPointAtIndex(glyph, int(index2))

            if L['direction'] == 'x':
                P1 = pt1.x, pt1.y
                P2 = pt2.x, pt1.y
            elif L['direction'] == 'y':
                P1 = pt2.x, pt1.y
                P2 = pt2.x, pt2.y 
            else: # angled
                P1 = pt1.x, pt1.y
                P2 = pt2.x, pt2.y

            ctx.save()

            # draw link
            ctx.stroke(0, 0, 1)
            ctx.strokeWidth(1*previewScale)
            ctx.lineDash(2*previewScale, 2*previewScale)
            ctx.line((pt1.x, pt1.y), (pt2.x, pt2.y))

            if selectedMeasurementIDs is not None and linkID in selectedMeasurementIDs:

                # draw measurement
                ctx.fill(None)
                ctx.lineDash(None)
                ctx.stroke(0, 0, 1, 0.35)
                ctx.strokeWidth(7*previewScale)
                ctx.line(P1, P2)

                # draw caption
                ctx.stroke(None)
                ctx.fill(0, 0, 1)
                ctx.fontSize(captionFontSize)
                _drawLinkMeasurement(P1, P2, L['name'], L['direction'])

            ctx.restore()

        ctx.restore()


if __name__ == '__main__':

    OpenWindow(GlyphMeasurements)


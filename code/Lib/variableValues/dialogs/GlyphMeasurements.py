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

f'{ptID1} {ptID2}' : {
    'name'      : 'XTRA',
    'direction' : 'x',
}

f'{ptID1} {ptID2}' : {
    'name'      : 'YTRA',
    'direction' : 'y',
}

f'{ptID}' : {
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
        IDs = []
        for m in self.selectedMeasurements:
            if 'point 1' in m and 'point 2' in m:
                p1 = getPointAtIndex(glyph, int(m['point 1']))
                p2 = getPointAtIndex(glyph, int(m['point 2']))
                L = makeLink(p1, p2)
                IDs.append(f'{L[0]} {L[1]}')
        return IDs

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
            name = item.get('name')
            direction = item.get('direction')
            pt1 = getPointAtIndex(g, int(item['point 1']))
            pt2 = getPointAtIndex(g, int(item['point 2']))

            L = makeLink(pt1, pt2)

            saveLinkToLib(g, L, name=name, direction=direction)

    def loadMeasurements(self, sender):

        g = CurrentGlyph()
        if not g:
            self.w.measurements.set([])
            return

        measurements = getLinks(g)

        listItems = []
        for key in measurements.keys():
            id1, id2 = key.split()
            p1 = getPoint(g, id1)
            p2 = getPoint(g, id2)
            listItem = {
                'name'      : measurements[key].get('name'),
                'direction' : measurements[key].get('direction'), 
                'point 1'   : getIndexForPoint(g, p1),
                'point 2'   : getIndexForPoint(g, p2), 
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

        for linkID, L in links.items():

            ID1, ID2 = linkID.split()
            pt1 = getPoint(glyph, ID1)
            pt2 = getPoint(glyph, ID2)

            color = 0, 0.5, 1
            sw = 3*previewScale

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
            ctx.fill(None)
            ctx.strokeWidth(sw)

            selectedMeasurementIDs = self.selectedMeasurementIDs(glyph)

            if selectedMeasurementIDs is not None and linkID in selectedMeasurementIDs:
                # draw link
                ctx.stroke(*(color + (0.35,)))
                ctx.line(P1, P2)
                ctx.lineDash(sw, sw)
                ctx.line((pt1.x, pt1.y), (pt2.x, pt2.y))
                # draw captions
                ctx.stroke(None)
                ctx.fill(*color)
                ctx.fontSize(captionFontSize)
                _drawLinkMeasurement(P1, P2, L['name'], L['direction'])

            else:
                ctx.stroke(0.5, 0.35)
                ctx.lineDash(sw, sw)
                ctx.line((pt1.x, pt1.y), (pt2.x, pt2.y))

            ctx.restore()

        ctx.restore()



if __name__ == '__main__':

    OpenWindow(GlyphMeasurements)


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

class FontMeasurements(BaseWindowController):
    
    title        = 'Measurements'
    key          = 'com.fontBureau.measurements'

    width        = 123*5
    height       = 640
    padding      = 10
    lineHeight   = 22
    verbose      = True
    buttonWidth  = 100

    _tabsTitles  = ['font', 'glyph', 'options']

    _colName     = 95
    _colValue    = 65   

    fontMeasurementParameters  = ['name', 'direction', 'glyph 1', 'point 1', 'glyph 2', 'point 2', 'distance']
    glyphMeasurementParameters = ['name', 'direction', 'point 1', 'point 2', 'distance', 'font'] # 'factor'

    _fonts = {}

    def __init__(self):

        self.w = FloatingWindow(
                (self.width, self.height), title=self.title,
                minSize=(self.width*0.9, 360))

        x = y = p = self.padding
        self.w.tabs = Tabs((x, y, -p, -p), self._tabsTitles)

        self.initializeFontTab()
        self.initializeGlyphTab()
        self.initializeOptionsTab()

        self.setUpBaseWindowBehavior()
        addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
        addObserver(self, "fontBecameCurrent",   "fontBecameCurrent")
        addObserver(self, "backgroundPreview",   "drawBackground")

        self.font  = CurrentFont()
        self.glyph = CurrentGlyph()

        self.loadFontMeasurements(None)
        self.loadGlyphMeasurements(None)
        self.updatePreviewCallback(None)

        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

    def initializeFontTab(self):

        tab = self._tabs['font']

        _columnDescriptions  = [{"title": self.fontMeasurementParameters[0], 'width': self._colName*1.5, 'minWidth': self._colName, 'editable': True}]
        _columnDescriptions += [{"title": t, 'width': self._colValue, 'editable': True} for i, t in enumerate(self.fontMeasurementParameters[1:-1])]
        _columnDescriptions += [{"title": self.fontMeasurementParameters[-1], 'width': self._colValue, 'editable': False}]

        x = y = p = self.padding
        tab.measurements = List(
                (x, y, -p, -(self.lineHeight + p*2)),
                [],
                columnDescriptions=_columnDescriptions,
                allowsMultipleSelection=True,
                allowsEmptySelection=True,
                enableDelete=True,
                editCallback=self.editFontMeasurementCallback,
            )

        y = -(self.lineHeight + p)
        tab.newMeasurement = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'new',
                callback=self.newFontMeasurementCallback,
            )

        x = -self.buttonWidth*2 -p*2
        tab.importMeasurements = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'import',
                callback=self.importFontMeasurementsCallback,
            )
        x = -self.buttonWidth -p
        tab.exportMeasurements = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'export',
                callback=self.exportFontMeasurementsCallback,
            )

    def initializeGlyphTab(self):

        tab = self._tabs['glyph']

        _columnDescriptions  = [{"title": self.glyphMeasurementParameters[0], 'width': self._colName*1.5, 'minWidth': self._colName, 'editable': True}]
        _columnDescriptions += [{"title": t, 'width': self._colValue, 'editable': True}  for i, t in enumerate(self.glyphMeasurementParameters[1:-2])]
        _columnDescriptions += [{"title": t, 'width': self._colValue, 'editable': False} for i, t in enumerate(self.glyphMeasurementParameters[-2:])]

        x = y = p = self.padding
        tab.measurements = List(
                (x, y, -p, -(self.lineHeight + p*2)),
                [],
                columnDescriptions=_columnDescriptions,
                allowsMultipleSelection=True,
                allowsEmptySelection=True,
                enableDelete=True,
                selectionCallback=self.updatePreviewCallback,
                editCallback=self.editGlyphMeasurementCallback,
            )

        y = -(self.lineHeight + p)
        tab.newMeasurement = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'new',
                callback=self.newGlyphMeasurementCallback,
            )

        x = -self.buttonWidth*2 -p*2
        tab.importMeasurements = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'import',
                callback=self.importGlyphMeasurementsCallback,
            )
        x = -self.buttonWidth -p
        tab.exportMeasurements = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'export',
                callback=self.exportGlyphMeasurementsCallback,
            )

    def initializeOptionsTab(self):
        pass

    # -------------
    # dynamic attrs
    # -------------

    @property
    def _tabs(self):
        tabsDict = {}
        for tabTitle in self._tabsTitles:
            tabIndex = self._tabsTitles.index(tabTitle)
            tabsDict[tabTitle] = self.w.tabs[tabIndex]
        return tabsDict

    # font

    @property
    def selectedFontMeasurements(self):
        pass

    # glyph

    @property
    def selectedGlyphMeasurements(self):
        tab = self._tabs['glyph']
        items = tab.measurements.get()
        selection = tab.measurements.getSelection()
        if not selection:
            return
        return [items[i] for i in selection]

    @property
    def selectedGlyphMeasurementIDs(self):
        if not self.selectedGlyphMeasurements:
            return
        return [f"{m['point 1']} {m['point 2']}" for m in self.selectedGlyphMeasurements]

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

    # font

    def newFontMeasurementCallback(self, sender):
        '''
        Create a link between two points, save it in the font lib, update the measurements list.

        '''
        f = self.font
        if not f:
            return

        tab = self._tabs['font']
        newListItem = {
            'name'      : None,
            'direction' : None,
            'glyph 1'   : None,
            'point 1'   : None,
            'glyph 2'   : None,
            'point 2'   : None,
        }
        tab.measurements.append(newListItem)
        self.updateFontDistances()

    def editFontMeasurementCallback(self, sender):
        f = self.font
        if not f:
            return

        items = self._tabs['font'].measurements.get()

        for item in items:
            name = item.get('name')
            if name is None or str(name) == '<null>':
                continue
            L = {
                'direction' : item.get('direction'),
                'glyph 1'   : item.get('glyph 1'),
                'point 1'   : item.get('point 1'),
                'glyph 2'   : item.get('glyph 2'),
                'point 2'   : item.get('point 2'),
            }

            # guess direction from name
            if str(L['direction']) == '<null>':
                if name[0] == 'X':
                    item['direction'] = 'x'
                    L['direction'] = 'x'
                if name[0] == 'Y':
                    item['direction'] = 'y'
                    L['direction'] = 'y'

            saveLinkToLib_font(f, name, L, verbose=False)

        self.updateFontDistances()

    def updateFontDistances(self):
        items = self._tabs['font'].measurements.get()
        for item in items:
            gName1 = item.get('glyph 1')
            gName2 = item.get('glyph 2')
            if gName1 is None or gName2 is None:
                continue
            gName1, gName2 = str(gName1), str(gName2)
            if gName1 not in self.font or gName2 not in self.font:
                continue
            g1 = self.font[gName1]
            g2 = self.font[gName2]
            try:
                index1 = int(item.get('point 1'))
                index2 = int(item.get('point 2'))
                p1 = getPointAtIndex(g1, index1)
                p2 = getPointAtIndex(g2, index2)
                distance = getDistance((p1.x, p1.y), (p2.x, p2.y), item['direction'])
                item['distance'] = distance
            except:
                pass

    def loadFontMeasurements(self, sender):
        '''
        Load current measurements from the font lib into the list.

        '''
        tab = self._tabs['font']

        f = self.font
        if not f:
            tab.measurements.set([])
            return

        measurements = getLinks_font(f)
        if measurements is None:
            tab.measurements.set([])
            return

        listItems = []
        for name in measurements.keys():
            item = {
                'name'      : name,
                'direction' : measurements[name].get('direction'), 
                'glyph 1'   : measurements[name].get('glyph 1'),
                'point 1'   : measurements[name].get('point 1'),
                'glyph 2'   : measurements[name].get('glyph 2'),
                'point 2'   : measurements[name].get('point 2'),
            }
            listItems.append(item)

        tab.measurements.set(listItems)
        self.updateFontDistances()

    def importFontMeasurementsCallback(self, sender):
        pass

    def exportFontMeasurementsCallback(self, sender):
        pass

    # glyph

    def newGlyphMeasurementCallback(self, sender):
        '''
        Create a link between two selected points, save it in the glyph lib, update the measurements list.

        '''
        g = self.glyph
        if not g:
            return

        linkPoints(g)

        self.loadGlyphMeasurements(None)

    def editGlyphMeasurementCallback(self, sender):
        '''
        When an item is edited, clear the glyph lib, and save all items in it.
        If we don't clear the lib, we may end up with duplicate measurements.
        
        '''
        g = self.glyph
        if not g:
            return

        items = self._tabs['glyph'].measurements.get()

        deleteAllLinks(g)

        for item in items:       
            if item['point 1'] is None:
                continue

            name      = item.get('name')
            direction = item.get('direction')
            ptIndex1  = int(item['point 1'])
            ptIndex2  = int(item['point 2'])

            L = ptIndex1, ptIndex2

            # guess direction from name
            if str(name) != '<null>' and str(direction) == '<null>':
                if name[0] == 'X':
                    direction = 'x'
                    item['direction'] = 'x'
                if name[0] == 'Y':
                    direction = 'y'
                    item['direction'] = 'y'

            saveLinkToLib(g, L, name=name, direction=direction, verbose=False)

    def loadGlyphMeasurements(self, sender):
        '''
        Load current measurements from the glyph lib into the list.

        '''
        tab = self._tabs['glyph']

        g = self.glyph
        if not g:
            tab.measurements.set([])
            return

        measurements = getLinks(g)

        listItems = []
        for key in measurements.keys():
            index1, index2 = key.split()
            index1, index2 = int(index1), int(index2)
            name = measurements[key].get('name')
            direction = measurements[key].get('direction')
            listItem = {
                'name'      : name,
                'direction' : direction, 
                'point 1'   : index1,
                'point 2'   : index2, 
            }   
            p1 = getPointAtIndex(g, index1)
            p2 = getPointAtIndex(g, index2)
            distance = getDistance((p1.x, p1.y), (p2.x, p2.y), listItem['direction'])
            listItem['distance'] = distance
            # get font measurement
            fontMeasurements = self._tabs['font'].measurements.get()
            if name is not None:
                for m in fontMeasurements:
                    if name != m['name']:
                        continue
                    listItem['font'] = m['distance']
                    try:
                        listItem['factor'] = fontDistance / float(m.get('distance'))
                    except:
                        if self.verbose:
                            print(f'no font distance for {name}')
                        pass

            listItems.append(listItem)

        tab.measurements.set(listItems)

    def updatePreviewCallback(self, sender):
        UpdateCurrentGlyphView()

    def importGlyphMeasurementsCallback(self, sender):
        pass

    def exportGlyphMeasurementsCallback(self, sender):
        pass

    # ---------
    # observers
    # ---------

    def backgroundPreview(self, notification):
        s = notification['scale']
        if self.glyph is None:
            return
        self.drawPreview(self.glyph, s)

    # font

    def fontBecameCurrent(self, notification):
        self.font = notification['font']
        self.loadFontMeasurements(None)

    # glyph

    def currentGlyphChanged(self, notification):
        '''
        When the current glyph changes, remove/add observer, update the measurements list, update the glyph view.

        '''
        if self.glyph is not None:
            self.glyph.removeObserver(self, "Glyph.Changed")

        self.glyph = notification['glyph']

        if self.glyph is not None:
            self.glyph.addObserver(self, "glyphChangedCallback", "Glyph.Changed")

        self.loadGlyphMeasurements(None)
        self.updatePreviewCallback(None)

    def glyphChangedCallback(self, notification):
        glyph = RGlyph(notification.object)
        for item in self._tabs['glyph'].measurements.get():
            p1 = getPointAtIndex(glyph, int(item['point 1']))
            p2 = getPointAtIndex(glyph, int(item['point 2']))
            distance = getDistance((p1.x, p1.y), (p2.x, p2.y), item['direction'])
            item['distance'] = distance

    # -------
    # methods
    # -------

    def drawPreview(self, glyph, previewScale):
        '''
        Draw the current glyph's measurements in the background of the Glyph View.

        '''
        links = getLinks(glyph)
        if not len(links):
            return

        def _drawLinkMeasurement(p1, p2, name, direction):
            value = getDistance(p1, p2, direction)
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

        ctx.save()

        for linkID, L in links.items():
            index1, index2 = linkID.split()
            index1, index2 = int(index1), int(index2)
            pt1 = getPointAtIndex(glyph, index1)
            pt2 = getPointAtIndex(glyph, index2)

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
            ctx.strokeWidth(2*previewScale)
            ctx.lineDash(3*previewScale, 3*previewScale)
            ctx.line((pt1.x, pt1.y), (pt2.x, pt2.y))

            if self.selectedGlyphMeasurementIDs is not None:
                if linkID in self.selectedGlyphMeasurementIDs:
                    # draw measurement
                    ctx.fill(None)
                    ctx.lineDash(None)
                    ctx.stroke(0, 0, 1, 0.35)
                    ctx.strokeWidth(7*previewScale)
                    ctx.line(P1, P2)
                    # draw caption
                    ctx.stroke(None)
                    ctx.fill(0, 0, 1)
                    ctx.fontSize(9*previewScale)
                    _drawLinkMeasurement(P1, P2, L['name'], L['direction'])

            ctx.restore()

        ctx.restore()


if __name__ == '__main__':

    OpenWindow(FontMeasurements)


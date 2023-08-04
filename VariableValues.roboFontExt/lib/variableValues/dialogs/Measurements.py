from importlib import reload
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
M E A S U R E M E N T S

A tool to measure distances in glyphs and store them in the font.

Font Measurements
-----------------

'XTRA' : {
    'glyph 1'   : 'H',
    'point 1'   : 11,
    'glyph 2'   : 'H',
    'point 2'   : 8,
    'direction' : 'x',
}

Glyph Measurements
------------------

f'{ptIndex1} {ptIndex2}' : {
    'name'      : 'XTRA',
    'direction' : 'x', # y
}

f'{ptIndex}' : {
    'name'      : 'YTAS',
    'direction' : 0, # 1
}

'''


# copied from hTools3.modules.color

from AppKit import NSColor

def rgb2nscolor(rgbColor):
    '''
    Convert RGB color tuple to NSColor object.

    Args:
        rgbColor (tuple): RGB color as a tuple of 1, 2, 3 or 4 values (floats between 0 and 1).

    Returns:
        A NSColor object.

    >>> rgbColor = 1, 0, 0
    >>> rgb2nscolor(rgbColor)
    NSCalibratedRGBColorSpace 1 0 0 1

    '''
    if rgbColor is None:
        return
    elif len(rgbColor) == 1:
        r = g = b = rgbColor[0]
        a = 1.0
    elif len(rgbColor) == 2:
        grey, a = rgbColor
        r = g = b = grey
    elif len(rgbColor) == 3:
        r, g, b = rgbColor
        a = 1.0
    elif len(rgbColor) == 4:
        r, g, b, a = rgbColor
    else:
        return
    nsColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, a)
    return nsColor

def nscolor2rgb(nsColor):
    '''
    Convert from NSColor object to RGBA color tuple.

    Args:
        nsColor (NSColor): A color object.

    Returns:
        A tuple of RGBA values.

    >>> nsColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, .5, 1, .8)
    >>> nsColorToRGB(nsColor)
    (0.0, 0.5, 1.0, 0.8)

    '''
    r = nsColor.redComponent()
    g = nsColor.greenComponent()
    b = nsColor.blueComponent()
    a = nsColor.alphaComponent()
    return r, g, b, a



class Measurements(BaseWindowController):
    
    title        = 'Measurements'
    key          = 'com.fontBureau.measurements'

    width        = 123*5
    height       = 640
    padding      = 10
    lineHeight   = 22
    verbose      = True
    buttonWidth  = 80
    buttonHeight = 25
    sizeStyle    = 'normal'

    _tabsTitles  = ['font', 'glyph']
    _colName     = 95
    _colValue    = 65

    settings = {
        'measurementsColor' : (1, 0, 0, 1),
        'strokeWidth1'      : 1,
        'strokeWidth2'      : 20,
        'radius1'           : 10,
    }

    fontMeasurementParameters  = ['name', 'direction', 'glyph 1', 'point 1', 'glyph 2', 'point 2', 'value', 'parent', 'scale']
    glyphMeasurementParameters = ['name', 'direction', 'point 1', 'point 2', 'value', 'parent', 'scale']

    #: measurements for current font
    fontMeasurements  = {}

    #: measurements for current glyph
    glyphMeasurements = {}

    def __init__(self):
        self.w = FloatingWindow(
                (self.width, self.height), title=self.title,
                minSize=(self.width*0.9, 360))

        x = y = p = self.padding
        self.w.tabs = Tabs((x, y, -p, -p), self._tabsTitles)

        self.initializeFontTab()
        self.initializeGlyphTab()

        self.setUpBaseWindowBehavior()
        addObserver(self, "fontBecameCurrent",   "fontBecameCurrent")
        addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
        addObserver(self, "backgroundPreview",   "drawBackground")
        addObserver(self, "drawLabelCell",       "glyphCellDrawBackground")

        self.font  = CurrentFont()
        self.glyph = CurrentGlyph()

        self.loadFontMeasurements(None)
        self.loadGlyphMeasurements(None)
        self.updatePreviewCallback(None)

        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

    def initializeFontTab(self):

        tab = self._tabs['font']

        _columnDescriptions  = [{"title": self.fontMeasurementParameters[0], 'width': self._colName*1.5, 'minWidth': self._colName, 'editable': True}] # name
        _columnDescriptions += [{"title": t, 'width': self._colValue, 'editable': True} for i, t in enumerate(self.fontMeasurementParameters[1:-3])]   # dir, g1, p1, g2, p2
        _columnDescriptions += [{"title": self.fontMeasurementParameters[-3], 'width': self._colValue, 'editable': False}]                             # value
        _columnDescriptions += [{"title": self.fontMeasurementParameters[-2], 'width': self._colValue, 'editable': True}]                              # parent
        _columnDescriptions += [{"title": self.fontMeasurementParameters[-1], 'width': self._colValue, 'editable': False}]                             # scale

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
        _columnDescriptions += [{"title": t, 'width': self._colValue, 'editable': True}  for i, t in enumerate(self.glyphMeasurementParameters[1:-3])]
        _columnDescriptions += [{"title": t, 'width': self._colValue, 'editable': False} for i, t in enumerate(self.glyphMeasurementParameters[-3:-1])]
        _columnDescriptions += [{"title": self.glyphMeasurementParameters[-1]}]

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

        x += self.buttonWidth + p
        tab.measurementsColor = ColorWell(
                (x, y, self.buttonWidth, self.lineHeight),
                callback=self.measurementsColorCallback,
                color=rgb2nscolor(self.settings['measurementsColor'])
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
        IDs = []
        for m in self.selectedGlyphMeasurements:
            if m['point 2'] is not None:
                ID = f"{m['point 1']} {m['point 2']}"
            else:
                ID = f"{m['point 1']}"
            IDs.append(ID)
        return IDs

    # options

    @property
    def measurementsColor(self):
        return self.settings.get('measurementsColor')

    @property
    def measurementsColorDim(self):
        r, g, b, a = self.measurementsColor
        return r, g, b, 0.35

    # ---------
    # callbacks
    # ---------

    def windowCloseCallback(self, sender):
        '''
        Removes observers from the dialog after the window is closed.

        '''
        super().windowCloseCallback(sender)
        removeObserver(self, "fontBecameCurrent")
        removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "drawBackground")
        removeObserver(self, "glyphCellDrawBackground")

    # font

    def loadFontMeasurements(self, sender):
        '''
        Load measurements from the current font's lib into a dictionary.

        '''
        f = self.font
        if not f:
            return

        self.fontMeasurements = getLinks_font(f)

        self.updateFontMeasurements()

    def updateFontMeasurements(self):
        '''
        Load measurements from dictionary into font measurements list.

        '''
        tab = self._tabs['font']

        if not self.fontMeasurements:
            tab.measurements.set([])
            return

        listItems = []
        for measurementName in self.fontMeasurements.keys():
            # get data from dict
            listItem = {
                'name'      : measurementName,
                'direction' : self.fontMeasurements[measurementName].get('direction'), 
                'glyph 1'   : self.fontMeasurements[measurementName].get('glyph 1'),
                'point 1'   : self.fontMeasurements[measurementName].get('point 1'),
                'glyph 2'   : self.fontMeasurements[measurementName].get('glyph 2'),
                'point 2'   : self.fontMeasurements[measurementName].get('point 2'),
                'parent'    : self.fontMeasurements[measurementName].get('parent'),
                'value'     : None,
                'scale'     : None,
            }

            # measure distance

            gName1 = listItem.get('glyph 1')
            gName2 = listItem.get('glyph 2')

            # glyph names must be strings
            if isinstance(gName1, str) and isinstance(gName2, str):

                # glyph names must not be empty
                if len(gName1.strip()) and len(gName2.strip()):

                    # glyphs must be included in the font
                    if not (gName1 not in self.font or gName2 not in self.font):

                        g1 = self.font[gName1]
                        g2 = self.font[gName2]

                        try:
                            index1 = int(listItem.get('point 1'))
                            index2 = int(listItem.get('point 2'))
                            p1 = getPointAtIndex(g1, index1)
                            p2 = getPointAtIndex(g2, index2)
                            distance = getDistance((p1.x, p1.y), (p2.x, p2.y), listItem['direction'])
                            listItem['value'] = distance

                        except:
                            pass

            listItem = { k : ('' if v is None else v) for k, v in listItem.items() }
            listItems.append(listItem)

        tab.measurements.set(listItems)

    def newFontMeasurementCallback(self, sender):
        '''
        Create an empty link between two points, and add it to the measurements list.

        '''
        f = self.font
        if not f:
            return

        # attrs = ['direction', 'glyph 1', 'point 1', 'glyph 2', 'point 2', 'parent']

        tab = self._tabs['font']

        listItem = {
            'name'      : 'untitled',
            'direction' : '',
            'glyph 1'   : '',
            'point 1'   : '',
            'glyph 2'   : '',
            'point 2'   : '',
            'parent'    : '',
            'value'     : '',
            'scale'     : '',
        }
        tab.measurements.append(listItem)

        # self.fontMeasurements['untitled'] = { m: None for m in attrs }
        # self.updateFontMeasurements()

    def editFontMeasurementCallback(self, sender):

        f = self.font
        if not f:
            return

        tab       = self._tabs['font']
        items     = tab.measurements.get()
        selection = tab.measurements.getSelection()

        if not selection:
            return

        item = items[selection[0]]

        # collect measurement data
        name = item.get('name')
        measurementAttrs = {
            'direction' : item.get('direction'),
            'glyph 1'   : item.get('glyph 1'),
            'point 1'   : item.get('point 1'),
            'glyph 2'   : item.get('glyph 2'),
            'point 2'   : item.get('point 2'),
            'parent'    : item.get('parent'),
        }
        # if name is valid and direction is empty,
        # try to guess the direction from name
        if len(name.strip()) and len(item['direction'].strip()) == 0:
            if name[0] == 'X':
                measurementAttrs['direction'] = 'x'
                item['direction'] = 'x'
            if name[0] == 'Y':
                measurementAttrs['direction'] = 'y'
                item['direction'] = 'y'

        # save measurement to dict
        # self.fontMeasurements[name] = measurementAttrs

        # save measurement to font
        saveLinkToLib_font(f, name, measurementAttrs, verbose=False)

        # self.loadFontMeasurements(None)

    def importFontMeasurementsCallback(self, sender):
        pass

    def exportFontMeasurementsCallback(self, sender):
        pass

    # glyph

    def newGlyphMeasurementCallback(self, sender):
        '''
        Create a link between two selected points.

        - save new measurement in the glyph lib
        - reload all measurements from the glyph lib into the list

        '''
        g = self.glyph
        if not g:
            return

        # if len(g.selectedPoints) == 1:
        #     newMeasurePoint(g)
        # else:

        linkPoints(g)

        self.loadGlyphMeasurements(None)

    def editGlyphMeasurementCallback(self, sender):
        '''
        When a measurement list item is edited: 

        - clear the glyph lib
        - save all measurement items in it

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
            ptIndex2  = item['point 2']

            if not len(name.strip()):
                name = None
            if not len(direction.strip()):
                direction = None
            if type(ptIndex2) is not int:
                if not len(ptIndex2.strip()):
                    ptIndex2 = None

            # if ptIndex2 is None:
            #     saveMeasurePointToLib(g, ptIndex1, name=name, direction=direction)
            # else:
            ptIndex2 = int(ptIndex2)

            # guess direction from name
            if name is not None and direction is None:
                if name[0] == 'X':
                    direction = 'x'
                    item['direction'] = 'x'
                if name[0] == 'Y':
                    direction = 'y'
                    item['direction'] = 'y'

            saveLinkToLib(g, (ptIndex1, ptIndex2), name=name, direction=direction, verbose=False)

    def loadGlyphMeasurements(self, sender):
        '''
        Load all measurements from the glyph lib into the measurements list.

        '''
        tab = self._tabs['glyph']

        g = self.glyph
        if not g:
            tab.measurements.set([])
            return

        measurements = getLinks(g)

        listItems = []
        for key in measurements.keys():
            # get point or points
            keyParts = key.split()
            if len(keyParts) == 2:
                index1, index2 = keyParts
                index1, index2 = int(index1), int(index2)
            elif len(keyParts) == 1:
                index1 = keyParts[0].strip()
                index2 = None
            else:
                continue
            name = measurements[key].get('name')
            direction = measurements[key].get('direction')
            listItem = {
                'name'      : name,
                'direction' : direction, 
                'point 1'   : index1,
                'point 2'   : index2, 
            }   
            if index2 is not None:
                # get distance between points
                p1 = getPointAtIndex(g, index1)
                p2 = getPointAtIndex(g, index2)
                distance = getDistance((p1.x, p1.y), (p2.x, p2.y), listItem['direction'])
                listItem['value'] = distance
                # get font measurement
                fontMeasurements = self._tabs['font'].measurements.get()
                if name is not None:
                    for m in fontMeasurements:
                        if name != m['name']:
                            continue
                        fontDistance = m['value']
                        listItem['parent'] = fontDistance
                        # get measurement scale
                        if distance and fontDistance:
                            scaleValue = distance / float(fontDistance)
                            listItem['scale'] = f'{scaleValue:.3f}'
            _listItem = {}
            for k, v in listItem.items():
                if v is None:
                   v = '' 
                _listItem[k] = v
            listItems.append(_listItem)

        tab.measurements.set(listItems)

    def updatePreviewCallback(self, sender):
        UpdateCurrentGlyphView()

    def importGlyphMeasurementsCallback(self, sender):
        pass

    def exportGlyphMeasurementsCallback(self, sender):
        pass

    def measurementsColorCallback(self, sender):
        '''
        Change the measurements color and update the glyph view.

        TO-DO: save the chosen color into custom RF preference

        '''
        tab = self._tabs['glyph']
        color = tab.measurementsColor.get()
        self.settings['measurementsColor'] = nscolor2rgb(color)
        self.updatePreviewCallback(None)

    # ---------
    # observers
    # ---------

    def backgroundPreview(self, notification):
        '''
        Draw a visualization of the glyph measurements in the Glyph View.

        '''
        s = notification['scale']

        if self.glyph is None:
            return

        self.drawPreview(self.glyph, s)

    def drawLabelCell(self, notification):

        glyph = notification['glyph']

        measurements = getLinks(glyph)
        if not len(measurements):
            return

        ctx.save()
        ctx.font('Menlo-Bold')
        ctx.fontSize(10)
        ctx.translate(3, 3)
        ctx.fill(0, 0, 1)
        ctx.text('M', (0, -3))
        ctx.restore()

    # font

    def fontBecameCurrent(self, notification):
        '''
        When the current font changes:

        - update the font measurements list

        '''
        self.font = notification['font']
        self.loadFontMeasurements(None)

    # glyph

    def currentGlyphChanged(self, notification):
        '''
        When the current glyph changes:

        - remove/add glyph observers
        - update the glyph measurements list
        - update the glyph view

        '''
        if self.glyph is not None:
            self.glyph.removeObserver(self, "Glyph.Changed")

        self.glyph = notification['glyph']

        if self.glyph is not None:
            self.glyph.addObserver(self, "glyphChangedObserver", "Glyph.Changed")

        self.loadGlyphMeasurements(None)
        self.updatePreviewCallback(None)

    def glyphChangedObserver(self, notification):
        '''
        When the current glyph is changed:

        - recalculate distances between points
        - recalculate scale in relation to parent value

        '''
        glyph = RGlyph(notification.object)

        glyphMeasurements = self._tabs['glyph'].measurements.get()
        fontMeasurements  = self._tabs['font'].measurements.get()

        for item in glyphMeasurements:
            p1 = getPointAtIndex(glyph, int(item['point 1']))
            p2 = item['point 2']
            if p2 is not None:
                p2 = getPointAtIndex(glyph, int(p2))
                distance = getDistance((p1.x, p1.y), (p2.x, p2.y), item['direction'])
            else:
                distance = None

            if not item.get('value'):
                return

            item['value'] = distance

            # get font measurement
            name = item.get('name')
            if name is None or not len(name.strip()):
                return

            for m in fontMeasurements:
                if name != m['name']:
                    continue
                item['parent'] = m['value']
                # item['scale']  = ''

                # fontDistance = m['value']
                # if distance == 0 and fontDistance == 0:
                #     item['scale'] = f'{1:.3f}'
                #     return

                # if not (distance and fontDistance):
                #     item['scale'] = ''
                #     return

                # # update measurement scale
                # scaleValue = distance / float(fontDistance)
                # item['scale'] = f'{scaleValue:.3f}'

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
            partsID = linkID.split()

            # two-point measurements
            if len(partsID) == 2:
                index1, index2 = partsID
                index1, index2 = int(index1), int(index2)

                pt1 = getPointAtIndex(glyph, index1)
                pt2 = getPointAtIndex(glyph, index2)

                if L.get('direction') == 'x':
                    P1 = pt1.x, pt1.y
                    P2 = pt2.x, pt1.y
                elif L.get('direction') == 'y':
                    P1 = pt2.x, pt1.y
                    P2 = pt2.x, pt2.y 
                else: # angled
                    P1 = pt1.x, pt1.y
                    P2 = pt2.x, pt2.y

                ctx.save()

                # draw link
                ctx.stroke(*self.measurementsColor)
                ctx.strokeWidth(self.settings['strokeWidth1']*previewScale)
                ctx.lineDash(3*previewScale, 3*previewScale)
                ctx.line((pt1.x, pt1.y), (pt2.x, pt2.y))

                if self.selectedGlyphMeasurementIDs is not None:
                    if linkID in self.selectedGlyphMeasurementIDs:
                        # draw measurement
                        ctx.fill(None)
                        ctx.lineDash(None)
                        ctx.stroke(*self.measurementsColorDim)
                        ctx.strokeWidth(self.settings['strokeWidth2']*previewScale)
                        ctx.line(P1, P2)
                        # draw caption
                        ctx.stroke(None)
                        ctx.fill(*self.measurementsColor)
                        ctx.fontSize(9*previewScale)
                        _drawLinkMeasurement(P1, P2, L.get('name'), L.get('direction'))

                ctx.restore()

            # one-point measurements
            elif len(partsID) == 1:
                index1 = partsID[0].strip()
                pt1 = getPointAtIndex(glyph, int(index1))
                r = self.settings['radius1'] * previewScale
                ctx.save()
                if self.selectedGlyphMeasurementIDs is not None and linkID in self.selectedGlyphMeasurementIDs:
                    ctx.fill(*self.measurementsColorDim)
                else:
                    ctx.fill(None)
                ctx.stroke(*self.measurementsColor)
                ctx.strokeWidth(self.settings['strokeWidth1']*previewScale)
                ctx.oval(pt1.x-r, pt1.y-r, r*2, r*2)
                ctx.restore()

            else:
                continue

        ctx.restore()


if __name__ == '__main__':

    OpenWindow(Measurements)


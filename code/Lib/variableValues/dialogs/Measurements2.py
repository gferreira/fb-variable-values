from importlib import reload
import variableValues.linkPoints
reload(variableValues.linkPoints)

import os
from math import sqrt
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import *
from mojo.UI import UpdateCurrentGlyphView, PutFile, GetFile
from mojo import drawingTools as ctx
from mojo.roboFont import *
from mojo.events import addObserver, removeObserver
from variableValues.linkPoints import *
from variableValues.measurements import Measurement


'''
M E A S U R E M E N T S v2

A tool to measure distances in glyphs and store them in the font.

# FONT MEASUREMENTS

'XTUC' : {
    'glyph 1'   : 'H',
    'point 1'   : 11,
    'glyph 2'   : 'H',
    'point 2'   : 8,
    'direction' : 'x',
    'parent'    : 'XTRA',
}

# GLYPH MEASUREMENTS

f'{ptIndex1} {ptIndex2}' : {
    'name'      : 'XTRA',
    'direction' : 'x',
}

f'{ptIndex}' : {
    'name'      : 'YTAS',
    'direction' : 0,
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



class Measurements2(BaseWindowController):
    
    title        = 'Measurements'
    key          = 'com.fontBureau.measurements2'

    width        = 123*5
    height       = 640
    padding      = 10
    lineHeight   = 22
    verbose      = True
    buttonWidth  = 85
    buttonHeight = 25
    sizeStyle    = 'normal'

    _tabsTitles  = ['font', 'glyph']
    _colName     = 55
    _colValue    = 55

    settings = {
        'measurementsColor' : (1, 0, 0, 1),
        'strokeWidth1'      : 1,
        'strokeWidth2'      : 20,
        'radius1'           : 10,
    }

    fontMeasurementParameters  = ['name', 'direction', 'glyph 1', 'point 1', 'glyph 2', 'point 2', 'units', 'permill', 'parent', 'scale']
    glyphMeasurementParameters = ['name', 'direction', 'point 1', 'point 2', 'units', 'permill', 'parent', 'scale']

    measurementFilePath = None

    #: measurements for current font
    # fontMeasurements  = {}

    #: measurements for current glyph
    # glyphMeasurements = {}

    def __init__(self):
        self.w = FloatingWindow(
                (self.width, self.height), title=self.title,
                minSize=(self.width*0.9, 360))

        x = y = p = self.padding
        self.w.tabs = Tabs((x, y, -p, -(self.lineHeight + p*2)), self._tabsTitles)

        self.initializeFontTab()
        self.initializeGlyphTab()

        y = -self.lineHeight -p
        self.w.loadMeasurements = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'load…',
                callback=self.loadMeasurementsCallback,
            )

        x += self.buttonWidth + p
        self.w.saveMeasurements = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'save',
                callback=self.saveMeasurementsCallback,
            )

        x = -self.buttonWidth -p
        self.w.exportMeasurements = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'export…',
                callback=self.exportMeasurementsCallback,
            )

        self.setUpBaseWindowBehavior()
        addObserver(self, "fontBecameCurrent",   "fontBecameCurrent")
        addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
        addObserver(self, "backgroundPreview",   "drawBackground")
        addObserver(self, "drawLabelCell",       "glyphCellDrawBackground")

        self.font  = CurrentFont()
        self.glyph = CurrentGlyph()

        # self.loadMeasurementsCallback(None)
        # self.loadGlyphMeasurements(None)
        # self.updatePreviewCallback(None)

        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

    def initializeFontTab(self):

        tab = self._tabs['font']

        _columnDescriptions  = [{"title": self.fontMeasurementParameters[0], 'width': self._colName*1.5, 'minWidth': self._colName, 'editable': True}] # name
        _columnDescriptions += [{"title": t, 'width': self._colValue, 'editable': True} for i, t in enumerate(self.fontMeasurementParameters[1:-4])]   # dir, g1, p1, g2, p2
        _columnDescriptions += [{"title": self.fontMeasurementParameters[-4], 'width': self._colValue, 'editable': False}]                             # units
        _columnDescriptions += [{"title": self.fontMeasurementParameters[-3], 'width': self._colValue, 'editable': False}]                             # permill
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

    def initializeGlyphTab(self):

        tab = self._tabs['glyph']

        _columnDescriptions  = [{"title": self.glyphMeasurementParameters[0], 'width': self._colName*1.5, 'minWidth': self._colName, 'editable': True}]     # name
        _columnDescriptions += [{"title": t, 'width': self._colValue, 'editable': True}  for i, t in enumerate(self.glyphMeasurementParameters[1:-4])]      # dir, p1, p2
        _columnDescriptions += [{"title": t, 'width': self._colValue, 'editable': False} for i, t in enumerate(self.glyphMeasurementParameters[-4:-1])]     # units, permill, parent
        _columnDescriptions += [{"title": self.glyphMeasurementParameters[-1]}]                                                                             # scale

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

    def loadMeasurementsCallback(self, sender):
        if self.verbose:
            print("loading measurement data from file...")

        jsonPath = GetFile(message='Select JSON file with measurements:')

        if self.verbose:
            print(f'\tloading data from {jsonPath}...')

        measurements = readMeasurements(jsonPath)

        self.fontMeasurements  = measurements['font']
        self.glyphMeasurements = measurements['glyphs']

        self.loadFontMeasurements()
        # self.updateFontMeasurements()
        self.updateGlyphMeasurements()

        if self.verbose:
            print('...done.\n')

    def saveMeasurementsCallback(self, sender):
        pass

    def exportMeasurementsCallback(self, sender):
        if self.font is None:
            return

        # get json file path for saving

        jsonFileName = 'measurements.json'
        jsonPath = PutFile(message='Save measurements into JSON file:', fileName=jsonFileName)

        if jsonPath is None:
            if self.verbose:
                print('[cancelled]\n')
            return

        if os.path.exists(jsonPath):
            os.remove(jsonPath)

        exportMeasurements(self.font, jsonPath)

    # font

    def loadFontMeasurements(self):
        '''
        Load measurements from dictionary into font measurements list.

        '''
        tab = self._tabs['font']

        if not self.fontMeasurements:
            tab.measurements.set([])
            return

        listItems = []
        for name in self.fontMeasurements.keys():
            # get data from dict
            listItem = {
                'name'      : name,
                'direction' : self.fontMeasurements[name].get('direction'), 
                'glyph 1'   : self.fontMeasurements[name].get('glyph 1'),
                'point 1'   : self.fontMeasurements[name].get('point 1'),
                'glyph 2'   : self.fontMeasurements[name].get('glyph 2'),
                'point 2'   : self.fontMeasurements[name].get('point 2'),
                'parent'    : self.fontMeasurements[name].get('parent'),
                'units'     : None,
                'permill'   : None,
                'scale'     : None,
            }
            listItems.append(listItem)

        # replace None with empty string to avoid `<null>`
        items = []
        for item in listItems:
            listItem = { k : ('' if v is None else v) for k, v in item.items() }
            items.append(listItem)

        tab.measurements.set(items)

    def updateFontMeasurements(self):

        tab = self._tabs['font']

        items = tab.measurements.get()

        # clear measurement values
        if not self.font:
            for item in items:
                item['units']   = ''
                item['permill'] = ''
                item['scale']   = ''
            return

        # measure distances
        for item in items:
            M = Measurement(
                item['name'],
                item['direction'],
                item['glyph 1'], int(item['point 1']),
                item['glyph 2'], int(item['point 2']),
                item['parent'])

            distance = M.measure(self.font)

            if distance is None:
                item['units']   = ''
                item['permill'] = ''
                item['scale']   = ''
                continue

            item['units'] = distance

            # convert value to permill
            if distance and self.font.info.unitsPerEm:
                item['permill'] = round(distance * 1000 / self.font.info.unitsPerEm)

        # calculate scale in relation to parent
        distances = { i['name']: i['units'] for i in items }

        for item in items:
            distance = item['units']
            parent = item['parent']

            if parent is None or not len(parent) or parent not in distances:
                continue

            fontDistance = distances[parent]

            if distance == 0 and fontDistance == 0:
                item['scale'] = f'{1:.3f}'
            else:
                scaleValue = distance / float(fontDistance)
                item['scale'] = f'{scaleValue:.3f}'


    def newFontMeasurementCallback(self, sender):
        pass

    def editFontMeasurementCallback(self, sender):

        # tab       = self._tabs['font']
        # items     = tab.measurements.get()
        # selection = tab.measurements.getSelection()

        # if not selection:
        #     return

        # item = items[selection[0]]

        # name = item.get('name')
        # attrs = {
        #     'direction' : item.get('direction'),
        #     'glyph 1'   : item.get('glyph 1'),
        #     'point 1'   : item.get('point 1'),
        #     'glyph 2'   : item.get('glyph 2'),
        #     'point 2'   : item.get('point 2'),
        #     'parent'    : item.get('parent'),
        # }

        # self.fontMeasurements[name] = attrs

        self.updateFontMeasurements()

    # glyph

    def newGlyphMeasurementCallback(self, sender):
        pass

    def editGlyphMeasurementCallback(self, sender):
        pass

    def updateGlyphMeasurements(self):
        pass

    # def loadGlyphMeasurements(self, sender):
    #     '''
    #     Load all measurements from the glyph lib into the measurements list.

    #     '''
    #     tab = self._tabs['glyph']

    #     g = self.glyph
    #     if not g:
    #         tab.measurements.set([])
    #         return

    #     measurements = getLinks(g)

    #     listItems = []
    #     for key in measurements.keys():
    #         # get point or points
    #         keyParts = key.split()
    #         if len(keyParts) == 2:
    #             index1, index2 = keyParts
    #             index1, index2 = int(index1), int(index2)
    #         elif len(keyParts) == 1:
    #             index1 = keyParts[0].strip()
    #             index2 = None
    #         else:
    #             continue
    #         name = measurements[key].get('name')
    #         direction = measurements[key].get('direction')
    #         listItem = {
    #             'name'      : name,
    #             'direction' : direction, 
    #             'point 1'   : index1,
    #             'point 2'   : index2, 
    #         }   
    #         if index2 is not None:
    #             # get distance between points
    #             p1 = getPointAtIndex(g, index1)
    #             p2 = getPointAtIndex(g, index2)
    #             distance = getDistance((p1.x, p1.y), (p2.x, p2.y), listItem['direction'])
    #             listItem['units'] = distance
    #             listItem['permill'] = round(distance * 1000 / self.font.info.unitsPerEm)

    #         _listItem = {}
    #         for k, v in listItem.items():
    #             if v is None:
    #                v = '' 
    #             _listItem[k] = v
    #         listItems.append(_listItem)


    #     # # get font measurement
    #     # fontMeasurements = self._tabs['font'].measurements.get()
    #     # if name is not None:
    #     #     for m in fontMeasurements:
    #     #         if name == m['name']:
    #     #             fontDistance = m['units']
    #     #             break
    #     #         listItem['parent'] = fontDistance
    #     #         # get measurement scale
    #     #         if distance and fontDistance:
    #     #             scaleValue = distance / float(fontDistance)
    #     #             listItem['scale'] = f'{scaleValue:.3f}'


    #     tab.measurements.set(listItems)

    def updatePreviewCallback(self, sender):
        pass

    def measurementsColorCallback(self, sender):
        pass

    # ---------
    # observers
    # ---------

    def backgroundPreview(self, notification):
        pass

    def drawLabelCell(self, notification):
        pass

    # font

    def fontBecameCurrent(self, notification):
        self.font = notification['font']
        self.updateFontMeasurements()

    # glyph

    def currentGlyphChanged(self, notification):
        pass

    def glyphChangedObserver(self, notification):
        pass

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

    OpenWindow(Measurements2)


from importlib import reload
import variableValues.measurements
reload(variableValues.measurements)
import variableValues.dialogs.base
reload(variableValues.dialogs.base)

import AppKit
import os
from vanilla import * # Window, TextBox, List, Button, Tabs, LevelIndicatorListCell
from fontParts.world import OpenFont, RGlyph
from fontTools.pens.transformPen import TransformPointPen
from defcon.objects.component import _defaultTransformation
from drawBot.ui.drawView import DrawView
import drawBot as DB
from mojo.roboFont import OpenWindow
from variableValues.measurements import importMeasurementDescriptionsFromCSV, FontMeasurements
from variableValues.dialogs.base import DesignSpaceSelector


def drawGlyph(g):
    B = DB.BezierPath()
    g.draw(B)
    DB.drawPath(B)


class DecomposePointPen:

    def __init__(self, glyphSet, outPointPen):
        self._glyphSet = glyphSet
        self._outPointPen = outPointPen
        self.beginPath = outPointPen.beginPath
        self.endPath = outPointPen.endPath
        self.addPoint = outPointPen.addPoint

    def addComponent(self, baseGlyphName, transformation, *args, **kwargs):
        if baseGlyphName in self._glyphSet:
            baseGlyph = self._glyphSet[baseGlyphName]
            if transformation == _defaultTransformation:
                baseGlyph.drawPoints(self)
            else:
                transformPointPen = TransformPointPen(self, transformation)
                baseGlyph.drawPoints(transformPointPen)


# http://www.unicode.org/reports/tr44/#General_Category_Values
CONTEXTS = {
    'Ll' : 'non', # lowercase letter
    'Lu' : 'HOH', # uppercase letter
    'Lo' : 'non', # other letter
    'Lm' : 'non', # modifier letter
    'Nd' : '080', # decimal number
    'No' : '080', # other number
    'Zs' : 'non', # space separator
    'Sm' : '080', # math symbol
    'Pd' : 'non', # dash punctuation
    'Pi' : 'non', # initial punctuation
    'Pf' : 'non', # final punctuation
    'Ps' : 'HOH', # open punctuation
    'Pe' : 'HOH', # close punctuation
    'Po' : 'non', # other punctuation
    'Sk' : 'non', # modifier symbol
    'Sc' : '080', # currency symbol
    'So' : 'non', # other symbol
    'Mn' : 'non', # non-spacing mark
}


class VarFontAssistant(DesignSpaceSelector):
    
    title             = 'VarFont Assistant'
    key               = 'com.fontBureau.varFontAssistant'

    _tabsTitles       = ['designspace', 'font values', 'glyph values', 'kerning', 'measurements']

    _measurementFiles = {}
    _measurements     = {}

    _fontAttrs        = {
        'unitsPerEm'                   : 'unitsPerEm',
        'xHeight'                      : 'xHeight',
        'capHeight'                    : 'capHeight',
        'descender'                    : 'descender',
        'ascender'                     : 'ascender',
        'italicAngle'                  : 'italic angle',
        'openTypeOS2WeightClass'       : 'OS2 weight',
        'openTypeOS2WidthClass'        : 'OS2 width',
        'openTypeOS2WeightClass'       : 'OS2 weight',
        'openTypeOS2TypoAscender'      : 'OS2 typo ascender',
        'openTypeOS2TypoDescender'     : 'OS2 typo descender',
        'openTypeOS2TypoLineGap'       : 'OS2 line gap',
        'openTypeOS2WinAscent'         : 'OS2 win ascender',
        'openTypeOS2WinDescent'        : 'OS2 win descender',
        'openTypeOS2StrikeoutSize'     : 'OS2 strikeout size',
        'openTypeOS2StrikeoutPosition' : 'OS2 strikeout position',
        'openTypeHheaAscender'         : 'hhea ascender',
        'openTypeHheaDescender'        : 'hhea descender',
        'openTypeHheaLineGap'          : 'hhea line gap',
    }
    _fontValues       = {}

    _glyphNamesAll    = []
    _glyphAttrs       = ['width', 'leftMargin', 'rightMargin']
    _glyphValues      = {}

    _kerningPairsAll  = []
    _kerning          = {}




    def __init__(self):
        self.w = Window(
                (self.width, self.height), title=self.title,
                minSize=(self.width, 360))

        x = y = p = self.padding
        self.w.tabs = Tabs((x, y, -p, -p), self._tabsTitles)

        self.initializeDesignspacesTab()
        self.initializeFontValuesTab()
        self.initializeGlyphValuesTab()
        self.initializeKerningTab()
        self.initializeMeasurementsTab()

        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

    # initialize UI

    def initializeMeasurementsTab(self):

        tab = self._tabs['measurements']

        x = p = self.padding
        y = p/2
        col = self._colLeft
        x2 = x + col + p

        tab.measurementFilesLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'measurement files')

        y += self.lineHeight + p/2
        tab.measurementFiles = List(
                (x, y, -p, self.lineHeight*3),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                enableDelete=True,
                # editCallback=self.selectDesignspaceCallback,
                selectionCallback=self.selectMeasurementFileCallback,
                otherApplicationDropSettings=dict(
                    type=AppKit.NSFilenamesPboardType,
                    operation=AppKit.NSDragOperationCopy,
                    callback=self.dropMeasurementFileCallback),
                )

        y += self.lineHeight*3 + p
        tab.measurementsLabel = TextBox(
                (x, y, col, self.lineHeight),
                'measurements')

        y += self.lineHeight + p/2
        tab.measurements = List(
                (x, y, col, -(self.lineHeight + p*2)),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                selectionCallback=self.updateMeasurementsCallback,
            )

        y = self.lineHeight*4 + p*2
        tab.fontMeasurementsLabel = TextBox(
                (x2, y, -p, self.lineHeight),
                'values')

        columnDescriptions = [
            {
                "title"    : 'file name',
                'width'    : self._colFontName*1.5,
                'minWidth' : self._colFontName,
            },
            {
                "title"    : 'value',
                'width'    : self._colValue,
            },
            {
                "title"    : 'level',
                'width'    : self._colValue*1.5,
                'cell'     : LevelIndicatorListCell(style="continuous", maxValue=1600),
            },
        ]
        y += self.lineHeight + p/2
        tab.fontMeasurements = List(
                (x2, y, -p, -(self.lineHeight + p*2)),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                columnDescriptions=columnDescriptions,
                allowsSorting=True,
                # editCallback=self.editFontInfoValueCallback,
                enableDelete=False)

        y = -(self.lineHeight + p)
        tab.updateValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'load',
                callback=self.loadMeasurementsCallback,
            )

    def initializeFontValuesTab(self):

        tab = self._tabs['font values']

        x = p = self.padding
        y = p/2
        col = self._colLeft
        x2 = x + col + p

        tab.fontAttrsLabel = TextBox(
                (x, y, col, self.lineHeight),
                'attributes')

        y += self.lineHeight + p/2
        tab.fontAttrs = List(
                (x, y, col, -(self.lineHeight + p*2)),
                self._fontAttrs.values(),
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                selectionCallback=self.updateFontValuesCallback,
            )

        y = p/2
        tab.fontInfoLabel = TextBox(
                (x2, y, -p, self.lineHeight),
                'values')

        columnDescriptions = [
            {
                "title"    : 'file name',
                'width'    : self._colFontName*1.5,
                'minWidth' : self._colFontName,
            },
            {
                "title"    : 'value',
                'width'    : self._colValue,
            },
            {
                "title"    : 'level',
                'width'    : self._colValue*1.5,
                'cell'     : LevelIndicatorListCell(style="continuous", maxValue=1600),
            },
        ]
        y += self.lineHeight + p/2
        tab.fontValues = List(
                (x2, y, -p, -(self.lineHeight + p*2)),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                columnDescriptions=columnDescriptions,
                allowsSorting=True,
                # editCallback=self.editFontInfoValueCallback,
                enableDelete=False)

        y = -(self.lineHeight + p)
        tab.updateValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'load',
                callback=self.loadFontValuesCallback,
            )

        # x += self.buttonWidth + p
        # tab.visualizeValues = Button(
        #         (x, y, self.buttonWidth, self.lineHeight),
        #         'visualize',
        #         callback=self.visualizeFontValuesCallback,
        #     )

        # x += self.buttonWidth + p
        # tab.exportValues = Button(
        #         (x, y, self.buttonWidth, self.lineHeight),
        #         'export',
        #         # callback=self.exportFontValuesCallback,
        #     )

        x = -(p + self.buttonWidth)
        tab.saveFontValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'save',
                callback=self.saveFontValuesCallback,
            )

    def initializeGlyphValuesTab(self):

        tab = self._tabs['glyph values']

        x = p = self.padding
        y = p/2
        col = self._colLeft
        x2 = x + col + p

        tab.glyphLabel = TextBox(
                (x, y, col, self.lineHeight),
                'glyphs')

        tab.glyphCounter = TextBox(
                (x, y, col, self.lineHeight),
                '',
                alignment='right')

        y += self.lineHeight + p/2
        tab.glyphs = List(
                (x, y, col, -(self.lineHeight + p*2)),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                selectionCallback=self.updateGlyphValuesCallback)

        y = p/2
        tab.glyphAttrsLabel = TextBox(
                (x2, y, -p, self.lineHeight),
                'attributes')

        y += self.lineHeight + p/2
        tab.glyphAttrs = List(
                (x2, y, -p, self.lineHeight*7),
                self._glyphAttrs,
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                selectionCallback=self.updateGlyphValuesCallback)

        y += self.lineHeight*7 + p
        tab.glyphsLabel = TextBox(
                (x2, y, -p, self.lineHeight),
                'values')

        columnDescriptions = [
            {
                "title"    : 'file name',
                'width'    : self._colFontName*1.5,
                'minWidth' : self._colFontName,
            },
            {
                "title"    : 'value',
                'width'    : self._colValue,
            },
            {
                "title"    : 'level',
                'width'    : self._colValue*1.5,
                'cell'     : LevelIndicatorListCell(style="continuous", maxValue=1600),
            },
        ]
        y += self.lineHeight + p/2
        tab.glyphValues = List(
                (x2, y, -p, -(self.lineHeight + p*2)),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                columnDescriptions=columnDescriptions,
                allowsSorting=True,
                editCallback=self.editGlyphValueCallback,
                enableDelete=False)

        y = -(self.lineHeight + p)
        tab.loadValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'load',
                callback=self.loadGlyphAttributesCallback)

        # x += self.buttonWidth + p
        # tab.visualizeValues = Button(
        #         (x, y, self.buttonWidth, self.lineHeight),
        #         'visualize',
        #         # callback=self.visualizeGlyphValuesCallback,
        #     )

        # x += self.buttonWidth + p
        # tab.exportValues = Button(
        #         (x, y, self.buttonWidth, self.lineHeight),
        #         'export',
        #         # callback=self.exportGlyphValuesCallback,
        #     )

        x = -(p + self.buttonWidth)
        tab.saveValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'save',
                callback=self.saveGlyphValuesCallback)

    def initializeKerningTab(self):

        tab = self._tabs['kerning']

        x = p = self.padding
        y = p/2
        col = self._colLeft * 2
        tab.pairsLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'pairs')

        tab.pairsCounter = TextBox(
                (x, y, col, self.lineHeight),
                '',
                alignment='right')

        y += self.lineHeight + p/2
        tab.pairs = List(
                (x, y, col, -(self.lineHeight + p*2)),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                columnDescriptions=[{"title": t} for t in ['1st', '2nd']],
                selectionCallback=self.updateKerningValuesCallback,
            )

        x2 = x + col + p
        y = p/2

        # preview group

        kerningPreview = Group((0, 0, -0, -0))
        _x = _y = 0
        kerningPreview.label = TextBox(
                (_x, _y, -p, self.lineHeight),
                'preview')

        _y = self.lineHeight + p/2
        kerningPreview.canvas = DrawView((_x, _y, -p, -(self.lineHeight + p*2)))

        _y = -(self.lineHeight + p)
        kerningPreview.showMetrics = CheckBox(
            (_x, _y, self.buttonWidth, self.lineHeight),
            "show metrics",
            callback=self.updateKerningPreviewCallback,
            value=False)

        _x += self.buttonWidth + p
        kerningPreview.showKerning = CheckBox(
            (_x, _y, self.buttonWidth, self.lineHeight),
            "show kerning",
            callback=self.updateKerningPreviewCallback,
            value=True)

        # values group

        kerningValues = Group((0, 0, -0, -0))
        _x = 0
        _y = p/2
        kerningValues.label = TextBox(
                (_x, _y, -p, self.lineHeight),
                'values')

        _y += self.lineHeight + p/2
        columnDescriptions = [
            {
                "title"    : 'file name',
                'width'    : self._colFontName*1.5,
                'minWidth' : self._colFontName,
            },
            {
                "title"    : 'value',
                'width'    : self._colValue,
            },
            {
                "title"    : 'level',
                'width'    : self._colValue*1.5,
                'cell'     : LevelIndicatorListCell(style="continuous", maxValue=200),
            },
        ]
        kerningValues.list = List(
                (_x, _y, -p, -p),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                columnDescriptions=columnDescriptions,
                allowsSorting=True,
                #editCallback=self.editKerningCallback,
                enableDelete=False)

        # make splitview

        tab._splitDescriptors = [
            dict(view=kerningPreview, identifier="kerningPreview"),
            dict(view=kerningValues,  identifier="kerningValues"),
        ]
        tab.splitview = SplitView(
                (x2, y, -0, -(self.lineHeight+p)),
                tab._splitDescriptors,
                dividerStyle='thin',
                isVertical=False)

        y = -(self.lineHeight + p)
        tab.loadKerningValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'load',
                callback=self.loadKerningPairsCallback,
            )

        # x += self.buttonWidth + p
        # tab.visualizeValues = Button(
        #         (x, y, self.buttonWidth, self.lineHeight),
        #         'visualize',
        #         callback=self.visualizeKerningCallback,
        #     )

        # x += self.buttonWidth + p
        # tab.exportValues = Button(
        #         (x, y, self.buttonWidth, self.lineHeight),
        #         'export',
        #         callback=self.exportKerningCallback,
        #     )

        x = -(p + self.buttonWidth)
        tab.saveValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'save',
                callback=self.saveKerningCallback,
            )

    # -------------
    # dynamic attrs
    # -------------

    # fontinfo

    @property
    def selectedFontAttr(self):
        tab = self._tabs['font values']
        selection = tab.fontAttrs.getSelection()
        fontAttrs = tab.fontAttrs.get()
        selectedFontAttrs = [fontinfo for i, fontinfo in enumerate(fontAttrs) if i in selection]
        if not len(selectedFontAttrs):
            return
        return selectedFontAttrs[0]

    # measurements

    @property
    def selectedMeasurementFile(self):
        tab = self._tabs['measurements']
        selection = tab.measurementFiles.getSelection()
        measurementFiles = tab.measurementFiles.get()
        selectedMeasurementFiles = [measurementFile for i, measurementFile in enumerate(measurementFiles) if i in selection]
        if not len(selectedMeasurementFiles):
            return
        return selectedMeasurementFiles[0]

    @property
    def selectedMeasurement(self):
        tab = self._tabs['measurements']
        selection = tab.measurements.getSelection()
        measurements = tab.measurements.get()
        selectedMeasurements = [m for i, m in enumerate(measurements) if i in selection]
        if not len(selectedMeasurements):
            return
        return selectedMeasurements[0]

    # glyph values

    @property
    def selectedGlyphName(self):
        tab = self._tabs['glyph values']
        i = tab.glyphs.getSelection()[0]
        return self._glyphNamesAll[i], i

    @property
    def selectedGlyphAttrs(self):
        tab = self._tabs['glyph values']
        selection = tab.glyphAttrs.getSelection()
        glyphAttrs = tab.glyphAttrs.get()
        selectedGlyphAttrs = [a for i, a in enumerate(glyphAttrs) if i in selection]
        if not len(selectedGlyphAttrs):
            return
        return selectedGlyphAttrs

    # kerning

    @property
    def selectedKerningPair(self):
        tab = self._tabs['kerning']
        i = tab.pairs.getSelection()[0]
        return self._kerningPairsAll[i], i

    @property
    def selectedKerningValue(self):
        tab = self._tabs['kerning']
        group = tab._splitDescriptors[1]['view']
        selection = group.list.getSelection()
        if not len(selection):
            return
        i = selection[0]
        item = group.list.get()[i]
        return item

    @property
    def showMetrics(self):
        tab = self._tabs['kerning']
        group = tab._splitDescriptors[0]['view']
        return group.showMetrics.get()

    @property
    def showKerning(self):
        tab = self._tabs['kerning']
        group = tab._splitDescriptors[0]['view']
        return group.showKerning.get()

    # ---------
    # callbacks
    # ---------

    # font info values

    def loadFontValuesCallback(self, sender):

        if not self.selectedSources:
            return

        tab = self._tabs['font values']

        # empty list
        if not self.selectedDesignspace:
            tab.fontInfo.set([])
            return

        # collect fontinfo values into dict
        self._fontValues = {}
        for source in self.selectedSources:
            sourceFileName = source['file name']
            sourcePath = self._sources[sourceFileName]
            f = OpenFont(sourcePath, showInterface=False)
            info = f.info.asDict()
            self._fontValues[sourceFileName] = {}
            for attr, attrLabel in self._fontAttrs.items():
                self._fontValues[sourceFileName][attrLabel] = info.get(attr)
            f.close()

        self.updateFontValuesCallback(None)

    def updateFontValuesCallback(self, sender):

        tab = self._tabs['font values']

        if not self.selectedSources or not self._fontValues:
            tab.fontValues.set([])
            return

        fontAttr = self.selectedFontAttr

        if self.verbose:
            print('updating font info values...\n')

        # create list items
        values = []
        fontInfoItems = []
        for fontName in self._fontValues.keys():
            value = self._fontValues[fontName][fontAttr]
            if value is None:
                value = '—'
            listItem = {
                "file name" : fontName,
                "value"     : value,
                "level"     : abs(value),
            }
            fontInfoItems.append(listItem)
            values.append(value)

        # set glyph values in table
        fontInfoValuesPosSize = tab.fontValues.getPosSize()
        del tab.fontValues

        columnDescriptions = [
            {
                "title"    : 'file name',
                'width'    : self._colFontName*1.5,
                'minWidth' : self._colFontName,
                'maxWidth' : self._colFontName*3,
            },
            {
                "title"    : 'value',
                'width'    : self._colValue,
            },
            {
                "title"    : 'level',
                'width'    : self._colValue*1.5,
                'cell'     : LevelIndicatorListCell(style="continuous", minValue=min(values), maxValue=max(values)),
            },
        ]
        tab.fontValues = List(
            fontInfoValuesPosSize,
            fontInfoItems,
            allowsMultipleSelection=False,
            allowsEmptySelection=False,
            columnDescriptions=columnDescriptions,
            allowsSorting=True,
            editCallback=self.editFontValueCallback,
            enableDelete=False)

    def visualizeFontValuesCallback(self, sender):
        print('visualize font infos')

    def editFontValueCallback(self, sender):
        '''
        Save the edited font value back to the dict, so we can load values for another attribute.

        '''
        tab = self._tabs['font values']
        selection = tab.fontValues.getSelection()
        if not len(selection):
            return

        i = selection[0]
        item = tab.fontValues.get()[i]

        # save change to internal dict
        fontAttr = self.selectedFontAttr
        fontName = item['file name']
        newValue = item['value']
        oldValue = self._fontValues[fontName].get(fontAttr)
        if oldValue != newValue:
            if self.verbose:
                print(f'changed font value {fontAttr} in {fontName}: {oldValue} → {newValue}\n')
            self._fontValues[fontName][fontAttr] = int(newValue)

    def exportFontValuesCallback(self, sender):
        '''
        Export current font values as a CSV file.

        '''
        pass

    def saveFontValuesCallback(self, sender):
        '''
        Save the edited font values back into their source fonts.

        '''
        tab = self._tabs['font values']
        fontAttrs = { v: k for k, v in self._fontAttrs.items() }

        if self.verbose:
            print('saving edited font values to sources...')

        for fontName in self._fontValues.keys():
            sourcePath = self._sources[fontName]
            f = OpenFont(sourcePath, showInterface=False)
            fontChanged = False

            # for attr in self._fontValues[fontName]:
            for attr, newValue in self._fontValues[fontName].items():
                fontAttr = fontAttrs[attr]
                if newValue is None:
                    continue
                if type(newValue) is str:
                    if not len(newValue.strip()):
                        continue
                newValue = float(newValue)
                if newValue.is_integer():
                    newValue = int(newValue)
                oldValue = getattr(f.info, fontAttr)
                if newValue != oldValue:
                    if self.verbose:
                        print(f'\twriting new value for {attr} in {fontName}: {oldValue} → {newValue}')
                    setattr(f.info, fontAttr, newValue)
                    if not fontChanged:
                        fontChanged = True
            if fontChanged:
                # if self.verbose:
                #     print(f'\tsaving {fontName}...')
                f.save()
            f.close()

        if self.verbose:
            print('...done.\n')

    # measurements

    def dropMeasurementFileCallback(self, sender, dropInfo):
        isProposal = dropInfo["isProposal"]
        existingPaths = sender.get()

        paths = dropInfo["data"]
        paths = [path for path in paths if path not in existingPaths]
        paths = [path for path in paths if os.path.splitext(path)[-1].lower() == '.csv']

        if not paths:
            return False

        if not isProposal:
            tab = self._tabs['measurements']
            for path in paths:
                label = os.path.splitext(os.path.split(path)[-1])[0]
                self._measurementFiles[label] = path
                tab.measurementFiles.append(label)
                tab.measurementFiles.setSelection([0])

        return True

    def loadMeasurementsCallback(self, sender):

        if not self.selectedSources:
            return

        tab = self._tabs['measurements']

        # empty list
        if not self.selectedDesignspace:
            tab.fontMeasurements.set([])
            return

        # collect measurements into dict
        measurementFilePath = self._measurementFiles[self.selectedMeasurementFile]
        measurementTuples = importMeasurementDescriptionsFromCSV(measurementFilePath)

        self._measurements = {}
        for source in self.selectedSources:
            sourceFileName = source['file name']
            sourcePath = self._sources[sourceFileName]
            f = OpenFont(sourcePath, showInterface=False)

            self._measurements[sourceFileName] = {}
            M = FontMeasurements(f, measurementTuples)
            for key, measurement in M.measurements.items():
                self._measurements[sourceFileName][key] = measurement.value
            f.close()
        
        self.updateMeasurementsCallback(None)

    def selectMeasurementFileCallback(self, sender):

        tab = self._tabs['measurements']

        if not self.selectedMeasurementFile:
            tab.measurements.set([])
            return

        measurementFilePath = self._measurementFiles[self.selectedMeasurementFile]
        measurementTuples = importMeasurementDescriptionsFromCSV(measurementFilePath)
        measurementNames = [m[0] for m in measurementTuples]
        tab.measurements.set(measurementNames)

    def updateMeasurementsCallback(self, sender):

        tab = self._tabs['measurements']

        if not self.selectedSources or not self._measurements:
            tab.fontMeasurements.set([])
            return

        measurementName = self.selectedMeasurement

        if self.verbose:
            print('updating font measurements...\n')

        # create list items
        values = []
        measurementItems = []
        for fontName in self._measurements.keys():
            value = self._measurements[fontName][measurementName]
            listItem = {
                "file name" : fontName,
                "value"     : value,
                "level"     : abs(value),
            }
            measurementItems.append(listItem)
            values.append(value)

        # set measurement values in table
        fontMeasurementsPosSize = tab.fontMeasurements.getPosSize()
        del tab.fontMeasurements

        columnDescriptions  = [
            {
                "title"    : 'file name',
                'width'    : self._colFontName*1.5,
                'minWidth' : self._colFontName,
                'maxWidth' : self._colFontName*3,
            },
            {
                "title"    : 'value',
                'width'    : self._colValue,
            },
            {
                "title"    : 'level',
                'width'    : self._colValue*1.5,
                'cell'     : LevelIndicatorListCell(style="continuous", minValue=min(values), maxValue=max(values)),
            },
        ]
        tab.fontMeasurements = List(
                fontMeasurementsPosSize,
                measurementItems,
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                columnDescriptions=columnDescriptions,
                allowsSorting=True,
                # editCallback=self.editGlyphValueCallback,
                enableDelete=False)

    def visualizeMeasurementsCallback(self, sender):
        pass

    def exportMeasurementsCallback(self, sender):
        '''
        Export measurement values as a CSV file.

        '''
        pass

    # glyph values

    def loadGlyphAttributesCallback(self, sender):
        '''
        Read glyph names and glyph values from selected sources and update UI.

        '''

        tab = self._tabs['glyph values']

        # collect glyph names and glyph values in selected fonts
        allGlyphs = []
        self._glyphValues = {}
    
        for source in self.selectedSources:
            sourceFileName = source['file name']
            sourcePath = self._sources[sourceFileName]
            f = OpenFont(sourcePath, showInterface=False)
            allGlyphs += f.keys()
            self._glyphValues[sourceFileName] = {}
            for glyphName in f.keys():
                self._glyphValues[sourceFileName][glyphName] = {}
                for attr in self._glyphAttrs:
                    value = getattr(f[glyphName], attr)
                    self._glyphValues[sourceFileName][glyphName][attr] = value
            f.close()

        # store all pairs in dict
        self._glyphNamesAll = list(set(allGlyphs))
        self._glyphNamesAll.sort()

        # update glyphs column
        tab.glyphs.set(self._glyphNamesAll)

    def updateGlyphValuesCallback(self, sender):
        '''
        Update table with sources and glyph values based on the currently selected glyph attribute.

        '''
        tab = self._tabs['glyph values']

        if not self.selectedSources or not self.selectedGlyphAttrs:
            tab.glyphValues.set([])
            return

        glyphName, glyphIndex = self.selectedGlyphName
        glyphAttr  = self.selectedGlyphAttrs[0]

        if self.verbose:
            print(f'updating glyph values for glyph {glyphName} ({glyphIndex})...\n')

        # create list items
        values = []
        glyphValuesItems = []
        for fontName in self._glyphValues.keys():
            value = self._glyphValues[fontName][glyphName][glyphAttr] if glyphName in self._glyphValues[fontName] else 0
            listItem = {
                "file name" : fontName,
                "value"     : value,
                "level"     : abs(value),
            }
            glyphValuesItems.append(listItem)
            values.append(value)

        # set glyph values in table
        glyphValuesPosSize = tab.glyphValues.getPosSize()
        del tab.glyphValues

        columnDescriptions = [
            {
                "title"    : 'file name',
                'width'    : self._colFontName*1.5,
                'minWidth' : self._colFontName,
                'maxWidth' : self._colFontName*3,
            },
            {
                "title"    : 'value',
                'width'    : self._colValue,
            },
            {
                "title"    : 'level',
                'width'    : self._colValue*1.5,
                'cell'     : LevelIndicatorListCell(style="continuous", minValue=min(values), maxValue=max(values)),
            },
        ]
        tab.glyphValues = List(
                glyphValuesPosSize,
                glyphValuesItems,
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                columnDescriptions=columnDescriptions,
                allowsSorting=True,
                editCallback=self.editGlyphValueCallback,
                enableDelete=False)

        # update pairs list label
        tab.glyphCounter.set(f'{glyphIndex+1} / {len(self._glyphNamesAll)}')

    def editGlyphValueCallback(self, sender):
        '''
        Save the edited glyph value back to the dict, so we can load values for another glyph or attribute.

        '''
        tab = self._tabs['glyph values']
        selection = tab.glyphValues.getSelection()
        if not len(selection):
            return

        i = selection[0]
        item = tab.glyphValues.get()[i]
        glyphAttr  = self.selectedGlyphAttrs[0]

        # save change to internal dict
        glyphName, glyphIndex = self.selectedGlyphName
        fontName = item['file name']
        newValue = item['value']
        oldValue = self._glyphValues[fontName][glyphName][glyphAttr]
        if oldValue != newValue:
            if self.verbose:
                print(f'changed {glyphName}.{glyphAttr} in {fontName}: {oldValue} → {newValue}\n')
            self._glyphValues[fontName][glyphName][glyphAttr] = int(newValue)

    def visualizeGlyphValuesCallback(self, sender):
        pass

    def exportGlyphValuesCallback(self, sender):
        '''
        Export current glyph values as a CSV file.

        '''
        pass

    def saveGlyphValuesCallback(self, sender):
        '''
        Save the edited glyph values back into their source fonts.

        '''
        tab = self._tabs['kerning']

        if self.verbose:
            print('saving edited glyph values to sources...')

        for fontName in self._glyphValues.keys():
            sourcePath = self._sources[fontName]
            f = OpenFont(sourcePath, showInterface=False)
            fontChanged = False
            for glyphName in self._glyphValues[fontName]:
                for attr, newValue in self._glyphValues[fontName][glyphName].items():
                    if newValue is None:
                        continue
                    if type(newValue) is str:
                        if not len(newValue.strip()):
                            continue
                    newValue = float(newValue)
                    if newValue.is_integer():
                        newValue = int(newValue)
                    oldValue = getattr(f[glyphName], attr)
                    if newValue != oldValue:
                        if self.verbose:
                            print(f'\twriting new value for {glyphName}.{attr} in {fontName}: {oldValue} → {newValue}')
                        setattr(f[glyphName], attr, newValue)
                        if not fontChanged:
                            fontChanged = True
            if fontChanged:
                # if self.verbose:
                #     print(f'\tsaving {fontName}...')
                f.save()
            f.close()

        if self.verbose:
            print('...done.\n')

    # kerning

    def loadKerningPairsCallback(self, sender):
        '''
        Load kerning pairs and values from selected sources into the UI.

        '''
        if not self.selectedSources:
            return

        tab = self._tabs['kerning']
        
        # collect pairs and kerning values in selected sources
        allPairs = []
        self._kerning = {}
        for source in self.selectedSources:
            sourceFileName = source['file name']
            sourcePath = self._sources[sourceFileName]
            f = OpenFont(sourcePath, showInterface=False)
            allPairs += f.kerning.keys()
            self._kerning[sourceFileName] = {}
            for pair, value in f.kerning.items():
                self._kerning[sourceFileName][pair] = value
        self._kerningPairsAll = list(set(allPairs))
        self._kerningPairsAll.sort()

        # update pairs column
        pairListItems = []
        for g1, g2 in sorted(self._kerningPairsAll):
            pairItem = {'1st': g1, '2nd': g2}
            pairListItems.append(pairItem)
        tab.pairs.set(pairListItems)

    def updateKerningValuesCallback(self, sender):
        '''
        Update table with sources and kerning values based on the currently selected kerning pair.

        '''
        tab = self._tabs['kerning']
        group = tab._splitDescriptors[1]['view']

        if not self.selectedSources:
            group.list.set([])
            return

        pair, pairIndex = self.selectedKerningPair

        if self.verbose:
            print(f'updating kerning values for pair {pair} ({pairIndex})...\n')

        # create list items
        values = []
        for fontName in self._kerning.keys():
            value = self._kerning[fontName][pair] if pair in self._kerning[fontName] else 0
            values.append(value)
        valuesMax = max(values) - min(values)

        kerningListItems = []
        for i, fontName in enumerate(self._kerning.keys()):
            value = values[i]
            listItem = {
                "file name" : fontName,
                "value"     : value,
                "level"     : value-min(values),
            }
            kerningListItems.append(listItem)

        # set kerning values in table
        kerningValuesPosSize = group.list.getPosSize()
        del group.list

        columnDescriptions = [
            {
                "title"    : 'file name',
                'width'    : self._colFontName*1.5,
                'minWidth' : self._colFontName,
                'maxWidth' : self._colFontName*3,
            },
            {
                "title"    : 'value',
                'width'    : self._colValue,
            },
            {
                "title"    : 'level',
                'width'    : self._colValue*1.5,
                'cell'     : LevelIndicatorListCell(style="continuous", minValue=0, maxValue=valuesMax),
            },
        ]
        group.list = List(
                kerningValuesPosSize,
                kerningListItems,
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                columnDescriptions=columnDescriptions,
                allowsSorting=True,
                editCallback=self.editKerningCallback,
                enableDelete=False)

        # update kerning pair counter (current/total)
        tab.pairsCounter.set(f'{pairIndex+1} / {len(self._kerningPairsAll)}')

        self.updateKerningPreviewCallback(None)

    def updateKerningPreviewCallback(self, sender):
        tab = self._tabs['kerning']
        groupPreview = tab._splitDescriptors[0]['view']
        groupValues = tab._splitDescriptors[0]['view']

        sampleWidth  = 800
        sampleHeight = 100

        pair, pairIndex = self.selectedKerningPair

        DB.newDrawing()
        DB.newPage(sampleWidth, len(self._kerning)*sampleHeight)
        DB.blendMode('multiply')

        s = 0.045
        x = 10
        y = DB.height() - sampleHeight*0.8

        for fontName in self._kerning.keys():

            ufoPath = self._sources[fontName]

            f = OpenFont(ufoPath, showInterface=False)

            # make a list of glyph/group names to get values from
            gName1, gName2 = pair

            # make a list of glyph names to create the preview
            if gName1.startswith('public.kern'):
                gName1 = f.groups[gName1][0]
            if gName2.startswith('public.kern'):
                gName2 = f.groups[gName2][0]

            # get context for string
            cat1 = f.naked().unicodeData.categoryForGlyphName(gName1)
            cat2 = f.naked().unicodeData.categoryForGlyphName(gName2)

            glyphsPre   = list(CONTEXTS[cat1] if cat1 in CONTEXTS else 'HOH')
            glyphsAfter = list(CONTEXTS[cat2] if cat2 in CONTEXTS else 'HOH')

            glyphsPre   = [f.naked().unicodeData.glyphNameForUnicode(ord(char)) for char in glyphsPre]
            glyphsAfter = [f.naked().unicodeData.glyphNameForUnicode(ord(char)) for char in glyphsAfter]

            gNames     = glyphsPre + [gName1, gName2] + glyphsAfter
            glyphNames = glyphsPre + [gName1, gName2] + glyphsAfter

            # draw the preview

            _x = x
            DB.save()
            for i, glyphName in enumerate(glyphNames):
                g = f[glyphName]

                # flatten components
                if len(g.components):
                    _g = RGlyph()
                    pointPen = _g.getPointPen()
                    decomposePen = DecomposePointPen(f, pointPen)
                    g.drawPoints(decomposePen)
                    _g.width = g.width
                    g = _g

                DB.save()
                DB.translate(_x, y)
                DB.scale(s)

                # draw glyph margins
                if self.showMetrics:
                    DB.strokeWidth(1)
                    DB.stroke(1, 0, 0)
                    DB.line((0, -f.info.unitsPerEm*0.2), (0, f.info.unitsPerEm*0.8))

                DB.stroke(None)
                DB.fill(0)
                drawGlyph(g)

                if not i < len(glyphNames)-1:
                    continue

                # get glyph for preview
                gNameNext = gNames[i+1]
                if gNameNext.startswith('public.kern'):
                    glyphNameNext = f.groups[gNameNext][0]
                else:
                    glyphNameNext = gNameNext
                gNext = f[glyphNameNext]

                # get glyph/group for current glyph name
                gName = gNames[i]

                # get value for pair
                value = self._kerning[fontName].get((gName, gNameNext)) # f.kerning.get((gName, gNameNext)) # f.kerning.find((gName, gNameNext))

                if value:
                    # draw kerning value
                    if self.showKerning:
                        DB.fill(1, 0, 0, 0.3)
                        DB.rect(g.width + value, -f.info.unitsPerEm*0.2, -value, f.info.unitsPerEm)

                    # apply kern value with next glyph
                    _x += value*s

                DB.restore()

                # advance to next glyph
                _x += g.width*s

            DB.restore()
            y -= sampleHeight

        # refresh preview
        pdfData = DB.pdfImage()
        groupPreview.canvas.setPDFDocument(pdfData)

    def editKerningCallback(self, sender):
        '''
        Save the edited kerning pair back to the dict, so we can load values for another pair.

        '''
        tab = self._tabs['kerning']
        item = self.selectedKerningValue

        # save change to internal dict
        pair, pairIndex = self.selectedKerningPair
        fontName = item['file name']
        newValue = item['value']
        oldValue = self._kerning[fontName].get(pair)
        if oldValue != newValue:
            if self.verbose:
                print(f'changed kerning pair {pair} in {fontName}: {oldValue} → {newValue}\n')
            self._kerning[fontName][pair] = int(newValue)

        # update level indicator
        ### this will crash RF3!!
        # kerningListItems = []
        # for fontName in self._kerning.keys():
        #     value = self._kerning[fontName][pair] if pair in self._kerning[fontName] else 0
        #     listItem = {
        #         "file name" : fontName,
        #         "value"     : value,
        #         "level"     : abs(value),
        #     }
        #     kerningListItems.append(listItem)
        # tab.kerningValues.set(kerningListItems)

        self.updateKerningPreviewCallback(None)

    def visualizeKerningCallback(self, sender):
        pass

    def exportKerningCallback(self, sender):
        pass

    def saveKerningCallback(self, sender):
        '''
        Save the edited kerning values back into their source fonts.

        '''
        tab = self._tabs['kerning']

        if self.verbose:
            print('saving edited kerning values to sources...')

        for fontName in self._kerning.keys():
            sourcePath = self._sources[fontName]
            f = OpenFont(sourcePath, showInterface=False)
            fontChanged = False
            for pair, newValue in self._kerning[fontName].items():
                if type(newValue) not in [int, float]:
                    if not len(newValue.strip()):
                        continue
                newValue = int(newValue)
                oldValue = f.kerning.get(pair)
                if newValue != oldValue:
                    if newValue == 0:
                        if self.verbose:
                            print(f"\tdeleting {pair} in '{fontName}'...")
                        del f.kerning[pair]
                    else:
                        if self.verbose:
                            print(f"\twriting new value for {pair} in '{fontName}': {oldValue} → {newValue}")
                        f.kerning[pair] = newValue
                    if not fontChanged:
                        fontChanged = True
            if fontChanged:
                # if self.verbose:
                #     print(f'\tsaving {fontName}...')
                f.save()
            f.close()

        if self.verbose:
            print('...done.\n')


# ----
# test
# ----

if __name__ == '__main__':

    OpenWindow(VarFontAssistant)


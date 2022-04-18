import os, csv
from vanilla import *
from AppKit import NSFilenamesPboardType, NSDragOperationCopy
from mojo.roboFont import OpenWindow
from fontParts.world import OpenFont
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.agl import UV2AGL


class VarFontAssistant:
    
    title             = 'VarFont Assistant'
    key               = 'com.hipertipo.varFontAssistant'
    width             = 123*4
    height            = 640
    padding           = 10
    lineHeight        = 22
    verbose           = True
    buttonWidth       = 100

    _colFontName      = 240
    _colValue         = 80

    _tabsTitles       = [
        "designspace",
        "fontinfo",
        "glyphs",
        "measurements"
    ]

    _designspaces     = {}
    _axes             = {}
    _sources          = {}
    
    _measurementFiles = {}
    _measurements     = {}

    _fontinfoAttrs    = {
        'unitsPerEm'             : 'unitsPerEm',
        'xHeight'                : 'xHeight',
        'capHeight'              : 'capHeight',
        'descender'              : 'descender',
        'ascender'               : 'ascender',
        'italicAngle'            : 'italic angle',
        'openTypeOS2WeightClass' : 'OS2 weight',
        'openTypeOS2WidthClass'  : 'OS2 width',
    }
    _fontinfo         = {}

    _glyphAttrs       = ['width', 'leftMargin', 'rightMargin']
    _glyphValues      = {}

    def __init__(self):
        self.w = FloatingWindow(
                (self.width, self.height), title=self.title,
                minSize=(self.width, 360))

        x = y = p = self.padding
        self.w.tabs = Tabs((x, y, -p, -p), self._tabsTitles)

        self.initializeDesignspacesTab()
        self.initializeFontInfoTab()
        self.initializeMeasurementsTab()
        self.initializeGlyphsTab()

        self.w.open()

    # initialize UI

    def initializeDesignspacesTab(self):

        tab = self._tabs['designspace']
        
        x = p = self.padding
        y = p/2
        tab.designspacesLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'designspaces')

        y += self.lineHeight + p/2
        tab.designspaces = List(
                (x, y, -p, self.lineHeight*5),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                enableDelete=True,
                # editCallback=self.selectDesignspaceCallback,
                selectionCallback=self.selectDesignspaceCallback,
                otherApplicationDropSettings=dict(
                    type=NSFilenamesPboardType,
                    operation=NSDragOperationCopy,
                    callback=self.dropDesignspaceCallback),
                )

        y += self.lineHeight*5 + p
        tab.axesLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'axes')

        y += self.lineHeight + p/2
        tab.axes = List(
                (x, y, -p, self.lineHeight*5),
                [],
            )

        y += self.lineHeight*5 + p
        tab.sourcesLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'sources')

        y += self.lineHeight + p/2
        tab.sources = List(
                (x, y, -p, -(self.lineHeight + p*2)),
                [],
            )

        # y = -(self.lineHeight + p)
        # tab.updateValues = Button(
        #         (x, y, self.buttonWidth, self.lineHeight),
        #         'update all',
        #         # callback=self.updateFontinfoCallback,
        #     )

    def initializeMeasurementsTab(self):

        tab = self._tabs['measurements']

        x = p = self.padding
        y = p/2
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
                selectionCallback=self.selectMeasurementFileCallback,
                otherApplicationDropSettings=dict(
                    type=NSFilenamesPboardType,
                    operation=NSDragOperationCopy,
                    callback=self.dropMeasurementFileCallback),
            )

        y += self.lineHeight*3 + p
        tab.measurementsLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'measurements')

        y += self.lineHeight + p/2
        tab.measurements = List(
                (x, y, -p, self.lineHeight*7),
                [],
            )

        y += self.lineHeight*7 + p
        tab.valuesLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'values')

        y += self.lineHeight + p/2
        tab.values = List(
                (x, y, -p, -(self.lineHeight + p*2)),
                [],
            )

        y = -(self.lineHeight + p)
        tab.updateValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'update',
                callback=self.updateMeasurementsCallback,
            )

        x += self.buttonWidth + p
        tab.visualizeValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'visualize',
                callback=self.visualizeMeasurementsCallback,
            )

        x += self.buttonWidth + p
        tab.exportValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'export',
                # callback=self.visualizeFontinfoCallback,
            )

        # x = -(p + self.buttonWidth)
        # tab.saveValues = Button(
        #         (x, y, self.buttonWidth, self.lineHeight),
        #         'save',
        #         # callback=self.visualizeFontinfoCallback,
        #     )

    def initializeFontInfoTab(self):

        tab = self._tabs['fontinfo']

        x = p = self.padding
        y = p/2

        tab.fontinfoAttrsLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'font info attributes')

        y += self.lineHeight + p/2
        tab.fontinfoAttrs = List(
                (x, y, -p, self.lineHeight*8),
                self._fontinfoAttrs.keys(),
                allowsMultipleSelection=True,
                allowsEmptySelection=False,
            )

        y += self.lineHeight*8 + p
        tab.fontinfoLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'font info values')

        y += self.lineHeight + p/2
        tab.fontinfo = List(
                (x, y, -p, -(self.lineHeight + p*2)),
                [],
                # allowsMultipleSelection=False,
                # allowsEmptySelection=False,
                # enableDelete=True,
                # selectionCallback=self.selectMeasurementFileCallback,
                # columnDescriptions=fontinfoDescriptions,
            )

        y = -(self.lineHeight + p)
        tab.updateValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'update',
                callback=self.updateFontinfoCallback,
            )

        x += self.buttonWidth + p
        tab.visualizeValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'visualize',
                callback=self.visualizeFontinfoCallback,
            )

        x += self.buttonWidth + p
        tab.exportValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'export',
                # callback=self.visualizeFontinfoCallback,
            )

        x = -(p + self.buttonWidth)
        tab.saveValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'save',
                # callback=self.visualizeFontinfoCallback,
            )

    def initializeGlyphsTab(self):

        tab = self._tabs['glyphs']

        x = p = self.padding
        y = p/2
        
        col = 120

        tab.glyphAttrsLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'glyph attributes')

        y += self.lineHeight + p/2
        tab.glyphAttrs = List(
                (x, y, -p, self.lineHeight*5),
                self._glyphAttrs,
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
            )

        y += self.lineHeight*5 + p
        tab.glyphNamesLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'glyph names')

        y += self.lineHeight + p/2
        tab.glyphNames = EditText(
                (x, y, -p, self.lineHeight*3),
                'A B C D a b c d zero one two three',
            )

        y += self.lineHeight*3 + p
        tab.glyphsLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'glyph values')

        y += self.lineHeight + p/2
        tab.glyphValues = List(
                (x, y, -p, -(self.lineHeight + p*2)),
                [],
                # allowsMultipleSelection=False,
                # allowsEmptySelection=False,
                # enableDelete=True,
                # selectionCallback=self.selectMeasurementFileCallback,
                # columnDescriptions=fontinfoDescriptions,
            )

        y = -(self.lineHeight + p)
        tab.updateValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'update',
                callback=self.updateGlyphValuesCallback,
            )

        x += self.buttonWidth + p
        tab.visualizeValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'visualize',
                # callback=self.visualizeFontinfoCallback,
            )

        x += self.buttonWidth + p
        tab.exportValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'export',
                # callback=self.visualizeFontinfoCallback,
            )

        x = -(p + self.buttonWidth)
        tab.saveValues = Button(
                (x, y, self.buttonWidth, self.lineHeight),
                'save',
                # callback=self.visualizeFontinfoCallback,
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

    # designspace

    @property
    def selectedDesignspace(self):
        tab = self._tabs['designspace']
        selection = tab.designspaces.getSelection()
        designspaces = tab.designspaces.get()
        selectedDesignspaces = [designspace for i, designspace in enumerate(designspaces) if i in selection]
        if not len(selectedDesignspaces):
            return
        return selectedDesignspaces[0]

    @property
    def selectedDesignspaceDocument(self):
        if not self.selectedDesignspace:
            return
        designspacePath = self._designspaces[self.selectedDesignspace]
        designspace = DesignSpaceDocument()
        designspace.read(designspacePath)
        return designspace

    @property
    def selectedSources(self):
        tab = self._tabs['designspace']
        selection = tab.sources.getSelection()
        sources = tab.sources.get()
        selectedSources = [source for i, source in enumerate(sources) if i in selection]
        if not len(selectedSources):
            return
        return selectedSources

    # fontinfo

    @property
    def selectedFontinfoAttrs(self):
        tab = self._tabs['fontinfo']
        selection = tab.fontinfoAttrs.getSelection()
        fontinfoAttrs = tab.fontinfoAttrs.get()
        selectedFontinfoAttrs = [fontinfo for i, fontinfo in enumerate(fontinfoAttrs) if i in selection]
        if not len(selectedFontinfoAttrs):
            return
        return selectedFontinfoAttrs

    # measurements

    @property
    def selectedMeasurementFile(self):
        tab = self._tabs['measurements']
        selection = tab.measurementFiles.getSelection()
        measurementFiles = tab.measurementFiles.get()
        return [measurementFile for i, measurementFiles in enumerate(measurementFiles)] if len(measurementFiles) else None

    @property
    def selectedMeasurements(self):
        tab = self._tabs['measurements']
        selection = tab.measurements.getSelection()
        measurements = tab.measurements.get()
        selectedMeasurements = [measurement for i, measurement in enumerate(measurements) if i in selection]
        if not len(selectedMeasurements):
            return
        return selectedMeasurements

    # glyph values

    @property
    def selectedGlyphAttrs(self):
        tab = self._tabs['glyphs']
        selection = tab.glyphAttrs.getSelection()
        glyphAttrs = tab.glyphAttrs.get()
        selectedGlyphAttrs = [a for i, a in enumerate(glyphAttrs) if i in selection]
        if not len(selectedGlyphAttrs):
            return
        return selectedGlyphAttrs

    # ---------
    # callbacks
    # ---------

    # designspace

    def dropDesignspaceCallback(self, sender, dropInfo):
        isProposal = dropInfo["isProposal"]
        existingPaths = sender.get()

        paths = dropInfo["data"]
        paths = [path for path in paths if path not in existingPaths]
        paths = [path for path in paths if os.path.splitext(path)[-1].lower() == '.designspace']

        if not paths:
            return False

        if not isProposal:
            tab = self._tabs['designspace']
            for path in paths:
                label = os.path.splitext(os.path.split(path)[-1])[0]
                self._designspaces[label] = path
                tab.designspaces.append(label)
                tab.designspaces.setSelection([0])

        return True

    def selectDesignspaceCallback(self, sender):

        tab = self._tabs['designspace']

        # -----------
        # reset lists
        # -----------

        axesPosSize    = tab.axes.getPosSize()
        sourcesPosSize = tab.sources.getPosSize()
        del tab.axes
        del tab.sources

        # -----------
        # empty lists
        # -----------

        if not self.selectedDesignspace:
            tab.axes    = List(axesPosSize, [])
            tab.sources = List(sourcesPosSize, [])
            return

        # ------------------------
        # get selected designspace
        # ------------------------
        
        designspace = self.selectedDesignspaceDocument 

        # -----------
        # update axes
        # -----------

        # get column descriptions
        axesTitles  = ['name', 'tag', 'minimum', 'maximum', 'default']
        axesDescriptions = [{"title": D} for D in axesTitles]
        
        # make list items
        self._axes = {}
        axesItems = []
        for axis in designspace.axes:
            axisItem = { attr : getattr(axis, attr) for attr in axesTitles }
            axesItems.append(axisItem)

        # create list UI with sources
        tab.axes = List(
            axesPosSize, axesItems,
                columnDescriptions=axesDescriptions,
                allowsMultipleSelection=True,
                enableDelete=False,
                allowsEmptySelection=False,
            )

        # --------------
        # update sources
        # --------------

        # get column descriptions
        sourcesDescriptions = [{'title': 'file name', 'minWidth': self._colFontName*2}]
        sourcesDescriptions += [{'title': axis.name, 'width': self._colValue} for axis in designspace.axes]

        # make list items
        self._sources = {}
        sourcesItems = []
        for source in designspace.sources:
            sourceFileName = os.path.splitext(os.path.split(source.path)[-1])[0]
            self._sources[sourceFileName] = source.path
            sourceItem = { 'file name' : sourceFileName }
            for axis in designspace.axes:
                sourceItem[axis.name] = source.location[axis.name]
            sourcesItems.append(sourceItem)

        # create list UI with sources
        tab.sources = List(
            sourcesPosSize, sourcesItems,
            columnDescriptions=sourcesDescriptions,
            allowsMultipleSelection=True,
            enableDelete=False)

    # fontinfo

    def updateFontinfoCallback(self, sender):

        if not self.selectedSources:
            return

        tab = self._tabs['fontinfo']

        # reset list
        fontinfoPosSize = tab.fontinfo.getPosSize()
        del tab.fontinfo

        # empty list
        if not self.selectedDesignspace:
            tab.fontinfo = List(fontinfoPosSize, [])
            return

        # collect fontinfo values into dict
        self._fontinfo = {}
        for source in self.selectedSources:
            sourceFileName = source['file name']
            sourcePath = self._sources[sourceFileName]
            f = OpenFont(sourcePath, showInterface=False)
            info = f.info.asDict()
            self._fontinfo[sourceFileName] = {}
            for a in self.selectedFontinfoAttrs:
                aLabel = self._fontinfoAttrs[a]
                aValue = info.get(a)
                self._fontinfo[sourceFileName][aLabel] = aValue if aValue is not None else '—'
            f.close()

        # make list items
        fontinfoItems = []
        for sourceFileName in self._fontinfo.keys():
            fontinfoItem = { 'file name' : sourceFileName }
            for aLabel in self._fontinfo[sourceFileName].keys():
                fontinfoItem[aLabel] = self._fontinfo[sourceFileName][aLabel]
            fontinfoItems.append(fontinfoItem)

        # create list UI with sources
        fontinfoDescriptions  = [{"title": 'file name', 'minWidth': self._colFontName}]
        fontinfoDescriptions += [{"title": self._fontinfoAttrs[a], 'width': self._colValue} for a in self.selectedFontinfoAttrs]
        tab.fontinfo = List(
            fontinfoPosSize, fontinfoItems,
            columnDescriptions=fontinfoDescriptions,
            allowsMultipleSelection=True,
            enableDelete=False)

    def visualizeFontinfoCallback(self, sender):
        print('visualize font infos')

    def exportFontinfoCallback(self, sender):
        pass

    def saveFontinfoCallback(self, sender):
        pass

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

    def selectMeasurementFileCallback(self, sender):

        tab = self._tabs['measurements']
        selection = sender.getSelection()
        measurementFiles = tab.measurementFiles.get()

        # delete current list
        posSize = tab.measurements.getPosSize()
        del tab.measurements

        # list of measurements is empty
        if not selection or not len(measurementFiles):
            tab.measurements = List(posSize, [])
            return

        # get measurements from selected measurement file
        measurementFileLabel = [F for i, F in enumerate(measurementFiles) if i in selection][0]
        measurementFilePath = self._measurementFiles[measurementFileLabel]

        with open(measurementFilePath, mode ='r') as file:
            csvFile = csv.DictReader(file)
            self._measurementFiles = {}
            items = []
            for i, lines in enumerate(csvFile):
                # # get column descriptions
                if i == 0:
                    titles = lines.keys()
                    descriptions = [{"title": T} for T in titles]

                # skip empty measurements
                if not any( list(lines.values())[2:] ):
                    continue

                # replace unicode hex values with unicode character
                if lines['Glyph 1']:
                    uniHex = lines['Glyph 1']
                    uniInt = int(uniHex.lstrip("x"), 16)
                    glyphName = UV2AGL.get(uniInt)
                    lines['Glyph 1'] = glyphName

                if lines['Glyph 2']:
                    uniHex = lines['Glyph 2']
                    uniInt = int(uniHex.lstrip("x"), 16)
                    glyphName = UV2AGL.get(uniInt)
                    lines['Glyph 2'] = glyphName


                # create list item
                items.append(lines)

        # create list UI with items
        tab.measurements = List(
            posSize, items,
            columnDescriptions=descriptions,
            allowsMultipleSelection=True,
            enableDelete=False)

    def updateMeasurementsCallback(self, sender):

        if not self.selectedMeasurements:
            return

        tab = self._tabs['measurements']

        # reset list
        valuesPosSize = tab.values.getPosSize()
        del tab.values

        # empty list
        if not self.selectedMeasurements:
            tab.values = List(valuesPosSize, [])
            return

        # collect measurements into dict
        self._measurements = {}
        for source in self.selectedSources:
            sourceFileName = source['file name']
            sourcePath = self._sources[sourceFileName]

            f = OpenFont(sourcePath, showInterface=False)

            self._measurements[sourceFileName] = {}
            for measurement in self.selectedMeasurements:
                measurementKey = measurement['Axis']
                self._measurements[sourceFileName][measurementKey] = 'XXX'

            f.close()

        # make list items
        valuesItems = []
        for sourceFileName in self._measurements.keys():
            valuesItem = { 'file name' : sourceFileName }
            for measurement in self._measurements[sourceFileName].keys():
                valuesItem[measurement] = self._measurements[sourceFileName][measurement]
            valuesItems.append(valuesItem)

        # create list UI with values
        valueDescriptions  = [{"title": 'file name', 'minWidth': self._colFontName}]
        valueDescriptions += [{"title": D['Axis'], 'width': self._colValue} for D in self.selectedMeasurements]
        tab.values = List(
            valuesPosSize, valuesItems,
            columnDescriptions=valueDescriptions,
            # allowsMultipleSelection=True,
            # enableDelete=False
            )

    def visualizeMeasurementsCallback(self, sender):
        print('visualize measurements')

    def exportMeasurementsCallback(self, sender):
        pass

    # glyph values
    
    def updateGlyphValuesCallback(self, sender):

        if not self.selectedGlyphAttrs:
            return

        self.selectedGlyphAttrs

        tab = self._tabs['glyphs']

        # reset list
        glyphValuesPosSize = tab.glyphValues.getPosSize()
        del tab.glyphValues

        # empty list
        if not self.selectedGlyphAttrs:
            tab.glyphValues = List(glyphValuesPosSize, [])
            return

        glyphAttr  = self.selectedGlyphAttrs[0]
        glyphNames = tab.glyphNames.get().split(' ')

        # collect glyph values into dict
        self._glyphValues = {}
        for source in self.selectedSources:
            sourceFileName = source['file name']
            sourcePath = self._sources[sourceFileName]
            f = OpenFont(sourcePath, showInterface=False)

            self._glyphValues[sourceFileName] = {}
            for glyphName in glyphNames:
                value = getattr(f[glyphName], glyphAttr) 
                self._glyphValues[sourceFileName][glyphName] = value

            f.close()

        # make list items
        glyphValueItems = []
        for sourceFileName in self._glyphValues.keys():
            glyphValueItem = { 'file name' : sourceFileName }
            for glyphName in self._glyphValues[sourceFileName].keys():
                glyphValueItem[glyphName] = self._glyphValues[sourceFileName][glyphName]
            glyphValueItems.append(glyphValueItem)

        # create list UI with sources
        glyphValuesDescriptions  = [{"title": 'file name', 'minWidth': self._colFontName}]
        glyphValuesDescriptions += [{"title": gName, 'width': self._colValue} for gName in glyphNames]
        tab.glyphValues = List(
            glyphValuesPosSize, glyphValueItems,
            columnDescriptions=glyphValuesDescriptions,
            allowsMultipleSelection=True,
            enableDelete=False)

    def visualizeGlyphValuesCallback(self, sender):
        pass

    def exportGlyphValuesCallback(self, sender):
        pass

    def saveGlyphValuesCallback(self, sender):
        pass



if __name__ == '__main__':

    OpenWindow(VarFontAssistant)


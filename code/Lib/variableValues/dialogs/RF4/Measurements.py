import os, json
import ezui
from mojo.UI import PutFile, GetFile
from mojo.roboFont import OpenFont, CurrentFont, CurrentGlyph
from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber, unregisterGlyphEditorSubscriber, registerRoboFontSubscriber, unregisterRoboFontSubscriber, registerSubscriberEvent, roboFontSubscriberEventRegistry
from mojo.events import postEvent
from variableValues.linkPoints import readMeasurements, getPointAtIndex, getIndexForPoint, getAnchorPoint
from variableValues.measurements import Measurement


'''
M E A S U R E M E N T S v4

RoboFont4 = EZUI + Subscriber + Merz

'''

DEBUG = False


class MeasurementsController(ezui.WindowController):

    title       = 'Measurements'
    key         = 'com.fontBureau.measurements4'
    buttonWidth = 75
    colWidth    = 55
    verbose     = False
    debug       = DEBUG

    fontMeasurements  = {}
    glyphMeasurements = {}

    font  = None
    glyph = None

    defaultFont = None

    def build(self):
        content = """
        = Tabs

        * Tab: font @fontTab
        > |---------------------------------------------------------------------------------------------------------|
        > | name | direction | glyph1 | point1 | glyph2 | point2 | units | permill | parent | p-scale | description |  @fontMeasurements
        > |------|-----------|--------|--------|--------|--------|-------|---------|--------|---------|-------------|
        > |      |           |        |        |        |        |       |         |        |         |             |
        > |---------------------------------------------------------------------------------------------------------|
        > (+-) @fontMeasurementsAddRemoveButton

        * Tab: glyph @glyphsTab
        > |-------------------------------------------------------------------------------------------|
        > | name | direction | point1 | point2 | units | permill | font | f-scale | default | d-scale |  @glyphMeasurements
        > |------|-----------|--------|--------|-------|---------|------|---------|---------|---------|
        > |      |           |        |        |       |         |      |         |         |         |
        > |-------------------------------------------------------------------------------------------|
        > > (+-)         @glyphMeasurementsAddRemoveButton
        > > [X] preview  @preview
        > > * ColorWell  @colorButton
        > > (flip)       @flipButton

        =============

        ( load… )     @loadButton
        ( save… )     @saveButton
        ( default… )  @defaultButton
        """

        descriptionData = dict(
            fontMeasurements=dict(
                columnDescriptions=[
                    dict(
                        identifier="name",
                        title="name",
                        width=self.colWidth,
                        editable=True
                    ),
                    dict(
                        identifier="direction",
                        title="direction",
                        width=self.colWidth,
                        editable=True,
                    ),
                    dict(
                        identifier="glyph1",
                        title="glyph 1",
                        width=self.colWidth,
                        editable=True
                    ),
                    dict(
                        identifier="point1",
                        title="point 1",
                        width=self.colWidth,
                        editable=True
                    ),
                    dict(
                        identifier="glyph2",
                        title="glyph 2",
                        width=self.colWidth,
                        editable=True
                    ),
                    dict(
                        identifier="point2",
                        title="point 2",
                        width=self.colWidth,
                        editable=True
                    ),
                    dict(
                        identifier="units",
                        title="units",
                        width=self.colWidth,
                        editable=False,
                        cellDescription=dict(
                            cellType='TextField',
                            valueType='integer',
                        ),
                    ),
                    dict(
                        identifier="permill",
                        title="permill",
                        width=self.colWidth,
                        editable=False,
                        cellDescription=dict(
                            cellType='TextField',
                            valueType='integer',
                        ),
                    ),
                    dict(
                        identifier="parent",
                        title="parent",
                        width=self.colWidth,
                        editable=True
                    ),
                    dict(
                        identifier="scale",
                        title="p-scale",
                        width=self.colWidth,
                        editable=False
                    ),
                    dict(
                        identifier="description",
                        title="description",
                        width=self.colWidth*6,
                        minWidth=self.colWidth*4,
                        maxWidth=self.colWidth*10,
                        editable=True
                    ),
                ],
                itemPrototype=dict(
                    name='_new',
                    direction=None,
                    glyph1=None,
                    point1=None,
                    glyph2=None,
                    point2=None,
                    units=None,
                    permill=None,
                    parent=None,
                    scale=None,
                    description=None,
                ),
            ),
            glyphMeasurements=dict(
                columnDescriptions=[
                    dict(
                        identifier="name",
                        title="name",
                        width=self.colWidth,
                        editable=True
                    ),
                    dict(
                        identifier="direction",
                        title="direction",
                        width=self.colWidth,
                        editable=True
                    ),
                    dict(
                        identifier="point1",
                        title="point 1",
                        width=self.colWidth,
                        editable=True
                    ),
                    dict(
                        identifier="point2",
                        title="point 2",
                        width=self.colWidth,
                        editable=True
                    ),
                    dict(
                        identifier="units",
                        title="units",
                        width=self.colWidth,
                        editable=False,
                        cellDescription=dict(
                            cellType='TextField',
                            valueType='integer',
                        ),
                    ),
                    dict(
                        identifier="permill",
                        title="permill",
                        width=self.colWidth,
                        editable=False,
                        cellDescription=dict(
                            cellType='TextField',
                            valueType='integer',
                        ),
                    ),
                    dict(
                        identifier="font",
                        title="font",
                        width=self.colWidth,
                        editable=False
                    ),
                    dict(
                        identifier="scale_f",
                        title="f-scale",
                        width=self.colWidth,
                        editable=False
                    ),
                    dict(
                        identifier="default",
                        title="default",
                        width=self.colWidth,
                        editable=False
                    ),
                    dict(
                        identifier="scale_d",
                        title="d-scale",
                        width=self.colWidth,
                        editable=False
                    ),
                ],
                itemPrototype=dict(
                    name='_new',
                    direction=None,
                    point1=None,
                    point2=None,
                    units=None,
                    permill=None,
                    default=None,
                    scale_d=None,
                    font=None,
                    scale_f=None,
                ),
            ),
            colorButton=dict(
                color=(1, 0.3, 0, 0.8),
                width=self.buttonWidth,
            ),
            flipButton=dict(
                width=self.buttonWidth,
            ),
            loadButton=dict(
                width=self.buttonWidth,
            ),
            saveButton=dict(
                width=self.buttonWidth,
            ),
            defaultButton=dict(
                width=self.buttonWidth,
            ),
        )

        self.w = ezui.EZPanel(
            title=self.title,
            content=content,
            descriptionData=descriptionData,
            controller=self,
            size=(800, 600),
            minSize=(600, 400),
        )
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        # self.w.getItem("fontMeasurements").getNSTableView().setRowHeight_(17)
        # self.w.getItem("glyphMeasurements").getNSTableView().setRowHeight_(17)
        self.w.open()

    def started(self):

        MeasurementsSubscriberRoboFont.controller = self
        registerRoboFontSubscriber(MeasurementsSubscriberRoboFont)

        MeasurementsSubscriberGlyphEditor.controller = self
        registerGlyphEditorSubscriber(MeasurementsSubscriberGlyphEditor)

        self.font  = CurrentFont()
        self.glyph = CurrentGlyph()

    def destroy(self):
        unregisterRoboFontSubscriber(MeasurementsSubscriberRoboFont)
        MeasurementsSubscriberRoboFont.controller = None

        unregisterGlyphEditorSubscriber(MeasurementsSubscriberGlyphEditor)
        MeasurementsSubscriberGlyphEditor.controller = None

    # ---------
    # callbacks
    # ---------

    def loadButtonCallback(self, sender):
        if self.debug:
            print('MeasurementsController.loadButtonCallback')

        jsonPath = GetFile(message='Select JSON file with measurements:')
        if jsonPath is None:
            return

        if self.verbose:
            print(f'loading data from {os.path.split(jsonPath)[-1]}... ', end='')

        measurements = readMeasurements(jsonPath)

        self.fontMeasurements  = measurements['font']
        self.glyphMeasurements = measurements['glyphs']

        self._loadFontMeasurements()
        self._loadGlyphMeasurements()

        if self.verbose:
            print('done.\n')

    def saveButtonCallback(self, sender):
        if self.debug:
            print('MeasurementsController.saveButtonCallback')

        fontItems = self.w.getItem("fontMeasurements").get()

        fontMeasurements = {
            i['name']: {
                'direction'   : i['direction'],
                'glyph 1'     : i['glyph1'],
                'point 1'     : i['point1'],
                'glyph 2'     : i['glyph2'],
                'point 2'     : i['point2'],
                'parent'      : i['parent'],
                'description' : i['description'],
            } for i in fontItems
        }

        glyphMeasurements = self.glyphMeasurements

        measurementsDict = {
            'font'   : fontMeasurements,
            'glyphs' : glyphMeasurements,
        }

        # get JSON file path
        jsonFileName = 'measurements.json'
        jsonPath = PutFile(message='Save measurements to JSON file:', fileName=jsonFileName)

        if jsonPath is None:
            if self.verbose:
                print('[cancelled]\n')
            return

        if os.path.exists(jsonPath):
            os.remove(jsonPath)

        if self.verbose:
            print(f'saving measurements to {jsonPath}...', end=' ')

        with open(jsonPath, 'w', encoding='utf-8') as f:
            json.dump(measurementsDict, f, indent=2)

        if self.verbose:
            print('done.\n')

    def defaultButtonCallback(self, sender):
        if self.debug:
            print('MeasurementsController.defaultButtonCallback')

        defaultPath = GetFile(message='Select default UFO source:')
        if defaultPath is None:
            return

        if self.verbose:
            print(f'loading default source from {os.path.split(defaultPath)[-1]}... ', end='')

        self.defaultFont = OpenFont(defaultPath, showInterface=False)

        if self.verbose:
            print('done.\n')

        postEvent(f"{self.key}.changed")

    # font

    def fontMeasurementsAddRemoveButtonAddCallback(self, sender):
        if self.debug:
            print('MeasurementsController.fontMeasurementsAddRemoveButtonAddCallback')
        table = self.w.getItem("fontMeasurements")
        item = table.makeItem()
        table.appendItems([item])
        postEvent(f"{self.key}.changed")

    def fontMeasurementsAddRemoveButtonRemoveCallback(self, sender):
        if self.debug:
            print('MeasurementsController.fontMeasurementsAddRemoveButtonRemoveCallback')
        table = self.w.getItem("fontMeasurements")
        table.removeSelectedItems()
        postEvent(f"{self.key}.changed")

    def fontMeasurementsEditCallback(self, sender):
        if self.debug:
            print('MeasurementsController.fontMeasurementsEditCallback')
        postEvent(f"{self.key}.changed")

    # glyph

    def glyphMeasurementsAddRemoveButtonAddCallback(self, sender):
        if self.debug:
            print('MeasurementsController.glyphMeasurementsAddRemoveButtonAddCallback')
        table = self.w.getItem("glyphMeasurements")
        item = table.makeItem()
        table.appendItems([item])

    def glyphMeasurementsAddRemoveButtonRemoveCallback(self, sender):
        if self.debug:
            print('MeasurementsController.glyphMeasurementsAddRemoveButtonRemoveCallback')
        table = self.w.getItem("glyphMeasurements")
        table.removeSelectedItems()
        postEvent(f"{self.key}.changed")

    def glyphMeasurementsSelectionCallback(self, sender):
        if self.debug:
            print('MeasurementsController.glyphMeasurementsSelectionCallback')
        postEvent(f"{self.key}.changed")

    def glyphMeasurementsEditCallback(self, sender):
        if self.debug:
            print('MeasurementsController.glyphMeasurementsEditCallback')
        items = self.w.getItem("glyphMeasurements").get()
        glyphMeasurements = {}
        for item in items:
            # auto set direction from name
            if not len(item['direction'].strip()):
                if item['name'][0] == 'X':
                    direction = 'x'
                    item['direction'] = 'x'
                if item['name'][0] == 'Y':
                    direction = 'y'
                    item['direction'] = 'y'
            # make glyph measurement dict
            meamsurementID = f"{item['point1']} {item['point2']}"
            glyphMeasurements[meamsurementID] = {
                'name'      : item['name'],
                'direction' : item['direction'],
            }
        self.glyphMeasurements[self.glyph.name] = glyphMeasurements
        postEvent(f"{self.key}.changed")

    def colorButtonCallback(self, sender):
        if self.debug:
            print('MeasurementsController.colorButtonCallback')
        postEvent(f"{self.key}.changed")

    def flipButtonCallback(self, sender):
        if self.debug:
            print('MeasurementsController.flipButtonCallback')
        postEvent(f"{self.key}.changed")

    # -------
    # methods
    # -------

    def _loadFontMeasurements(self):
        if self.debug:
            print('MeasurementsController._loadFontMeasurements')
        table = self.w.getItem("fontMeasurements")
        items = []
        for name, data in self.fontMeasurements.items():
            item = table.makeItem(
                name=name,
                direction=data.get('direction'),
                glyph1=data.get('glyph 1'),
                point1=data.get('point 1'),
                glyph2=data.get('glyph 2'),
                point2=data.get('point 2'),
                units=data.get('units'),
                permill=data.get('permill'),
                parent=data.get('parent'),
                scale=data.get('scale'),
                description=data.get('description'),
            )
            items.append(item)
        table.set(items)

        # self._updateFontMeasurements()
        # self._loadGlyphMeasurements()

        postEvent(f"{self.key}.changed")

    def _updateFontMeasurements(self):
        if self.debug:
            print('MeasurementsController._updateFontMeasurements')

        if self.font is None:
            return

        table = self.w.getItem("fontMeasurements")
        items = table.get()

        needReload = []
        for itemIndex, item in enumerate(items):
            try:
                pt1_index = int(item['point1'])
            except:
                pt1_index = item['point1']
            try:
                pt2_index = int(item['point2'])
            except:
                pt2_index = item['point2']

            M = Measurement(
                item['name'],
                item['direction'],
                item['glyph1'], pt1_index,
                item['glyph2'], pt2_index,
                item['parent']
            )
            distanceUnits = M.measure(self.font)
            item['units'] = distanceUnits

            if distanceUnits and self.font.info.unitsPerEm:
                distancePermill = round(distanceUnits * 1000 / self.font.info.unitsPerEm)
                item['permill'] = distancePermill

            needReload.append(itemIndex)

        for item in items:
            item['scale'] = None
            if item['parent']:
                distanceParent = None
                for i in items:
                    if i['name'] == item['parent']:
                        distanceParent = i['units']
                if distanceParent:
                    scaleParent = item['units'] / distanceParent
                    item['scale'] = f'{scaleParent:.2f}'

        table.reloadData(needReload)

    def _loadGlyphMeasurements(self):
        if self.debug:
            print('MeasurementsController._loadGlyphMeasurements')

        table = self.w.getItem("glyphMeasurements")
        items = []

        if not self.glyph:
            if self.debug:
                print('\tno current glyph!')
            table.set(items)
            return

        measurements = self.glyphMeasurements.get(self.glyph.name)

        if measurements is None:
            table.set(items)
            return

        for key in measurements.keys():
            parts = key.split()
            if len(parts) == 2:
                index1, index2 = parts
            else:
                continue
            item = table.makeItem(
                name=measurements[key].get('name'),
                direction=measurements[key].get('direction'),
                point1=index1,
                point2=index2,
                units=None,
                permill=None,
                font=measurements[key].get('parent'),
                scale_f=None,
                default=None,
                scale_d=None,
            )
            items.append(item)

        table.set(items)

        # self._updateGlyphMeasurements()
        postEvent(f"{self.key}.changed")

    def _updateGlyphMeasurements(self):
        if self.debug:
            print('MeasurementsController._updateGlyphMeasurements')

        table = self.w.getItem("glyphMeasurements")
        items = table.get()

        # get font-level values
        fontMeasurements = self.w.getItem("fontMeasurements").get()
        fontValues       = { i['name']: i['units'] for i in fontMeasurements }

        needReload = []
        for itemIndex, item in enumerate(items):

            # measure distance
            try:
                pt1_index = int(item['point1'])
            except:
                pt1_index = item['point1']
            try:
                pt2_index = int(item['point2'])
            except:
                pt2_index = item['point2']

            M = Measurement(
                item['name'],
                item['direction'],
                self.glyph.name, pt1_index,
                self.glyph.name, pt2_index,
                item['font']
            )
            distanceUnits = M.measure(self.font)

            # no measurement value
            if distanceUnits is None:
                item['units']   = None
                item['permill'] = None
                item['font']    = None
                item['scale_f'] = None

            else:
                item['units'] = distanceUnits

                # calculate permille value
                if distanceUnits and self.font.info.unitsPerEm:
                    item['permill'] = round(distanceUnits * 1000 / self.font.info.unitsPerEm)
                elif distanceUnits == 0:
                    item['permill'] = 0
                else:
                    item['permill'] = None

                # get font-level value
                name = item['name']
                if name in fontValues:
                    distanceFont = fontValues.get(name)
                    item['font'] = distanceFont
                    # calculate f-scale
                    if distanceUnits and distanceFont:
                        item['scale_f'] = f'{distanceUnits / distanceFont:.2f}'
                    else:
                        item['scale_f'] = None

            # get default value
            if self.defaultFont:
                distanceDefault = M.measure(self.defaultFont)
                item['default'] = distanceDefault
                # calculate d-scale
                if distanceUnits and distanceDefault:
                    item['scale_d'] = f'{distanceUnits / distanceDefault:.2f}'
                else:
                    item['scale_d'] = None

            needReload.append(itemIndex)

        table.reloadData(needReload)


class MeasurementsSubscriberRoboFont(Subscriber):

    controller = None
    debug = DEBUG

    def fontDocumentDidBecomeCurrent(self, info):
        if self.debug:
            print('MeasurementsSubscriberRoboFont.fontDocumentDidBecomeCurrent')
        self.controller.font = info['font']
        self.controller._updateFontMeasurements()
        self.controller._updateGlyphMeasurements()

    def fontDocumentDidOpen(self, info):
        if self.debug:
            print('MeasurementsSubscriberRoboFont.fontDocumentDidOpen')
        self.controller.font = info['font']
        self.controller._updateFontMeasurements()
        self.controller._updateGlyphMeasurements()

    def roboFontDidSwitchCurrentGlyph(self, info):
        if self.debug:
            print('MeasurementsSubscriberRoboFont.roboFontDidSwitchCurrentGlyph')
        self.controller.glyph = info["glyph"]
        self.controller._loadGlyphMeasurements()
        self.controller._updateGlyphMeasurements()

    def measurementsDidChange(self, info):
        if self.debug:
            print('MeasurementsSubscriberRoboFont.measurementsDidChange')
        self.controller._updateFontMeasurements()
        self.controller._updateGlyphMeasurements()


class MeasurementsSubscriberGlyphEditor(Subscriber):

    controller = None
    debug = DEBUG

    def build(self):
        if self.debug:
            print('MeasurementsSubscriberGlyphEditor.build')
        glyphEditor = self.getGlyphEditor()
        container = glyphEditor.extensionContainer(
            identifier=f"{self.controller.key}.foreground",
            location="foreground",
        )
        self.measurementsLayer = container.appendBaseSublayer()
        self._drawGlyphMeasurements()

    def destroy(self):
        if self.debug:
            print('MeasurementsSubscriberGlyphEditor.destroy')
        self.measurementsLayer.clearSublayers()

    def glyphEditorGlyphDidChange(self, info):
        if self.debug:
            print('MeasurementsSubscriberGlyphEditor.glyphEditorGlyphDidChange')
        self.controller._updateFontMeasurements()
        self.controller._updateGlyphMeasurements()
        self._drawGlyphMeasurements()

    def measurementsDidChange(self, info):
        if self.debug:
            print('MeasurementsSubscriberGlyphEditor.measurementsDidChange')
        self._drawGlyphMeasurements()

    def _drawGlyphMeasurements(self):
        if self.debug:
            print('MeasurementsSubscriberGlyphEditor._drawGlyphMeasurements')

        table = self.controller.w.getItem("glyphMeasurements")
        items = table.get()
        selectedItems = table.getSelectedItems()
        color = self.controller.w.getItem("colorButton").get()

        self.measurementsLayer.clearSublayers()

        with self.measurementsLayer.sublayerGroup():
            for item in items:
                pt1_index = item['point1']
                pt2_index = item['point2']

                try:
                    pt1 = getPointAtIndex(self.controller.glyph, int(pt1_index))
                except:
                    pt1 = getAnchorPoint(self.controller.font, pt1_index)

                try:
                    pt2 = getPointAtIndex(self.controller.glyph, int(pt2_index))
                except:
                    pt2 = getAnchorPoint(self.controller.font, pt2_index)

                if pt1 is None or pt2 is None:
                    continue

                if item in selectedItems:
                    direction = item['direction']
                    if direction == 'x':
                        P1 = pt1.x, pt1.y
                        P2 = pt2.x, pt1.y
                    elif direction == 'y':
                        P1 = pt2.x, pt1.y
                        P2 = pt2.x, pt2.y
                    else: # angled
                        P1 = pt1.x, pt1.y
                        P2 = pt2.x, pt2.y

                    R, G, B, a = color
                    self.measurementsLayer.appendLineSublayer(
                        startPoint=P1,
                        endPoint=P2,
                        strokeColor=(R, G, B, 0.3),
                        strokeWidth=100000,
                    )

                strokeDash = (3, 3) if item not in selectedItems else None
                strokeWidth = 2 if item in selectedItems else 1
                self.measurementsLayer.appendLineSublayer(
                    startPoint=(pt1.x, pt1.y),
                    endPoint=(pt2.x, pt2.y),
                    strokeColor=color,
                    strokeWidth=strokeWidth,
                    strokeDash=strokeDash,
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
                        pointSize=9,
                        padding=(4, 0),
                        cornerRadius=4,
                        fillColor=(1, 1, 1, 1),
                        horizontalAlignment='center',
                        verticalAlignment='center',
                    )


measurementsEventName = f"{MeasurementsController.key}.changed"

if measurementsEventName not in roboFontSubscriberEventRegistry:
    registerSubscriberEvent(
        subscriberEventName=measurementsEventName,
        methodName="measurementsDidChange",
        lowLevelEventNames=[measurementsEventName],
        documentation="Send when the measurements window changes its parameters.",
        dispatcher="roboFont",
        delay=0,
        debug=True
    )


if __name__ == '__main__':

    OpenWindow(MeasurementsController)



import os
import ezui
from mojo.UI import PutFile, GetFile
from mojo.roboFont import CurrentFont, CurrentGlyph
from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber, unregisterGlyphEditorSubscriber, registerRoboFontSubscriber, unregisterRoboFontSubscriber
from variableValues.linkPoints import readMeasurements
from variableValues.measurements import Measurement

'''
M E A S U R E M E N T S v3

RoboFont4 = EZUI + Subscriber + Merz

'''

class MeasurementsSubscriberRoboFont(Subscriber):

    def fontDocumentDidBecomeCurrent(self, info):
        self.controller.font = info['font']
        self.controller.updateFontMeasurements()

    def fontDocumentDidOpen(self, info):
        self.controller.font = info['font']
        self.controller.updateFontMeasurements()

    def roboFontDidSwitchCurrentGlyph(self, info):
        self.controller.glyph = info["glyph"]
        self.controller.loadGlyphMeasurements()


class MeasurementsSubscriberGlyphEditor(Subscriber):

    def roboFontDidSwitchCurrentGlyph(self, info):
        self.controller.glyph = info["glyph"]
        self.controller.loadGlyphMeasurements()

    def glyphEditorGlyphDidChange(self, info):
        self.controller.updateGlyphMeasurements()


class MeasurementsController(ezui.WindowController):

    title       = 'Measurements'
    key         = 'com.fontBureau.measurements'
    buttonWidth = 70
    colWidth    = 55
    verbose     = True

    fontMeasurements  = {}
    glyphMeasurements = {}

    font  = None
    glyph = None

    def build(self):
        content = """
        = Tabs

        * Tab: font @fontTab
        > |-------------------------------------------------------------------------------------------------------|
        > | name | direction | glyph1 | point1 | glyph2 | point2 | units | permill | parent | scale | description |  @fontMeasurements
        > |------|-----------|--------|--------|--------|--------|-------|---------|--------|-------|-------------|
        > |      |           |        |        |        |        |       |         |        |       |             |
        > |-------------------------------------------------------------------------------------------------------|
        > (+-) @fontMeasurementsAddRemoveButton

        * Tab: glyph @glyphsTab
        > |-----------------------------------------------------------------------|
        > | name | direction | point1 | point2 | units | permill | parent | scale |  @glyphMeasurements
        > |------|-----------|--------|--------|-------|---------|--------|-------|
        > |      |           |        |        |       |         |        |       |
        > |-----------------------------------------------------------------------|
        > > (+-)              @glyphMeasurementsAddRemoveButton
        > > [X] show preview  @preview
        > > * ColorWell       @colorButton
        > > (flip)            @flipButton

        =============

        ( load… ) @loadButton
        ( save… ) @saveButton
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
                        editable=True
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
                        editable=False
                    ),
                    dict(
                        identifier="permill",
                        title="permill",
                        width=self.colWidth,
                        editable=False
                    ),
                    dict(
                        identifier="parent",
                        title="parent",
                        width=self.colWidth,
                        editable=True
                    ),
                    dict(
                        identifier="scale",
                        title="scale",
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
                        editable=False
                    ),
                    dict(
                        identifier="permill",
                        title="permill",
                        width=self.colWidth,
                        editable=False
                    ),
                    dict(
                        identifier="parent",
                        title="parent",
                        width=self.colWidth,
                        editable=False
                    ),
                    dict(
                        identifier="scale",
                        title="scale",
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
                    parent=None,
                    scale=None,
                ),
            ),
            colorButton=dict(
                color=(1, 0, 0, 0.8),
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
        )

        self.w = ezui.EZPanel(
            title=self.title,
            content=content,
            descriptionData=descriptionData,
            controller=self,
            size=(800, 600),
            minSize=(600, 400),
        )

    def started(self):
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        # self.w.getItem("fontMeasurements").getNSTableView().setRowHeight_(17)
        # self.w.getItem("glyphMeasurements").getNSTableView().setRowHeight_(17)
        self.w.open()

        self.font  = CurrentFont()
        self.glyph = CurrentGlyph()

        MeasurementsSubscriberRoboFont.controller = self
        registerRoboFontSubscriber(MeasurementsSubscriberRoboFont)

        MeasurementsSubscriberGlyphEditor.controller = self
        registerGlyphEditorSubscriber(MeasurementsSubscriberGlyphEditor)

    def destroy(self):
        unregisterRoboFontSubscriber(MeasurementsSubscriberRoboFont)
        MeasurementsSubscriberRoboFont.controller = None

        unregisterGlyphEditorSubscriber(MeasurementsSubscriberGlyphEditor)
        MeasurementsSubscriberGlyphEditor.controller = None

    # ---------
    # callbacks
    # ---------

    def loadButtonCallback(self, sender):

        if self.verbose:
            print("loading measurement data from file...")

        jsonPath = GetFile(message='Select JSON file with measurements:')

        if self.verbose:
            print(f'\tloading data from {os.path.split(jsonPath)[-1]}...')

        measurements = readMeasurements(jsonPath)

        self.fontMeasurements  = measurements['font']
        self.glyphMeasurements = measurements['glyphs']

        self.loadFontMeasurements()

        if self.verbose:
            print('...done.\n')

    def saveButtonCallback(self, sender):
        print("save button was pushed.")

    # font

    def fontMeasurementsAddRemoveButtonAddCallback(self, sender):
        table = self.w.getItem("fontMeasurements")
        item = table.makeItem()
        table.appendItems([item])

    def fontMeasurementsAddRemoveButtonRemoveCallback(self, sender):
        table = self.w.getItem("fontMeasurements")
        table.removeSelectedItems()

    # glyph

    def glyphMeasurementsAddRemoveButtonAddCallback(self, sender):
        table = self.w.getItem("glyphMeasurements")
        item = table.makeItem()
        table.appendItems([item])

    def glyphMeasurementsAddRemoveButtonRemoveCallback(self, sender):
        table = self.w.getItem("glyphMeasurements")
        table.removeSelectedItems()

    def colorButtonCallback(self, sender):
        print("color button was pushed.")

    def flipButtonCallback(self, sender):
        print("flip button was pushed.")

    # -------
    # methods
    # -------

    def loadFontMeasurements(self):
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

        self.updateFontMeasurements()
        self.loadGlyphMeasurements()

    def updateFontMeasurements(self):

        if self.font is None:
            return

        table = self.w.getItem("fontMeasurements")
        items = table.get()

        # if self.verbose:
        #     print(f'getting font measurements for {self.font.info.familyName} {self.font.info.styleName}...')

        _items = []
        for i, item in enumerate(items):
            _item = item.copy()

            try:
                index1 = int(item['point1'])
            except:
                index1 = item['point1']
            try:
                index2 = int(item['point2'])
            except:
                index2 = item['point2']

            M = Measurement(
                item['name'], item['direction'],
                item['glyph1'], index1,
                item['glyph2'], index2,
                item['parent']
            )

            distance = M.measure(self.font)
            _item['units'] = distance

            if distance and self.font.info.unitsPerEm:
                distancePermill = round(distance * 1000 / self.font.info.unitsPerEm)
                _item['permill'] = distancePermill

            _items.append(_item)

        table.set(_items)

    def loadGlyphMeasurements(self):

        table = self.w.getItem("glyphMeasurements")
        items = []

        if not self.glyph:
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
                parent=measurements[key].get('parent'),
                scale=None,
            )
            items.append(item)

        table.set(items)

        self.updateGlyphMeasurements()

    def updateGlyphMeasurements(self):

        table = self.w.getItem("glyphMeasurements")

        if not self.glyph:
            table.set([])
            return

        items = table.get()

        # get font-level values to calculate scale
        fontItems        = self.w.getItem("fontMeasurements").get()
        fontValues       = { i['name']: i['units'] for i in fontItems }
        fontDescriptions = { i['name']: i['description'] for i in fontItems }

        _items = []

        # measure distances
        for i, item in enumerate(items):
            _item = item.copy()
            try:
                index1 = int(item['point1'])
            except:
                index1 = item['point1']
            try:
                index2 = int(item['point2'])
            except:
                index2 = item['point2']

            M = Measurement(
                item['name'], item['direction'],
                self.glyph.name, index1,
                self.glyph.name, index2,
                item['parent']
            )

            distance = M.measure(self.glyph.font)

            if distance is None:
                _item['units']   = None
                _item['permill'] = None
                _item['scale']   = None
            else:
                # table.setItemValue(i, 'units', distance)
                _item['units'] = distance

                # convert value to permill
                if distance and self.glyph.font.info.unitsPerEm:
                    distancePermill = round(distance * 1000 / self.glyph.font.info.unitsPerEm)
                    _item['permill'] = distancePermill

                # connect with font-level measurement
                name = item['name']
                if name in fontValues:
                    parent = fontValues.get(name)
                    if parent is not None:
                        parentValue = fontValues[name]
                        _item['parent'] = parentValue
                        try:
                            _item['scale'] = f'{distance/parentValue:.2f}'
                        except:
                            _item['scale'] = None
                    else:
                        _item['parent'] = None

            _items.append(_item)

        # refresh table with updated items
        table.set(_items)


# ----
# test
# ----

if __name__ == '__main__':

    OpenWindow(MeasurementsController)

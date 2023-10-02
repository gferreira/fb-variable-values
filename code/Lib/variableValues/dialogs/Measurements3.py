import ezui

'''
M E A S U R E M E N T S v3

RoboFont4 = EZUI + Subscriber + Merz

'''

class Measurements3(ezui.WindowController):
    
    title = 'Measurements'
    key   = 'com.fontBureau.measurements3'

    buttonWidth = 70
    colWidth = 55

    # -------
    # methods
    # -------

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
        > |-------------------------------------------------------------------------------------|
        > | name | direction | point1 | point2 | units | permill | parent | scale | description |  @glyphMeasurements
        > |------|-----------|--------|--------|-------|---------|--------|-------|-------------|
        > |      |           |        |        |       |         |        |       |             |
        > |-------------------------------------------------------------------------------------|
        > > (+-)        @glyphMeasurementsAddRemoveButton
        > > * ColorWell @colorButton 
        > > (flip)      @flipButton

        =============

        ( load ) @loadButton
        ( save ) @saveButton
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
                        minWidth=self.colWidth*4,
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
                    dict(
                        identifier="description",
                        title="description",
                        minWidth=self.colWidth*4,
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
                    description=None,
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
            )
        )

        self.w = ezui.EZPanel(
            title=self.title,
            content=content,
            descriptionData=descriptionData,
            controller=self,
            size=(800, 600),
            minSize=(800, 600),
        )

    def started(self):
        self.w.open()

    # ---------
    # callbacks
    # ---------

    def loadButtonCallback(self, sender):
        print("load button was pushed.")

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


# ----
# test
# ----

if __name__ == '__main__':

    OpenWindow(Measurements3)

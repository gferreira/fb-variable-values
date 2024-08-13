import ezui
from mojo.roboFont import OpenWindow
from fontTools.designspaceLib import DesignSpaceDocument


class DesignSpaceSelector_(ezui.WindowController):

    title  = 'DesignSpaceSelector'
    width  = 123*5 
    height = 640

    def build(self):

        content = """
        = Tabs
        * Tab: designspace   @designspaceTab
        >= VerticalStack
        >> designspaces
        >> |-files--------|
        >> | designspaces |  @designspaces
        >> |--------------|
        >> sources
        >> |--------------|
        >> | sources      |  @sources
        >> |--------------|
        >> ( open ) @openButton
        """

        descriptionData = dict(
            designspaces=dict(
                alternatingRowColors=True,
                height=100,
                itemType="dict",
                acceptedDropFileTypes=[".designspace"],
                allowsDropBetweenRows=True,
                allowsInternalDropReordering=True,
                allowsMultipleSelection=False,
                columnDescriptions=[
                    dict(
                        identifier="path",
                        title="path",
                        cellClassArguments=dict(
                            showFullPath=True
                        )
                    ),
                    dict(
                        identifier="lines",
                        title="line count"
                    )
                ]
            ),
            sources=dict(
                alternatingRowColors=True,
                height='auto',
                columnDescriptions=[
                    dict(
                        identifier="name",
                        title="name",
                        editable=False,
                    ),
                ],
            ),
        )

        self.w = ezui.EZWindow(
            title=self.title,
            content=content,
            descriptionData=descriptionData,
            controller=self,
            size=(self.width, self.height),
            minSize=(self.width, 360),
        )

    def started(self):
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        # self.w.getItem("designspaces").getNSTableView().setRowHeight_(17)
        # self.w.getItem("sources").getNSTableView().setRowHeight_(17)
        self.w.open()

    def designspacesCreateItemsForDroppedPathsCallback(self, sender, paths):
        items = []
        for path in paths:
            item = dict(path=path, lines=None)
            items.append(item)

        return items

    def designspacesSelectionCallback(self, sender):

        designspacesTable = self.w.getItem("designspaces")
        designspacesSelection = designspacesTable.getSelectedItems()

        if not designspacesSelection:
            return

        selectedDesignspace = designspacesSelection[0]
        designspacePath = selectedDesignspace['path']

        D = DesignSpaceDocument()
        D.read(designspacePath)

        sourcesTable = self.w.getItem("sources")

        sourcesItems = []
        for i, source in enumerate(D.sources):
            sourcesItems.append(dict(name=source.filename))
        
        sourcesTable.set(sourcesItems)


# ----
# test
# ----

if __name__ == '__main__':

    OpenWindow(DesignSpaceSelector_)


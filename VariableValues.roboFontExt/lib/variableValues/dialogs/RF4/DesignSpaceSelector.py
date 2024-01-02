import ezui
from mojo.roboFont import OpenWindow


class DesignSpaceSelector(ezui.WindowController):
    
    title = 'DesignSpaceSelector'
    key          = 'com.fontBureau.measurements'
    
    def build(self):
        content = """
        = Tabs
        
        * Tab: designspace @designspaceTab
        > |--------------|
        > | designspaces |  @designspaces
        > |--------------|
        
        > |--------------|
        > | axes         |  @axes
        > |--------------|
        
        > |--------------|
        > | sources      |  @sources
        > |--------------|

        =============

        ( load ) @loadButton
        ( save ) @saveButton
        """

        descriptionData = dict()

        self.w = ezui.EZWindow(
            title=self.title,
            content=content,
            descriptionData=descriptionData,
            controller=self,
            size=(800, 600),
            minSize=(600, 400),
        )


# ----
# test
# ----

if __name__ == '__main__':

    OpenWindow(DesignSpaceSelector)


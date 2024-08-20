import ezui


class GlyphValidator_EZUI(ezui.WindowController):

    title = 'validator'
    width = 123 

    content = """
    ( get default… )   @getDefaultButton
    ( reload ↺ )       @reloadButton

    checks
    [X] width          @widthCheck
    [ ] left           @leftCheck
    [ ] right          @rightCheck
    [X] points         @pointsCheck
    [X] components     @componentsCheck
    [X] anchors        @anchorsCheck
    [X] unicodes       @unicodesCheck

    display
    [X] font overview  @displayFontOverview
    [X] glyph window   @displayGlyphWindow

    ( mark glyphs )    @markGlyphsButton
    """

    descriptionData = dict(
        content=dict(
            sizeStyle="small",
        ),
        getDefaultButton=dict(
            width='fill',
        ),
        reloadButton=dict(
            width='fill',
        ),
        markGlyphsButton=dict(
            width='fill',
        ),
    )

    def build(self):

        self.w = ezui.EZPanel(
            title=self.title,
            content=self.content,
            descriptionData=self.descriptionData,
            controller=self,
            size=(self.width, 'auto'),
            minSize=(self.width, 360),
        )

    def started(self):
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()



if __name__ == '__main__':

    OpenWindow(GlyphValidator_EZUI)

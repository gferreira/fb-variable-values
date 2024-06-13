from vanilla import *
from mojo.UI import AccordionView


class VarProjectControllerWindow:

    title      = 'batch project'
    width      = 123*2
    height     = 640
    padding    = 10
    lineHeight = 22
    verbose    = True

    _designspaces = {}
    _sources = {}

    _fontActions = [
        'set names from measurements',
        'set validation mark colors',
        'copy default glyph order',
        'copy default features',
        'copy default unicodes',
    ]

    def __init__(self):
        self.w = FloatingWindow(
                (self.width, self.height),
                title=self.title,
                minSize=(self.width*0.9, self.width*0.5))

        self.designspaces = Group((0, 0, -0, -0))
        x = y = p = self.padding
        self.designspaces.list = List(
                (x, y, -p, -p),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                # editCallback=self.selectDesignspaceCallback,
                # selectionCallback=self.selectDesignspaceCallback,
                # enableDelete=True,
                # otherApplicationDropSettings=dict(
                #     type=NSFilenamesPboardType,
                #     operation=NSDragOperationCopy,
                #     callback=self.dropCallback),
                )

        self.sources = Group((0, 0, -0, -0))

        x = y = p = self.padding
        self.sources.list = List((x, y, -p, -self.lineHeight-p*2), [])
        
        y = -self.lineHeight - p
        self.sources.validate = Button(
                (x, y, -p, self.lineHeight),
                'validate locations',
                sizeStyle='small',
                # callback=self.importButtonCallback
            )
        
        y = -(p + self.lineHeight)

        # font actions

        self.fontActions = Group((0, 0, -0, -0))

        x = y = p = self.padding

        self.fontActions.list = List(
                (x, y, -p, -self.lineHeight-p*2),
                self._fontActions)

        y = -self.lineHeight - p
        self.fontActions.apply = Button(
                (x, y, -p, self.lineHeight),
                'apply actions to sources',
                sizeStyle='small',
                # callback=self.importButtonCallback
            )

        # glyph actions

        self.glyphsCopy = Group((0, 0, -0, -0))

        x = y = p = self.padding
        textBoxHeight = -(self.lineHeight * 1) - (p * 2)
        self.glyphsCopy.names = EditText(
                (x, y, -p, textBoxHeight),
                'a b c A B C one two three')

        y = -(p + self.lineHeight)
        self.glyphsCopy.apply = Button(
                (x, y, -p, self.lineHeight),
                'copy default glyphs to sources',
                sizeStyle='small',
                # callback=self.importButtonCallback
            )

        self.glyphsBuild = Group((0, 0, -0, -0))

        x = y = p = self.padding
        textBoxHeight = -(self.lineHeight * 1) - (p * 2)
        self.glyphsBuild.names = EditText(
                (x, y, -p, textBoxHeight),
                'a b c A B C one two three')

        y = -(p + self.lineHeight)
        self.glyphsBuild.apply = Button(
                (x, y, -p, self.lineHeight),
                'build glyphs in sources',
                sizeStyle='small',
                # callback=self.importButtonCallback
            )

        self.glyphsRemove = Group((0, 0, -0, -0))

        x = y = p = self.padding
        textBoxHeight = -(self.lineHeight * 1) - (p * 2)
        self.glyphsRemove.names = EditText(
                (x, y, -p, textBoxHeight),
                'a b c A B C one two three')

        y = -(p + self.lineHeight)
        self.glyphsRemove.apply = Button(
                (x, y, -p, self.lineHeight),
                'remove glyphs from sources',
                sizeStyle='small',
                # callback=self.importButtonCallback
            )
            
        # build accordion

        descriptions = [
           dict(label="designspaces",
                view=self.designspaces,
                size=self.lineHeight*5,
                minSize=self.lineHeight*3,
                collapsed=False,
                canResize=True),
           dict(label="sources",
                view=self.sources,
                size=self.lineHeight*8,
                minSize=self.lineHeight*6,
                collapsed=False,
                canResize=True),
           dict(label="font actions",
                view=self.fontActions,
                size=self.lineHeight*7,
                minSize=self.lineHeight*12,
                collapsed=True,
                canResize=False),
           dict(label="copy glyphs",
                view=self.glyphsCopy,
                size=self.lineHeight*6,
                minSize=self.lineHeight*4,
                collapsed=True,
                canResize=True),
           dict(label="build glyphs",
                view=self.glyphsBuild,
                size=self.lineHeight*6,
                minSize=self.lineHeight*4,
                collapsed=True,
                canResize=True),
           dict(label="remove glyphs",
                view=self.glyphsRemove,
                size=self.lineHeight*6,
                minSize=self.lineHeight*4,
                collapsed=True,
                canResize=True),
        ]
        self.w.accordionView = AccordionView((0, 0, -0, -0), descriptions)

        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)

        self.w.open()


VarProjectControllerWindow()

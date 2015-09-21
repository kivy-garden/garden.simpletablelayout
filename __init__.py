"""
    Simple Table Layout
    ===================
    Simple Table like Layout that understands rowspan and colspan properties of
    children (like HTML tables).

    Usage (kv):

    Example 1:

    SimpleTableLayout:
        rows: 2
        cols: 2

        Button:
            text: "C1"
            colspan: 2
        Button:
            text: "C2"
        Button:
            text: "C3"

    creates:
    ###########
    #    C1   #
    ###########
    # C2 # C3 #
    ###########

    Example 2:
    
    SimpleTableLayout:
        rows: 2
        cols: 2

        Button:
            text: "C1"
            rowspan: 2
        Button:
            text: "C2"
        Button:
            text: "C3"

    creates:
    ###########
    #    # C2 #
    # C1 ######
    #    # C3 #
    ###########

    Lastly, SimpleTableLayout.cell(row, col) returns widget at that position in
    the grid.
    
    author: Jeyson Molina <jeyson.mco@gmail.com>
"""

__all__ = ('SimpleTableLayout', )
__version__ = '0.1'

from kivy.lang import Builder
from kivy.uix.layout import Layout
from kivy.properties import BoundedNumericProperty, ListProperty


class SimpleTableLayout(Layout):

    """Class for creating a TableLayout widget."""
    cols = BoundedNumericProperty(None, min=0, allownone=True)
    rows = BoundedNumericProperty(None, min=0, allownone=True)
    _grid = ListProperty([])

    def __init__(self, *args, **kwargs):
        super(SimpleTableLayout, self).__init__(*args, **kwargs)
        self.bind(
            children=self._trigger_layout,
            size=self._trigger_layout,
            pos=self._trigger_layout)

    def add_widget(self, widget):
        if not hasattr(widget, 'colspan'):
            widget.colspan = 1  # TODO warning, not defined as property.

        if not hasattr(widget, 'rowspan'):
            widget.rowspan = 1  # TODO warning, not defined as property.

        return super(SimpleTableLayout, self).add_widget(widget)

    def on_children(self, o, v):
        children_cells = sum([c.rowspan * c.colspan for c in self.children])
        total_cells = self.cols * \
            self.rows if self.cols is not None and self.rows is not None else None

        if total_cells and children_cells > total_cells:
            raise NotEnoughCellsException(
                """Available cells: %s. Requested cells: %s.
                Increase cols and/or rows""" % (total_cells, children_cells))

    def do_layout(self, *largs):
        if not self.children:
            return

        cols_width = self.width / self.cols
        rows_height = self.height / self.rows

        grid = [[0 for x in range(self.cols)] for y in range(self.rows)]
        # A grid with size cols x rows.
        # each position represents a cell. zero means the cell is available,
        

        for i, c in enumerate(self.children[::-1]):
            c.size = cols_width * c.colspan, rows_height * c.rowspan
            # Find next available cell
            cur_row, cur_col = self._next_cell(grid)
            if cur_row is None or cur_col is None:  # TODO raise exception?
                break
            # fill cell or cells in grid according to rowspan, colspan
            for ry in range(c.rowspan):
                # if rowspan > 1 we need to put the widget at the lowest row
                last_row = cur_row + ry
                for rx in range(c.colspan):
                    grid[cur_row + ry][cur_col + rx] = c
            c.pos = self.x + cols_width * cur_col,  self.y + \
                self.height - rows_height - rows_height * last_row

        self._grid = grid

    def cell(self, row, col):
        """Returns widget at pos (row, col) in the grid"""
        return self._grid[row - 1][col - 1]

    def _next_cell(self, grid):
        # TODO optimize
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                if grid[y][x] == 0:
                    return y, x
        return None, None


class NotEnoughCellsException(Exception):
    pass

if __name__ == '__main__':
    from kivy.app import App
    from kivy.factory import Factory
    from kivy.config import Config


    class TestSimpleTableApp(App):

        def build(self):
            return Builder.load_string('''
SimpleTableLayout:
    pos: root.pos
    size: root.size
    cols: 5
    rows: 2

    Button:
        text: "(row: 1, col: 1)"

    Button:
        text: "(row: 1, col: 2) \\n colspan: 2  \\n rowspan: 2"
        colspan: 2
        rowspan: 2

    Button:
        text: "(row: 1, col: 4) \\n colspan: 2"
        colspan: 2
    Button:
        text: "(row: 2, col: 1)"
    Button:
        text: "(row: 2, col: 4)"
    Button:
        text: "(row: 2, col: 5)"

                    ''')
    Config.set('modules', 'monitor', '')
    TestSimpleTableApp().run()

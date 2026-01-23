import prismatui as pr
import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class TUIMolPrisma(pr.Terminal):
    IDX_PAIR_HELP = 1
    IDX_PAIR_META = 2
    IDX_PAIR_DATA = 3
    COLOR_GRAY = 8
    NLINES_FAST_SCROLL = 10

    # --------------------------------------------------------------------------
    def __init__(self, mol_data: mp.MolData):
        super().__init__()
        self._mol = mol_data

    # --------------------------------------------------------------------------
    def on_start(self):
        pr.init_pair(self.IDX_PAIR_HELP, pr.COLOR_BLACK, pr.COLOR_CYAN)
        pr.init_pair(self.IDX_PAIR_META, pr.COLOR_WHITE, self.COLOR_GRAY)
        pr.init_pair(self.IDX_PAIR_DATA, pr.COLOR_BLACK, pr.COLOR_YELLOW)

        self.pair_meta = pr.get_color_pair(self.IDX_PAIR_META)
        self.pair_data = pr.get_color_pair(self.IDX_PAIR_DATA)

    # --------------------------------------------------------------------------
    def on_update(self):
        match self.key:
            case pr.KEY_UP:   self._scroll_up(1)
            case pr.KEY_DOWN: self._scroll_down(1)
            case pr.KEY_PPAGE: self._scroll_up(self.NLINES_FAST_SCROLL)
            case pr.KEY_NPAGE: self._scroll_down(self.NLINES_FAST_SCROLL)

        hdisplay = self.h - 1
        self.NLINES_FAST_SCROLL = hdisplay // 2 # dinamically adjust fast scroll based on terminal height

        lines = [line.text for line in self._mol.iter_lines(hdisplay)]
        attrs = [
            [self.pair_data if line.kind == mp.MolKind.DATA else self.pair_meta] * len(line.text)
            for line in self._mol.iter_lines(hdisplay)
        ]

        self.root.draw_matrix(0, 0, lines, attrs)

        self.draw_text('b', 'l', "Press F1 to exit", pr.get_color_pair(self.IDX_PAIR_HELP))

    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.key == pr.KEY_F1

    # --------------------------------------------------------------------------
    def _scroll_up(self, nlines: int):
        self._mol.pos = max(0, self._mol.pos - nlines)

    # --------------------------------------------------------------------------
    def _scroll_down(self, nlines: int):
        self._mol.pos = min(len(self._mol._all_lines) - 1, self._mol.pos + nlines)


# //////////////////////////////////////////////////////////////////////////////

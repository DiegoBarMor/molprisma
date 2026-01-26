import prismatui as pr
import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class TUIMolPrisma(pr.Terminal):
    IDX_PAIR_HELP = 1
    IDX_PAIR_META = 2
    IDX_PAIR_DATA = 3
    NLINES_FAST_SCROLL = 10

    COLOR_GRAY = 8
    KEY_M = ord('m')

    # --------------------------------------------------------------------------
    def __init__(self, mol_data: mp.MolData):
        super().__init__()
        self._mol = mol_data
        self._show_meta = True

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
            case pr.KEY_UP:    self._scroll_up(1)
            case pr.KEY_DOWN:  self._scroll_down(1)
            case pr.KEY_PPAGE: self._scroll_up(self.NLINES_FAST_SCROLL)
            case pr.KEY_NPAGE: self._scroll_down(self.NLINES_FAST_SCROLL)
            case self.KEY_M:   self._toggle_meta()

        hdisplay = self.h - 1
        self.NLINES_FAST_SCROLL = hdisplay // 2 # dinamically adjust fast scroll based on terminal height

        lines = tuple(self._mol.iter_lines(hdisplay, self._get_filter_key()))
        chars = [line.text for line in lines]
        attrs = [self._get_attr_array(line) for line in lines]

        self.root.draw_matrix(0, 0, chars, attrs)

        self.draw_text('b', 'l', "Press F1 to exit", pr.get_color_pair(self.IDX_PAIR_HELP))

    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.key == pr.KEY_F1

    # --------------------------------------------------------------------------
    def _scroll_up(self, nlines: int):
        self._mol.pos = max(0, self._mol.pos - nlines)

    # --------------------------------------------------------------------------
    def _scroll_down(self, nlines: int):
        nlines_available = self._mol.count_lines(self._get_filter_key())
        self._mol.pos = min(self._mol.pos + nlines, nlines_available - 1)

    # --------------------------------------------------------------------------
    def _toggle_meta(self):
        self._show_meta = not self._show_meta
        if self._show_meta:
            self._mol.pos = 0
            return

        for idx, line in enumerate(self._mol.iter_lines()):
            if line.kind != mp.MolKind.DATA: continue
            self._mol.pos = idx
            return

    # --------------------------------------------------------------------------
    def _get_filter_key(self) -> callable:
        if self._show_meta:
            return lambda _: True
        return lambda line: line.kind == mp.MolKind.DATA

    # --------------------------------------------------------------------------
    def _get_attr_array(self, line: mp.MolLine) -> list[int]:
        if line.kind == mp.MolKind.DATA:
            return [self.pair_data] * len(line.text)
        return [self.pair_meta] * len(line.text)


# //////////////////////////////////////////////////////////////////////////////

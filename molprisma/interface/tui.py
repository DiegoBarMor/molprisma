import prismatui as pr
import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class TUIMolPrisma(pr.Terminal):
    COLOR_GRAY = 8
    NLINES_FAST_SCROLL = 10
    KEY_CTRL_HOME = 540 # [TODO] test this
    KEY_CTRL_END = 535

    # --------------------------------------------------------------------------
    def __init__(self, mol_data: mp.MolData):
        super().__init__()
        self._mol = mol_data
        self._show_atom = True
        self._show_hete = True
        self._show_meta = True

        self._filter_key: callable[mp.MolLine] = lambda _: True


    # --------------------------------------------------------------------------
    def on_start(self):
        self.pair_none   = pr.init_pair(1, pr.COLOR_WHITE, pr.COLOR_RED)
        self.pair_meta   = pr.init_pair(2, pr.COLOR_WHITE, self.COLOR_GRAY)
        self.pair_atom   = pr.init_pair(3, pr.COLOR_BLACK, pr.COLOR_YELLOW)
        self.pair_hete   = pr.init_pair(4, pr.COLOR_BLACK, pr.COLOR_GREEN)
        self.pair_help   = pr.init_pair(5, pr.COLOR_BLACK, pr.COLOR_CYAN)
        self.pair_help_0 = pr.init_pair(6, pr.COLOR_WHITE, pr.COLOR_RED)
        self.pair_help_1 = pr.init_pair(7, pr.COLOR_BLACK, pr.COLOR_GREEN)


    # --------------------------------------------------------------------------
    def on_update(self):
        match self.key:
            case pr.KEY_UP:      self._scroll_up(1)
            case pr.KEY_DOWN:    self._scroll_down(1)
            case pr.KEY_PPAGE:   self._scroll_up(self.NLINES_FAST_SCROLL)
            case pr.KEY_NPAGE:   self._scroll_down(self.NLINES_FAST_SCROLL)
            case pr.KEY_H_LOWER: self._help_screen()
            case pr.KEY_H_UPPER: self._help_screen()
            case pr.KEY_A_LOWER: self._toggle_all()
            case pr.KEY_A_UPPER: self._toggle_all()
            case pr.KEY_Z_LOWER: self._toggle_atom()
            case pr.KEY_Z_UPPER: self._toggle_atom()
            case pr.KEY_X_LOWER: self._toggle_hete()
            case pr.KEY_X_UPPER: self._toggle_hete()
            case pr.KEY_C_LOWER: self._toggle_meta()
            case pr.KEY_C_UPPER: self._toggle_meta()
            case self.KEY_CTRL_HOME: self._scroll_up(float("inf"))
            case self.KEY_CTRL_END:  self._scroll_down(float("inf"))

        hdisplay = self.h - 2
        self.NLINES_FAST_SCROLL = hdisplay // 2 # dinamically adjust fast scroll based on terminal height

        lines = tuple(self._mol.iter_lines(self._filter_key, hdisplay))
        chars = [line.text for line in lines]
        attrs = [self._get_attr_array(line) for line in lines]

        self.draw_matrix(0, 0, chars, attrs)
        self._draw_guides(w = len(self._mol._lines[0].text))


    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.key == pr.KEY_Q_LOWER or self.key == pr.KEY_Q_UPPER


    # --------------------------------------------------------------------------
    def _draw_guides(self, w: int):
        def choose_pair(show: bool) -> int:
            return self.pair_help_1 if show else self.pair_help_0

        self.draw_text(-2, 'l', '-'*w, pr.A_BOLD)
        show_all = self._show_atom and self._show_hete and self._show_meta

        x = 0
        x += self.draw_text('b', x, "q: quit", self.pair_help) + 1
        # x += self.draw_text('b', x, "h: help", self.pair_help) + 1
        x += self.draw_text('b', x, "a: all",      choose_pair(show_all)) + 1
        x += self.draw_text('b', x, "z: atoms",    choose_pair(self._show_atom)) + 1
        x += self.draw_text('b', x, "x: hetatms",  choose_pair(self._show_hete)) + 1
        x += self.draw_text('b', x, "c: metadata", choose_pair(self._show_meta)) + 1
        self.draw_text('b', x, '.'*(w - x), pr.A_DIM)


    # --------------------------------------------------------------------------
    def _scroll_up(self, nlines: int):
        self._mol.pos = max(0, self._mol.pos - nlines)


    # --------------------------------------------------------------------------
    def _scroll_down(self, nlines: int):
        nlines_available = self._mol.count_lines(self._filter_key) - 1 # account for NONE terminator line
        self._mol.pos = min(self._mol.pos + nlines, nlines_available - 1)


    # --------------------------------------------------------------------------
    def _help_screen(self):
        ... # [TODO]


    # --------------------------------------------------------------------------
    def _toggle_all(self):
        self._show_meta = not self._show_meta
        self._show_atom = not self._show_atom
        self._show_hete = not self._show_hete
        self._update_filter_key()
        self._update_pos()


    # --------------------------------------------------------------------------
    def _toggle_meta(self):
        self._show_meta = not self._show_meta
        self._update_filter_key()
        self._update_pos()


    # --------------------------------------------------------------------------
    def _toggle_atom(self):
        self._show_atom = not self._show_atom
        self._update_filter_key()
        self._update_pos()


    # --------------------------------------------------------------------------
    def _toggle_hete(self):
        self._show_hete = not self._show_hete
        self._update_filter_key()
        self._update_pos()


    # --------------------------------------------------------------------------
    def _get_attr_array(self, line: mp.MolLine) -> list[int]:
        match line.kind:
            case mp.MolKind.NONE: pair = self.pair_none
            case mp.MolKind.META: pair = self.pair_meta
            case mp.MolKind.ATOM: pair = self.pair_atom
            case mp.MolKind.HETE: pair = self.pair_hete
            case _: raise ValueError("Unknown MolKind")

        return [pair for _ in line.text]


    # --------------------------------------------------------------------------
    def _update_filter_key(self):
        def filterkey(line: mp.MolLine) -> bool:
            match line.kind:
                case mp.MolKind.NONE: return True
                case mp.MolKind.META: return self._show_meta
                case mp.MolKind.ATOM: return self._show_atom
                case mp.MolKind.HETE: return self._show_hete
                case _: raise ValueError("Unknown MolKind")

        self._filter_key = filterkey


    # --------------------------------------------------------------------------
    def _update_pos(self):
        self._mol.pos = 0
        for idx, line in enumerate(self._mol.iter_lines(self._filter_key)):
            if not self._filter_key(line): continue
            self._mol.pos = idx
            return


# //////////////////////////////////////////////////////////////////////////////

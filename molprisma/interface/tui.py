import prismatui as pr
import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class TUIMolPrisma(pr.Terminal):
    IDX_PAIR_NONE = 1
    IDX_PAIR_META = 2
    IDX_PAIR_ATOM = 3
    IDX_PAIR_HETA = 4
    IDX_PAIR_HELP = 5
    IDX_PAIR_HELP_0 = 6
    IDX_PAIR_HELP_1 = 7
    NLINES_FAST_SCROLL = 10

    COLOR_GRAY = 8
    KEY_A = ord('a')
    KEY_C = ord('c')
    KEY_H = ord('h')
    KEY_Q = ord('q')
    KEY_X = ord('x')
    KEY_Z = ord('z')
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
        pr.init_pair(self.IDX_PAIR_NONE,   pr.COLOR_WHITE, pr.COLOR_RED)
        pr.init_pair(self.IDX_PAIR_META,   pr.COLOR_WHITE, self.COLOR_GRAY)
        pr.init_pair(self.IDX_PAIR_ATOM,   pr.COLOR_BLACK, pr.COLOR_YELLOW)
        pr.init_pair(self.IDX_PAIR_HETA,   pr.COLOR_BLACK, pr.COLOR_GREEN)
        pr.init_pair(self.IDX_PAIR_HELP  , pr.COLOR_BLACK, pr.COLOR_CYAN)
        pr.init_pair(self.IDX_PAIR_HELP_0, pr.COLOR_WHITE, pr.COLOR_RED)
        pr.init_pair(self.IDX_PAIR_HELP_1, pr.COLOR_WHITE, pr.COLOR_GREEN)

        self.pair_none   = pr.get_color_pair(self.IDX_PAIR_NONE)
        self.pair_meta   = pr.get_color_pair(self.IDX_PAIR_META)
        self.pair_atom   = pr.get_color_pair(self.IDX_PAIR_ATOM)
        self.pair_hete   = pr.get_color_pair(self.IDX_PAIR_HETA)
        self.pair_help   = pr.get_color_pair(self.IDX_PAIR_HELP)
        self.pair_help_0 = pr.get_color_pair(self.IDX_PAIR_HELP_0)
        self.pair_help_1 = pr.get_color_pair(self.IDX_PAIR_HELP_1)


    # --------------------------------------------------------------------------
    def on_update(self):
        match self.key:
            case pr.KEY_UP:    self._scroll_up(1)
            case pr.KEY_DOWN:  self._scroll_down(1)
            case pr.KEY_PPAGE: self._scroll_up(self.NLINES_FAST_SCROLL)
            case pr.KEY_NPAGE: self._scroll_down(self.NLINES_FAST_SCROLL)
            case self.KEY_H:         self._show_help()
            case self.KEY_A:         self._toggle_all()
            case self.KEY_Z:         self._toggle_atom()
            case self.KEY_X:         self._toggle_hete()
            case self.KEY_C:         self._toggle_meta()
            case self.KEY_CTRL_HOME: self._scroll_up(float("inf"))
            case self.KEY_CTRL_END:  self._scroll_down(float("inf"))

        hdisplay = self.h - 2
        self.NLINES_FAST_SCROLL = hdisplay // 2 # dinamically adjust fast scroll based on terminal height

        lines = tuple(self._mol.iter_lines(self._filter_key, hdisplay))
        chars = [line.text for line in lines]
        attrs = [self._get_attr_array(line) for line in lines]

        self.root.draw_matrix(0, 0, chars, attrs)
        self._draw_guides()


    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.key == self.KEY_Q


    # --------------------------------------------------------------------------
    def _draw_guides(self):
        x = 0
        self.draw_text(-2, 0, '-'*self.w, pr.A_BOLD)
        self.draw_text('b', x, "q: quit", self.pair_help)
        ...


    # --------------------------------------------------------------------------
    def _scroll_up(self, nlines: int):
        self._mol.pos = max(0, self._mol.pos - nlines)


    # --------------------------------------------------------------------------
    def _scroll_down(self, nlines: int):
        nlines_available = self._mol.count_lines(self._filter_key) - 1 # account for NONE terminator line
        self._mol.pos = min(self._mol.pos + nlines, nlines_available - 1)


    # --------------------------------------------------------------------------
    def _show_help(self):
        ...


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

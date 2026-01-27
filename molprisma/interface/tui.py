import prismatui as pr
import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class TUIMolPrisma(pr.Terminal):
    NLINES_FAST_SCROLL = 10
    PDB_WIDTH = 80
    H_GUIDES = 2

    KEY_CTRL_HOME = 540 # [TODO] test this
    KEY_CTRL_END = 535
    COLOR_GRAY = 8

    # --------------------------------------------------------------------------
    def __init__(self, mol_data: mp.MolData):
        super().__init__()
        self._mol = mol_data
        self._show_atom = True
        self._show_hete = True
        self._show_meta = True
        self._color_by = mp.ColorBy.ROW

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

        w_lsect = self.PDB_WIDTH + 2

        self.lsect = self.root.create_child( 1.0,  w_lsect, 0, 0)
        self.rsect = self.root.create_child( 1.0, -w_lsect, 0, w_lsect)

        self.lsect_body   = self.lsect.create_child(-self.H_GUIDES, 1.0,  0, 0)
        self.lsect_footer = self.lsect.create_child( self.H_GUIDES, 1.0, -1, 0)


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
            case pr.KEY_S_LOWER: self._toggle_atom()
            case pr.KEY_S_UPPER: self._toggle_atom()
            case pr.KEY_D_LOWER: self._toggle_hete()
            case pr.KEY_D_UPPER: self._toggle_hete()
            case pr.KEY_F_LOWER: self._toggle_meta()
            case pr.KEY_F_UPPER: self._toggle_meta()
            case self.KEY_CTRL_HOME: self._scroll_up(float("inf"))
            case self.KEY_CTRL_END:  self._scroll_down(float("inf"))

        hdisplay = self.lsect_body.h - 2
        self.NLINES_FAST_SCROLL = hdisplay // 2 # dinamically adjust fast scroll based on terminal height

        lines = tuple(self._mol.iter_lines(self._filter_key, hdisplay))
        chars = [line.text for line in lines]
        attrs = [self._get_attr_array(line) for line in lines]

        self.lsect.draw_matrix(1, 1, chars, attrs)
        self._draw_borders()
        self._draw_guides_top()
        self._draw_guides_bottom()

    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.key == pr.KEY_Q_LOWER or self.key == pr.KEY_Q_UPPER


    # --------------------------------------------------------------------------
    def _draw_guides_top(self):
        show_all = self._show_atom and self._show_hete and self._show_meta
        self.lsect_footer.draw_matrix(0, 2,
            *self._get_guides_matrices(guides = (
                ("filter→ ",  None),
                ("a: all",      show_all),
                ("s: atoms",    self._show_atom),
                ("d: hetatms",  self._show_hete),
                ("f: metadata", self._show_meta),
            ))
        )
        self.lsect_footer.draw_text(0, "r-2", "[h]elp", self.pair_help)


    # --------------------------------------------------------------------------
    def _draw_guides_bottom(self):
        self.lsect_footer.draw_matrix(1, 2,
            *self._get_guides_matrices(guides = (
                ("color→  ",  None),
                ("[c]olumn", self._color_by == mp.ColorBy.COLUMN),
                ("[r]ow",    self._color_by != mp.ColorBy.COLUMN),
            ))
        )
        self.lsect_footer.draw_text(0, "r-2", "[q]uit", self.pair_help)


    # --------------------------------------------------------------------------
    def _draw_borders(self):
        self.rsect.draw_border()
        self.lsect_body.draw_border()
        self.lsect_body.draw_text(0, 2, f" Molecule: {self._mol.name} ", pr.A_BOLD)
        self.lsect_footer.draw_border(bl = '│', bs = ' ', br = '│')


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

    # --------------------------------------------------------------------------
    def _get_guides_matrices(self, guides: list[tuple[str, bool]]) -> tuple[list[str], list[list[int]]]:
        def choose_pair(cond: bool) -> int:
            return self.pair_help_1 if cond else self.pair_help_0

        chars = "  ".join(f"{text}" for text, _ in guides)
        attrs = []
        for text, condition in guides:
            pair = self.pair_help if condition is None else choose_pair(condition)
            attrs.extend([pair for _ in text] + [pr.A_NORMAL, pr.A_NORMAL])
        return [chars], [attrs]


# //////////////////////////////////////////////////////////////////////////////

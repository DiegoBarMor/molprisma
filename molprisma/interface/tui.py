import molsimple as ms
import prismatui as pr

import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class TUIMolPrisma(pr.Terminal):
    NLINES_FAST_SCROLL = 10
    PDB_WIDTH = 80
    H_GUIDES = 2
    H_PDB_SECTIONS = 18

    KEY_SCROLL_TOP    = ord('-')
    KEY_SCROLL_BOTTOM = ord('+')

    COLOR_GRAY = 8
    COLOR_YELLOW_SOFT = 9
    COLOR_GREEN_SOFT = 10

    # --------------------------------------------------------------------------
    def __init__(self, mol_data: mp.MolData):
        super().__init__()
        self._mol: mp.MolData = mol_data
        self._show_atom: bool = True
        self._show_hete: bool = True
        self._show_meta: bool = True
        self._filter_key: callable[mp.MolLine] = lambda _: True

        ### this mask is used in TUIMolPrisma._get_attr_array for choosing appropriate column colors
        ### this is not a boolean mask. instead, it has 3 possible values
        ### 0: reserved for empty columns i.e. those not associated with PDB sections
        ### 1: first  color variation for relevant columns
        ### 2: second color variation for relevant columns
        self._mask_cols_alt_color: list[bool] = [0 for _ in range(ms.LENGTH_RECORD)]
        for i,section in enumerate(self._mol._sections):
            val_mask = 2 if i % 2 == 1 else 1
            self._mask_cols_alt_color[section.start:section.end] = [val_mask] * (section.end - section.start)

        self._str_sections_header: str = "0-index | 1-index  | Name       "
        self._strs_sections_body: list[str] = [
            " | ".join((
                section.display_idx_range(zero_indexing = True),
                section.display_idx_range(zero_indexing = False),
                section.name,
            )) for section in self._mol._sections
        ]


    # --------------------------------------------------------------------------
    def on_start(self):
        pr.init_color(self.COLOR_GRAY, 400, 400, 400)
        pr.init_color(self.COLOR_YELLOW_SOFT, 700, 700, 300)
        pr.init_color(self.COLOR_GREEN_SOFT, 200, 500, 200)
        self.pair_none = pr.init_pair(1, pr.COLOR_WHITE, pr.COLOR_RED)
        self.pair_meta = pr.init_pair(2, pr.COLOR_WHITE, self.COLOR_GRAY)
        self.pair_atom = pr.init_pair(3, pr.COLOR_BLACK, pr.COLOR_YELLOW)
        self.pair_hete = pr.init_pair(4, pr.COLOR_BLACK, pr.COLOR_GREEN)

        self.pair_atom_alt = pr.init_pair(5, pr.COLOR_BLACK, self.COLOR_YELLOW_SOFT)
        self.pair_hete_alt = pr.init_pair(6, pr.COLOR_BLACK, self.COLOR_GREEN_SOFT)

        self.pair_help   = pr.init_pair(7, pr.COLOR_BLACK, pr.COLOR_CYAN)
        self.pair_help_0 = pr.init_pair(8, pr.COLOR_WHITE, pr.COLOR_RED)
        self.pair_help_1 = pr.init_pair(9, pr.COLOR_BLACK, pr.COLOR_GREEN)

        w_lsect = self.PDB_WIDTH + 2

        self.lsect = self.root.create_child( 1.0,  w_lsect, 0, 0)
        self.rsect = self.root.create_child( 1.0, -w_lsect, 0, w_lsect)

        self.lsect_body   = self.lsect.create_child(-self.H_GUIDES, 1.0,  0, 0)
        self.lsect_footer = self.lsect.create_child( self.H_GUIDES, 1.0, -1, 0)
        self.rsect_top    = self.rsect.create_child( self.H_PDB_SECTIONS, 1.0, 0, 0)
        self.rsect_bottom = self.rsect.create_child(-self.H_PDB_SECTIONS, 1.0, self.H_PDB_SECTIONS, 0)


    # --------------------------------------------------------------------------
    def on_update(self):
        match self.key:
            case pr.KEY_UP:      self._scroll_up(1)
            case pr.KEY_DOWN:    self._scroll_down(1)
            case pr.KEY_LEFT:    self._prev_column()
            case pr.KEY_RIGHT:   self._next_column()
            case pr.KEY_PPAGE:   self._scroll_up(self.NLINES_FAST_SCROLL)
            case pr.KEY_NPAGE:   self._scroll_down(self.NLINES_FAST_SCROLL)
            case pr.KEY_A_LOWER: self._toggle_all()
            case pr.KEY_A_UPPER: self._toggle_all()
            case pr.KEY_S_LOWER: self._toggle_atom()
            case pr.KEY_S_UPPER: self._toggle_atom()
            case pr.KEY_D_LOWER: self._toggle_hete()
            case pr.KEY_D_UPPER: self._toggle_hete()
            case pr.KEY_F_LOWER: self._toggle_meta()
            case pr.KEY_F_UPPER: self._toggle_meta()
            case pr.KEY_C_LOWER: self._next_unique("chains")
            case pr.KEY_C_UPPER: self._next_unique("chains")
            case pr.KEY_E_LOWER: self._next_unique("elements")
            case pr.KEY_E_UPPER: self._next_unique("elements")
            case pr.KEY_R_LOWER: self._next_unique("resnames")
            case pr.KEY_R_UPPER: self._next_unique("resnames")
            case pr.KEY_X_LOWER: self._reset_filters()
            case pr.KEY_X_UPPER: self._reset_filters()
            case self.KEY_SCROLL_TOP:    self._scroll_up(float("inf"))
            case self.KEY_SCROLL_BOTTOM: self._scroll_down(float("inf"))

        hdisplay = self.lsect_body.h - 2
        self.NLINES_FAST_SCROLL = hdisplay // 2 # dinamically adjust fast scroll based on terminal height

        lines = tuple(self._mol.iter_lines(self._filter_key, hdisplay))
        chars = [line.text for line in lines]
        attrs = [self._get_attr_array(line) for line in lines]

        self.lsect.draw_matrix(1, 1, chars, attrs)

        self._draw_borders()
        self._draw_guides_top()
        self._draw_guides_bottom()

        self.rsect_top.draw_text(1, 2, self._str_sections_header, pr.A_UNDERLINE)
        for i,chars in enumerate(self._strs_sections_body):
            self.rsect_top.draw_text(2+i, 2, chars,
                attr = pr.A_REVERSE if i == self._mol.current_section else pr.A_NORMAL
            )

        for i,k in enumerate(self._mol.UNIQUE_VALS_KEYS.keys(), start = 1):
            chars, attrs = self._mol.get_unique_chars_attrs(k)
            self.rsect_bottom.draw_text(i, 2, f"{k}:")
            self.rsect_bottom.draw_text(i, 12, chars, attrs)
        self.rsect_bottom.draw_text(i+1, 2, "... Press [c]/[e]/[r] to show only rows")
        self.rsect_bottom.draw_text(i+2, 2, "... matching a specific chain/element/residue.")


    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.key == pr.KEY_Q_LOWER or self.key == pr.KEY_Q_UPPER


    # --------------------------------------------------------------------------
    def _draw_guides_top(self):
        show_all = self._show_atom and self._show_hete and self._show_meta
        self.lsect_footer.draw_matrix(0, 2,
            *self._get_guides_matrices(guides = (
                ("toggle...",     None),
                ("a: all",        show_all),
                ("s: atoms",      self._show_atom),
                ("d: hetatms",    self._show_hete),
                ("f: metadata",   self._show_meta),
                ("c/e/r: filter", self._mol.current_unique is not None),
            ))
        )
        self.lsect_footer.draw_text(0, "r-2", "x: reset", self.pair_help)


    # --------------------------------------------------------------------------
    def _draw_guides_bottom(self):
        self.lsect_footer.draw_matrix(1, 2,
            *self._get_guides_matrices(guides = (
                ("move...", None),
                ("↑/↓: rows", None),
                ("←/→: cols", None),
                ("PPage/NPage: fast scroll",  None),
                ("-: top", None),
                ("+: end", None),
            ))
        )
        self.lsect_footer.draw_text(1, "r-2", "[q]uit", self.pair_help)


    # --------------------------------------------------------------------------
    def _draw_borders(self):
        self.lsect_body.draw_border()
        self.lsect_body.draw_text(0, 2, f" {self._mol.name} ", pr.A_BOLD)

        self.lsect_footer.draw_border(bl = '│', bs = ' ', br = '│')

        self.rsect_top.draw_border()
        self.rsect_top.draw_text(0, 2, " PDB Sections ", pr.A_BOLD)

        self.rsect_bottom.draw_border()
        self.rsect_bottom.draw_text(0, 2, " Unique Values ", pr.A_BOLD)


    # --------------------------------------------------------------------------
    def _scroll_up(self, nlines: int):
        self._mol.current_line = max(0, self._mol.current_line - nlines)


    # --------------------------------------------------------------------------
    def _scroll_down(self, nlines: int):
        nlines_available = self._mol.count_lines(self._filter_key) - 1 # account for NONE terminator line
        self._mol.current_line = min(self._mol.current_line + nlines, nlines_available - 1)


    # --------------------------------------------------------------------------
    def _prev_column(self):
        idx = (self._mol.nsections - 1) \
            if (self._mol.current_section is None) \
            else (self._mol.current_section - 1)
        if idx == -1: idx = None
        self._mol.current_section = idx


    # --------------------------------------------------------------------------
    def _next_column(self):
        idx = 0 if (self._mol.current_section is None) \
            else (self._mol.current_section + 1)
        if idx == self._mol.nsections: idx = None
        self._mol.current_section = idx


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
    def _next_unique(self, name: str):
        self._update_filter_key()
        prev_name = self._mol.current_unique
        self._mol.current_unique = name
        if name != prev_name: return
        self._mol.increment_idx_unique_current()
        self._update_pos()


    # --------------------------------------------------------------------------
    def _reset_filters(self):
        self._show_meta = True
        self._show_atom = True
        self._show_hete = True
        self._mol.current_unique = None
        self._update_filter_key()
        self._update_pos()


    # --------------------------------------------------------------------------
    def _get_attr_array(self, line: mp.MolLine) -> list[int]:
        def get_attr_atoms(i):
            idx_sect = self._mol.get_idx_section(i)
            if idx_sect is None: return pr.A_NORMAL
            return pr.A_REVERSE if idx_sect == self._mol.current_section else pr.A_NORMAL

        get_attr_other = lambda _: pr.A_NORMAL

        match line.kind: #               color_empty   | color_standard| color_alt         | highligh or normal attr
            case mp.MolKind.NONE: tup = (self.pair_none, self.pair_none, self.pair_none,     get_attr_other)
            case mp.MolKind.META: tup = (self.pair_meta, self.pair_meta, self.pair_meta,     get_attr_other)
            case mp.MolKind.ATOM: tup = (self.pair_meta, self.pair_atom, self.pair_atom_alt, get_attr_atoms)
            case mp.MolKind.HETE: tup = (self.pair_meta, self.pair_hete, self.pair_hete_alt, get_attr_atoms)
            case _: raise ValueError("Unknown MolKind")

        return [
            tup[int(m)] | tup[3](i)
            for i,m in enumerate(self._mask_cols_alt_color)
        ]


    # --------------------------------------------------------------------------
    def _update_filter_key(self):
        def filterkey(line: mp.MolLine) -> bool:
            if self._mol.current_unique is not None:
                if not self._mol.match_current_unique_char(line):
                    return line.kind == mp.MolKind.NONE # "none" lines should never be skipped

            match line.kind:
                case mp.MolKind.NONE: return True
                case mp.MolKind.META: return self._show_meta
                case mp.MolKind.ATOM: return self._show_atom
                case mp.MolKind.HETE: return self._show_hete
                case _: raise ValueError("Unknown MolKind")

        self._filter_key = filterkey


    # --------------------------------------------------------------------------
    def _update_pos(self):
        self._mol.current_line = 0
        for idx, line in enumerate(self._mol.iter_lines(self._filter_key)):
            if not self._filter_key(line): continue
            self._mol.current_line = idx
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

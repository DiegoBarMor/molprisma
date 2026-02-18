import molsimple as ms
import prismatui as pr

import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class MolData:
    KEYS_FILTERS = {
        "altloc": "ALTLOC",
        "chains": "CHAIN_ID",
        "elements": "ELEMENT_SYMBOL",
        "resnames": "RESIDUE_NAME",
    }

    # --------------------------------------------------------------------------
    def __init__(self, name = ""):
        self.name: str = name
        self.nsections = 0
        self.current_line: int = 0 # a.k.a row
        self.current_section: int | None = None # a.k.a column

        self._refs_filters: dict[str, list[str]] = {
            # store all the possible reference strings for every filter
            "altloc" : [],   "chains" : [],   "elements" : [],   "resnames" : [],
        }
        self._idxs_filters: dict[str, int | None] = {
            # store the current index of every filter (None if disabled)
            "altloc" : None, "chains" : None, "elements" : None, "resnames" : None,
        }

        self._idxs_chars2idxs_sects = [None for _ in range(ms.LENGTH_RECORD)]
        self._lines: list[mp.MolLine] = []
        self._sections: list[mp.PDBSection] = []

    # --------------------------------------------------------------------------
    def __len__(self):
        return len(self._lines)

    # --------------------------------------------------------------------------
    def reset(self):
        self.current_line = 0
        self.current_section = None
        self._idxs_chars2idxs_sects = [None for _ in range(ms.LENGTH_RECORD)]
        for v in self._refs_filters.values(): v.clear()
        self._lines.clear()
        self._sections.clear()

    # --------------------------------------------------------------------------
    def init_sections(self):
        constants = ms.get_pdb_constants()
        keys = set(k[:-4] for k in constants.keys() if k.endswith("_END"))
        for key in keys:
            start = constants.get(f"{key}_START", None)
            end   = constants.get(f"{key}_END",   None)
            if start is None or end is None: continue
            self._sections.append(mp.PDBSection(key, start, end))

        self._sections.sort(key = lambda s: s.start)
        self.nsections = len(self._sections)

        for i,section in enumerate(self._sections):
            self._idxs_chars2idxs_sects[section.start:section.end] = [i] * (section.end - section.start)

    # --------------------------------------------------------------------------
    def init_filters(self):
        for k,name_section in self.KEYS_FILTERS.items():
            self._refs_filters[k] = list(sorted(set(
                line.get_section_data(name_section) for line in self._lines
            ) - {None}))

    # --------------------------------------------------------------------------
    def append(self, line: mp.MolLine):
        self._lines.append(line)

    # --------------------------------------------------------------------------
    def extend(self, lines: list[mp.MolLine]):
        self._lines.extend(lines)

    # --------------------------------------------------------------------------
    def pad_lines(self):
        max_line_length = max(len(line.text) for line in self._lines)
        for line in self._lines:
            line.text = line.text.ljust(max_line_length)

    # --------------------------------------------------------------------------
    def count_lines(self, filterkey: callable = None) -> int:
        if filterkey is None:
            filterkey = lambda _: 1
        return sum(filterkey(line) for line in self._lines)

    # --------------------------------------------------------------------------
    def iter_lines(self, filterkey: callable, nlines: int = None):
        if nlines is None:
            nlines = len(self._lines) - self.current_line

        lines = tuple(
            filter(filterkey, self._lines)
        )[self.current_line : self.current_line+nlines]

        for line in lines:
            yield line

    # --------------------------------------------------------------------------
    def iter_sections(self):
        for section in self._sections:
            yield section

    # --------------------------------------------------------------------------
    def get_idx_section(self, idx_char: int):
        """Returns the section index associated to a character's column index"""
        return self._idxs_chars2idxs_sects[idx_char]

    # --------------------------------------------------------------------------
    def prev_column(self):
        self.current_section = mp.Utils.prev_cyclic(self.current_section, self.nsections)

    # --------------------------------------------------------------------------
    def next_column(self):
        self.current_section = mp.Utils.next_cyclic(self.current_section, self.nsections)

    # --------------------------------------------------------------------------
    def next_filter(self, key):
        self._assert_key(key)
        vals = self._refs_filters[key]
        self._idxs_filters[key] = mp.Utils.next_cyclic(
            self._idxs_filters[key], len(vals)
        )

    # --------------------------------------------------------------------------
    def reset_filter_idxs(self):
        for k in self._idxs_filters.keys():
            self._idxs_filters[k] = None

    # --------------------------------------------------------------------------
    def any_filter_active(self):
        return any(idx is not None for idx in self._idxs_filters.values())

    # --------------------------------------------------------------------------
    def get_filter_render_data(self, key: str) -> tuple[str, list[int]]:
        """Return 'chars' and 'attrs' data for rendering a filter's state with PrismaTUI"""
        self._assert_key(key)
        vals = [v if v else "''" for v in self._refs_filters[key]]
        idx = self._idxs_filters[key]

        chars = ' '.join(vals)
        mask = ' '.join(
            len(v)*('!' if idx == i else ' ')
            for i,v in enumerate(vals)
        )
        attrs = [[pr.A_REVERSE if m == '!' else pr.A_NORMAL for m in mask]]
        return chars, attrs

    # --------------------------------------------------------------------------
    def match_filters(self, line: mp.MolLine) -> bool:
        for key in self._refs_filters.keys():
            if not self._match_filter(line, key):
                return False
        return True

    # --------------------------------------------------------------------------
    def _match_filter(self, line: mp.MolLine, key: str) -> bool:
        vals = self._refs_filters[key]
        idx = self._idxs_filters[key]
        if idx is None: return True

        key_pdb_section = self.KEYS_FILTERS[key]
        to_evaluate = line.get_section_data(key_pdb_section)
        if to_evaluate is None: return False

        return to_evaluate.strip() == vals[idx]

    # --------------------------------------------------------------------------
    def _assert_key(self, key: str):
        assert key in self._refs_filters, \
            f"Invalid key for MolData's filter: '{key}'. " +\
            f"Available filters: {self._refs_filters.keys()}"


# //////////////////////////////////////////////////////////////////////////////

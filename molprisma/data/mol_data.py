import molsimple as ms
import prismatui as pr

import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class MolData:
    UNIQUE_VALS_KEYS = {
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
        self.current_unique: str | None = None # can be set to a unique value name to show only that one (i.e. "chains")

        self._unique_vals: dict[str, list[str]] = {
            "chains" : [], "elements" : [], "resnames" : [],
        }
        self._idx_unique_current: dict[str, list[str]] = {
            "chains" : 0,  "elements" : 0,  "resnames" : 0,
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
        for v in self._unique_vals.values(): v.clear()
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
    def init_unique_values(self):
        for k,name_section in self.UNIQUE_VALS_KEYS.items():
            self._unique_vals[k] = list(sorted(set(
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
    def increment_idx_unique_current(self):
        key = self.current_unique
        self._assert_key(key)

        vals = self._unique_vals[key]
        idx = self._idx_unique_current[key] + 1
        if idx >= len(vals): idx = 0
        self._idx_unique_current[key] = idx

    # --------------------------------------------------------------------------
    def match_current_unique_char(self, line: mp.MolLine) -> bool:
        key = self.current_unique
        self._assert_key(key)

        vals = self._unique_vals[key]
        idx = self._idx_unique_current[key]
        ref = vals[idx]

        key_pdb_section = self.UNIQUE_VALS_KEYS[self.current_unique]
        to_evaluate = line.get_section_data(key_pdb_section)
        if to_evaluate is None: return False

        return to_evaluate.strip() == ref

    # --------------------------------------------------------------------------
    def get_unique_chars_attrs(self, key: str) -> tuple[str, list[int]]:
        self._assert_key(key)
        vals = [v if v else "''" for v in self._unique_vals[key]]
        idx = self._idx_unique_current[key]

        chars = ' '.join(vals)
        if self.current_unique != key:
            return chars, pr.A_NORMAL

        mask = ' '.join(
            len(v)*('!' if idx == i else ' ')
            for i,v in enumerate(vals)
        )
        attrs = [[pr.A_REVERSE if m == '!' else pr.A_NORMAL for m in mask]]
        return chars, attrs

    # --------------------------------------------------------------------------
    def _assert_key(self, key: str):
        assert key in self._unique_vals, \
            f"Invalid key for MolData's unique chars: '{key}'. " +\
            f"Available keys: {self._unique_vals.keys()}"


# //////////////////////////////////////////////////////////////////////////////

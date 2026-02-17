import molsimple as ms

import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class MolData:
    def __init__(self, name = ""):
        self.name: str = name
        self.nsections = 0
        self.current_line: int = 0 # a.k.a row
        self.current_section: int | None = None # a.k.a column
        self.unique_chains:   list[str] = []
        self.unique_elements: list[str] = []
        self.unique_resnames: list[str] = []

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
        self.unique_chains.clear()
        self.unique_elements.clear()
        self.unique_resnames.clear()
        self._lines.clear()
        self._sections.clear()

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
        self.unique_chains = list(sorted(set(
            line.get_section_data("CHAIN_ID") for line in self._lines
        ) - {None}))
        self.unique_elements = list(sorted(set(
            line.get_section_data("ELEMENT_SYMBOL") for line in self._lines
        ) - {None}))
        self.unique_resnames = list(sorted(set(
            line.get_section_data("RESIDUE_NAME") for line in self._lines
        ) - {None}))


# //////////////////////////////////////////////////////////////////////////////

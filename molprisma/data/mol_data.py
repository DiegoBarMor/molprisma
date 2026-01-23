import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class MolData:
    def __init__(self):
        self.pos = 0
        self._all_lines: list[mp.MolLine] = []
        self._meta: list[mp.MolLine] = []
        self._data: list[mp.MolLine] = []

    # --------------------------------------------------------------------------
    def extend_meta(self, lines: list[str]):
        self._all_lines.extend(lines)
        self._meta.extend(lines)

    # --------------------------------------------------------------------------
    def extend_data(self, lines: list[str]):
        self._all_lines.extend(lines)
        self._data.extend(lines)

    # --------------------------------------------------------------------------
    def pad_lines(self):
        max_line_length = max(len(line.text) for line in self._all_lines)
        for line in self._all_lines:
            line.text = line.text.ljust(max_line_length)

    # --------------------------------------------------------------------------
    def iter_lines(self, nlines: int):
        for line in self._all_lines[self.pos:self.pos+nlines]:
            yield line


# //////////////////////////////////////////////////////////////////////////////

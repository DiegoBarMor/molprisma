import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class MolData:
    def __init__(self):
        self.pos = 0
        self._lines: list[mp.MolLine] = []

    # --------------------------------------------------------------------------
    def __len__(self):
        return len(self._lines)

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
    def iter_lines(self, nlines: int = None, filterkey: callable = None):
        if nlines is None:
            nlines = len(self._lines) - self.pos

        if filterkey is None:
            filterkey = lambda _: True

        lines = tuple(
            filter(filterkey, self._lines)
        )[self.pos : self.pos+nlines]

        for line in lines:
            yield line


# //////////////////////////////////////////////////////////////////////////////

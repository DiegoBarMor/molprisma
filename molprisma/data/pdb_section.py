# //////////////////////////////////////////////////////////////////////////////
class PDBSection:
    def __init__(self, name: str, start: int, end: int):
        self.name = name
        self.start = start
        self.end = end

    # --------------------------------------------------------------------------
    def display_idx_range(self, zero_indexing: bool = True) -> str:
        if zero_indexing:
            return f"[{self.start:02},{self.end:02}["
        return f"({self.start+1:02}..{self.end:02})"


# //////////////////////////////////////////////////////////////////////////////

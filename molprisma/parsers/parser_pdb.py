import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class ParserPDB:
    KEYWORDS_DATA = ("ATOM", "HETATM")

    # --------------------------------------------------------------------------
    def __init__(self, path_pdb):
        with open(path_pdb, 'r') as file:
            self._raw = file.readlines()

    # --------------------------------------------------------------------------
    def parse(self) -> mp.MolData:
        mol = mp.MolData()

        mask = [line.startswith(self.KEYWORDS_DATA) for line in self._raw]
        data = [
            mp.MolLine(line.rstrip('\n'), mp.MolKind.DATA)
            for line,m in zip(self._raw, mask) if m
        ]
        meta = [
            mp.MolLine(line.rstrip('\n'), mp.MolKind.META)
            for line,m in zip(self._raw, mask) if not m
        ]
        mol.extend_meta(meta)
        mol.extend_data(data)
        mol.pad_lines()
        return mol


# //////////////////////////////////////////////////////////////////////////////

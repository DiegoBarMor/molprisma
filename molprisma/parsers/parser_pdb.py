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
        def get_kind(line: str) -> mp.MolKind:
            if line.startswith(self.KEYWORDS_DATA):
                return mp.MolKind.DATA
            return mp.MolKind.META

        mol = mp.MolData()
        mol.extend([
            mp.MolLine(line.rstrip('\n'), get_kind(line))
            for line in self._raw
        ])
        mol.pad_lines()
        return mol


# //////////////////////////////////////////////////////////////////////////////

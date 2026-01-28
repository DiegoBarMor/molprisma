from pathlib import Path

import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class ParserPDB:
    KEYWORD_ATOM = "ATOM"
    KEYWORD_HETA = "HETATM"

    # --------------------------------------------------------------------------
    def __init__(self, path_pdb: str | Path):
        self.path_pdb = Path(path_pdb)
        self._mol = mp.MolData(self.path_pdb.name)
        self._raw: list[str] = self.path_pdb.read_text().splitlines()


    # --------------------------------------------------------------------------
    def parse(self) -> mp.MolData:
        self._mol.reset()
        self._parse_lines()
        return self._mol


    # --------------------------------------------------------------------------
    def _parse_lines(self):
        def get_kind(line: str) -> mp.MolKind:
            if line.startswith(self.KEYWORD_ATOM):
                return mp.MolKind.ATOM
            if line.startswith(self.KEYWORD_HETA):
                return mp.MolKind.HETE
            return mp.MolKind.META

        self._mol.extend([
            mp.MolLine(line.rstrip('\n'), get_kind(line))
            for line in self._raw
        ])
        self._mol.append(mp.MolLine('', mp.MolKind.NONE))
        self._mol.pad_lines()



# //////////////////////////////////////////////////////////////////////////////

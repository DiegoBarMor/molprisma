from pathlib import Path

import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class ParserPDB:
    KEYWORD_ATOM = "ATOM"
    KEYWORD_HETA = "HETATM"

    # --------------------------------------------------------------------------
    def __init__(self, path_pdb: str | Path):
        self._path_pdb: Path = Path(path_pdb)
        with open(path_pdb, 'r') as file:
            self._raw = file.readlines()

    # --------------------------------------------------------------------------
    def parse(self) -> mp.MolData:
        def get_kind(line: str) -> mp.MolKind:
            if line.startswith(self.KEYWORD_ATOM):
                return mp.MolKind.ATOM
            if line.startswith(self.KEYWORD_HETA):
                return mp.MolKind.HETE
            return mp.MolKind.META

        mol = mp.MolData(self._path_pdb.stem)
        mol.extend([
            mp.MolLine(line.rstrip('\n'), get_kind(line))
            for line in self._raw
        ])
        mol.append(mp.MolLine('', mp.MolKind.NONE))
        mol.pad_lines()
        return mol


# //////////////////////////////////////////////////////////////////////////////

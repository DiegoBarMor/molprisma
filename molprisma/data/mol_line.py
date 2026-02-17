import molsimple as ms

import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class MolLine:
    def __init__(self, text: str, kind: "mp.MolKind"):
        self.text = text
        self.kind = kind

    # --------------------------------------------------------------------------
    def get_section_data(self, name_section: str):
        if self.kind not in (mp.MolKind.ATOM, mp.MolKind.HETE): return
        constants = ms.get_pdb_constants()
        start = constants.get(f"{name_section}_START", None)
        end   = constants.get(f"{name_section}_END",   None)
        if start is None or end is None: return
        return self.text[start:end].strip()


# //////////////////////////////////////////////////////////////////////////////

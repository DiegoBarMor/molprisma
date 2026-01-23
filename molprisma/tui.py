import prismatui as pr
import molprisma as mp

# //////////////////////////////////////////////////////////////////////////////
class TUIMolPrisma(pr.Terminal):
    def __init__(self, mol_data: mp.MolData):
        super().__init__()
        self._mol = mol_data

    # --------------------------------------------------------------------------
    def on_start(self):
        pr.init_pair(1, pr.COLOR_BLACK, pr.COLOR_CYAN)

    # --------------------------------------------------------------------------
    def on_update(self):
        self.draw_text('t', 'l', self._mol.text)
        self.draw_text('b', 'l', "Press F1 to exit", pr.get_color_pair(1))

    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.key == pr.KEY_F1


# //////////////////////////////////////////////////////////////////////////////

import sys
from pathlib import Path

import molprisma as mp

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def main():
    mol = mp.ParserPDB(PATH_STRUCT).mol
    mp.TUIMolPrisma(mol).run()


################################################################################
if __name__ == "__main__":
    PATH_STRUCT = Path(sys.argv[1])
    main()


################################################################################
# python3 main.py testdata/1akx.pdb

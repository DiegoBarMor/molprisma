import sys
from pathlib import Path

import molprisma as mp

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def main():
    if len(sys.argv) < 2:
        print("usage: molprisma [path_pdb]")
        exit(-1)

    PATH_STRUCT = Path(sys.argv[1])
    mol = mp.ParserPDB(PATH_STRUCT).parse()
    mp.TUIMolPrisma(mol).run()


################################################################################
if __name__ == "__main__":
    main()


################################################################################

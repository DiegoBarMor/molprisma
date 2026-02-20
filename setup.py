from setuptools import setup, find_packages
from pathlib import Path

def read_requirements(path = "requirements.txt"):
    p = Path(path)
    if not p.exists(): return []
    stripped_lines = (ln.strip() for ln in p.read_text().strip().splitlines())
    return [ln for ln in stripped_lines if ln and not ln.startswith("#")]

setup(
    name="molprisma",
    version="1.0.0",
    description="Tool for fast inspection of PDB molecular files inside the terminal",
    keywords="pdb rcsb molecular terminal tui protein nucleic rna dna ligand",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="DiegoBarMor",
    author_email="diegobarmor42@gmail.com",
    url="https://github.com/diegobarmor/molprisma",
    license="MIT",
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "molprisma=molprisma.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)

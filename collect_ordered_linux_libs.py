# %%
import os
from os.path import join
from subprocess import check_output
from collections import defaultdict
from typing import List, Dict


# %%
# this script figures out the correct link order for static lib files.
# if there are doubly defined symbols, try to fix these by putting unused
# libs in the end of the conan-libs in package_info.
def collect_ordered_linux_libs(libfolder: str) -> List[str]:
    os.chdir(libfolder)
    symToLibNeeded: Dict[str, set[str]] = defaultdict(lambda: set())
    symToLibDefined: Dict[str, set[str]] = defaultdict(lambda: set())
    for file in os.listdir():
        if not file.endswith(".a"):
            continue
        r = check_output(f"nm -go {file}".split()).decode("utf-8")
        if r == "":
            continue
        lines = r.split("\n")[:-1]
        for line in lines:
            cols = line.split()
            defState = cols[1].strip()
            sym = cols[2].strip()
            if defState == "U":
                symToLibNeeded[sym].add(file)
            else:
                symToLibDefined[sym].add(file)
    for symbol, libs_needing in symToLibDefined.items():
        if symbol not in symToLibNeeded:
            continue

        symToLibNeeded[symbol] = symToLibNeeded[symbol].difference(libs_needing)
    output = set()
    for symbol, libs_needing in symToLibNeeded.items():
        for lib_needing in libs_needing:
            for lib_defining in symToLibDefined[symbol]:
                output.add(f"{lib_needing} {lib_defining}")
    linkdepsfile = join(libfolder, "linkdeps.txt")
    with open(linkdepsfile, "w") as f:
        for dep in output:
            f.write(f"{dep}\n")

    order = check_output(f'cat "{linkdepsfile}" | tsort', shell=True).decode("utf-8")
    return order.split("\n")[:-1]

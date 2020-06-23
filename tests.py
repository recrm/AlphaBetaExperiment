from collections import OrderedDict
import xml.etree.ElementTree as ET

import udebs
import progressbar

import udebs_config
#---------------------------------------------------
#                    Configuration                 -
#---------------------------------------------------
import va_window as module # modify this import to change which version is being tested
weak = False # set this to true for any module after and includeing the strong solver.

row_count = 1000 # use smaller number to run less tests. 1000 is the maximum.

# Comment out tests you don't want to run.
tests = [
    "tests/Test_L3_R1",
    "tests/Test_L2_R1",
    "tests/Test_L1_R1",
    "tests/Test_L2_R2",
#     "tests/Test_L1_R2",
#     "tests/Test_L1_R3"
]
####################################################

def modifyconfig(config, x, y):
    root = ET.parse(config).getroot()
    root.find("map/dim/x").text = str(x)
    root.find("map/dim/y").text = str(y)
    return ET.tostring(root)

def setup(main_map, raw_moves):
    main_map.resetState()
    for x,y,z in udebs.alternate(["xPlayer", "oPlayer"], list(map(int, raw_moves)), "drop"):
        main_map.castMove(x,(y-1,0),z)
        main_map.controlTime()

    return main_map

def printBad(main_map, expected, result):
    main_map.printMap()
    print(pos)
    print("result", result, "expected", expected)
    print("xPlayer", main_map.getStat("xPlayer", "ACT"))

if __name__ == "__main__":
    with udebs.Timer():
        modified = modifyconfig(udebs_config.config,7,6)
        main_map = udebs.battleStart(modified, field=module.Connect4())

        widgets = [
            "(",progressbar.SimpleProgress(),") ",
            progressbar.Bar()," ",
            progressbar.Timer()," ",
            progressbar.AdaptiveETA(),
        ]

        for test_file in tests:
            module.storage = OrderedDict()
            module.counter = 0

            print(test_file)
            with open(test_file) as f:
                with udebs.Timer() as t:
                    for i in progressbar.progressbar(range(row_count), widgets=widgets):
                        pos, expected = f.readline().strip().split()
                        expected = int(expected)
                        main_map = setup(main_map, pos)

                        result = main_map.result()

                        if weak and expected != 0:
                            expected = expected / abs(expected)

                        if result != expected:
                            printBad(main_map, expected, result)
                            break

                print("average time per puzzle:", t.total / 1000)
                print("average number of positions:", module.counter / row_count)
                print("Positions per second", module.counter / t.total)
                print()

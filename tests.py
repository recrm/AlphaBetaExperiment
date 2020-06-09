import pathlib
from v9_strongsolver import Connect4
import udebs
import udebs_config
import xml.etree.ElementTree as ET

def modifyconfig(config, x, y):
    tree = ET.parse(config)
    root = tree.getroot()

    root.find("map/dim/x").text = str(x)
    root.find("map/dim/y").text = str(y)

    return ET.tostring(root)

def setup(raw_moves, config):
    main_map = udebs.battleStart(config, field=Connect4())

    moves = [int(i) for i in raw_moves]

    for x,y,z in udebs.alternate(["xPlayer", "oPlayer"], moves, "drop"):
        main_map.castMove(x,(y-1,0),z)
        main_map.controlTime()

    return main_map

if __name__ == "__main__":

    modified = modifyconfig(udebs_config.config,7,6)

    for test_file in pathlib.Path("tests").glob("**/*"):
        go = True
        for i in ["L1_R2", "L2_R2", "L1_R1", "L1_R3"]:
            if i in str(test_file):
                go = False

        if not go:
            continue

        print(test_file)
        with test_file.open() as f:
            row_count = 0
            with udebs.Timer() as t:
                for row in f:
                    row_count +=1
                    pos, expected = row.split()
                    expected = int(expected)

                    main_map = setup(pos, modified)
                    result = main_map.result(-22, 22)
                    if result != expected:
                        main_map.printMap()
                        print(pos)
                        print("result", result, "expected", expected)
                        print("xPlayer", main_map.getStat("xPlayer", "ACT"))
                        break

            print("average time per position:", t.total / row_count)
            print()
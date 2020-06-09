import udebs
import functools
import udebs_config

class Connect4(udebs.State):
    win_cond = 4

    def legalMoves(self):
        player = "xPlayer" if self.getStat("xPlayer", "ACT") >= 2 else "oPlayer"
        for x in range(self.map["map"].x):
            yield player, (x, 0), "drop"

    @udebs.countrecursion
    def result(self):
        if self.value is not None:
            return -abs(self.value)

        return max(-i.result() for i,e in self.substates())

if __name__ == "__main__":
    main_map = udebs.battleStart(udebs_config.config, field=Connect4())
    main_map.printMap()

    with udebs.Timer():
        result = main_map.result()

    print(result)
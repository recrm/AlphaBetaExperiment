import udebs
import functools
import udebs_config

class Connect4(udebs.State):
    win_cond = 4

    def hash(self):
        map_ = self.getMap()
        mappings = {
            "empty": "0",
            "x": "1",
            "o": "2",
        }

        data = []
        sym = []
        for y in range(map_.y):
            buf = [mappings[map_[x,y]] for x in range(map_.x)]
            data.extend(buf)
            sym.extend(reversed(buf))

        return min(int("".join(data), 3), int("".join(sym), 3))

    def legalMoves(self):
        player = "xPlayer" if self.getStat("xPlayer", "ACT") >= 2 else "oPlayer"
        for x in range(self.map["map"].x):
            yield player, (x, 0), "drop"

    @udebs.countrecursion
    @udebs.cache
    def result(self, alpha=-float("inf"), beta=float("inf")):
        if self.value is not None:
            return -abs(self.value)

        for child, e in self.substates():
            result = -child.result(-beta, -alpha)

            if result > alpha:
                alpha = result
                if alpha >= beta:
                    return alpha

        return alpha

if __name__ == "__main__":
    main_map = udebs.battleStart(udebs_config.config, field=Connect4())
    main_map.printMap()

    with udebs.Timer():
        result = main_map.result()

    print(result)
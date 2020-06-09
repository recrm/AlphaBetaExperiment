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
        map_ = self.map["map"]
        player = "xPlayer" if self.getStat("xPlayer", "ACT") >= 2 else "oPlayer"
        other = self.getStat("oPlayer" if player == "xPlayer" else "xPlayer", "token")
        token = self.getStat(player, "token")

        options = []
        forced = None

        for x in range(map_.x):
            y = udebs_config.BOTTOM(map_, x)
            if y is not None:
                loc = (x, y)
                position = player, loc, "drop"

                # Check if we win
                if udebs_config.win(map_, token, loc) >= self.win_cond:
                    yield position
                    return

                # we are in check and must play here.
                if forced is None:
                    if udebs_config.win(map_, other, loc) >= self.win_cond:
                        forced = position

                    options.append(position)

        if forced:
            yield forced
            return

        yield from options

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
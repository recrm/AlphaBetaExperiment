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
        backup = None
        for x in range(map_.x):
            y = udebs_config.BOTTOM(map_, x)
            if y is not None:

                loc = (x, y)

                if udebs_config.win(map_, other, loc) >= self.win_cond:
                    if forced is not None:
                        yield 1
                        return

                    forced = loc

                if y > 0:
                    if udebs_config.win(map_, other, (x, y - 1)) >= self.win_cond:
                        # We cannot play here unless it is our only option
                        backup = 1
                        if forced == loc:
                            yield 1
                            return

                        continue

                # finally these are our only good options
                if forced is None:
                    options.append(loc)

        if forced:
            yield player, forced, "drop"
        elif len(options) > 0:
            for loc in options:
                yield player, loc, "drop"
        else:
            yield backup if backup else 0

    def result(self, alpha=-1, beta=1):
        if self.value is not None:
            return -abs(self.value)

        map_ = self.getMap()
        player = "xPlayer" if self.getStat("xPlayer", "ACT") >= 2 else "oPlayer"
        token = "x" if player == "xPlayer" else "o"
        for x in range(map_.x):
            y = udebs_config.BOTTOM(map_, x)
            if y is not None:
                if udebs_config.win(map_, token, (x,y)) >= self.win_cond:
                    return 1

        return self.negamax(alpha, beta)

    @udebs.countrecursion
    @udebs.cache
    def negamax(self, alpha, beta):
        current = -float("inf")
        for child, e in self.substates():
            if child is e:
                result = -child
            else:
                result = -child.negamax(-beta, -alpha)

            if result > current:
                current = result
                if result > alpha:
                    alpha = result
                    if alpha >= beta:
                        break

        return current

if __name__ == "__main__":
    main_map = udebs.battleStart(udebs_config.config, field=Connect4())
    main_map.printMap()

    with udebs.Timer():
        result = main_map.result()

    print(result)
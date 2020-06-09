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
                position = player, loc, "drop"

                # First check if we win here.
                win_me = udebs_config.win(map_, token, loc)
                if win_me >= self.win_cond:
                    yield -1
                    return

                if forced is None:
                    win_you = udebs_config.win(map_, other, loc)
                    if win_you >= self.win_cond:
                        # we are in check, must play here
                        forced = position
                        continue

                    if y > 0:
                        above_you = udebs_config.win(map_, other, (x, y - 1))
                        if above_you >= self.win_cond:
                            # We cannot play here unless it is our only option
                            backup = 1
                            continue

                    # finally these are our only good options
                    options.append(position)

        if forced:
            yield forced
            return
        elif len(options) == 0:
            yield backup if backup else 0
            return

        yield from options

    def result(self, alpha=-1, beta=1):
        if self.value is not None:
            return -abs(self.value)

        return self.negamax(alpha, beta)

    @udebs.countrecursion
    @udebs.cache
    def negamax(self, alpha, beta):
        for child, e in self.substates():
            if child is e:
                result = -child
            else:
                result = -child.negamax(-beta, -alpha)

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
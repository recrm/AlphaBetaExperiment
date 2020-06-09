import udebs
import functools
import udebs_config
from collections import OrderedDict

def cache(f, maxsize=2**20):
    storage = OrderedDict()
    empty = (-float("inf"), float("inf"))

    @functools.wraps(f)
    def cache_wrapper(self, alpha, beta, map_):
        key = self.hash(map_)

        a_, b_ = storage.get(key, empty)
        if a_ > alpha:
            alpha = a_

        if b_ < beta:
            beta = b_

        if alpha >= beta:
            # Note: Alpha and beta may not be the same.
            # Returning either will produce the right answer, but
            # it is unclear which is more effecient.
            return beta

        result = f(self, alpha, beta, map_)
        if result <= alpha:
            storage[key] = (a_, result)
        elif result >= beta:
            storage[key] = (result, b_)
        else:
            storage[key] = (result, result)

        storage.move_to_end(key)
        while storage.__len__() > maxsize:
            storage.popitem(False)

        return result
    return cache_wrapper

class Connect4(udebs.State):
    win_cond = 4

    def hash(self, map_):
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

    def legalMoves(self, map_):
        token = "x" if map_.playerx else "o"
        other = ("o" if token == "x" else "x")

        options = []
        forced = None
        backup = None

        stones = len(map_) - map_.time

        # First yield score of surrender
        yield int(stones / 2)

        for x in range(map_.x):
            y = udebs_config.BOTTOM(map_, x)
            if y is not None:
                loc = (x, y)
                position = token, loc, "drop"

                # First check if we win here.
                win_me = udebs_config.win(map_, token, loc)
                if win_me >= self.win_cond:
                    yield -int((stones + 1) / 2)
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
                            backup = int((stones + 2) / 2)
                            continue

                    # finally these are our only good options
                    options.append((
                        *position,
                        win_me,
                    ))

        if forced:
            yield forced
            return
        elif len(options) == 0:
            yield backup if backup else 0
            return

        huristic = lambda x: (x[3], -abs(((map_.x - 1) / 2) - x[1][0]))
        yield from sorted(options, key=huristic, reverse=True)

    def result(self, alpha=-1, beta=1):
        assert alpha < beta

        if self.value is not None:
            return -int((len(map_) - self.time) / 2)

        map_ = self.getMap().copy()
        map_.playerx = self.getStat("xPlayer", "ACT") >= 2
        map_.time = self.time
        value = self.negamax(alpha, beta, map_)
        if value > beta:
            return beta
        if value < alpha:
            return alpha
        return value

    def substates(self, map_):
        for move in self.legalMoves(map_):
            if not isinstance(move, tuple):
                yield move, move
            else:
                stateNew = map_.copy()
                stateNew.playerx = not map_.playerx
                stateNew[move[1]] = move[0]
                stateNew.time = map_.time + 1
                yield stateNew, move

    @udebs.countrecursion
    @cache
    def negamax(self, alpha, beta, map_):
        for child, e in self.substates(map_):
            if child is e:
                result = -child
            else:
                result = -self.negamax(-beta, -alpha, child)

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
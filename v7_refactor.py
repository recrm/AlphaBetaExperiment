import udebs
import functools
import udebs_config
from collections import OrderedDict

counter = 0
storage = OrderedDict()

def cache(f, maxsize=2**23):
    empty = (-float("inf"), float("inf"))

    @functools.wraps(f)
    def cache_wrapper(self, alpha, beta, map_):
        global counter
        counter +=1
        key = self.hash(map_)

        a_, b_ = storage.get(key, empty)
        if a_ > alpha:
            alpha = a_

        if b_ < beta:
            beta = b_

        if alpha >= beta:
            storage.move_to_end(key)
            return alpha

        result = f(self, alpha, beta, map_)
        if result <= alpha:
            storage[key] = (a_, result)
        elif result >= beta:
            storage[key] = (result, b_)
        else:
            storage[key] = (result, result)

        storage.move_to_end(key)
        if storage.__len__() > maxsize:
            storage.popitem(False)

        return result
    return cache_wrapper

class Connect4(udebs.State):
    win_cond = 4

    @staticmethod
    def hash(map_):
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
        token, other = ("x", "o") if map_.playerx else ("o", "x")
        options = []
        forced = None
        backup = None
        for x in range(map_.x):
            for y in range(map_.y -1, -1, -1):
                if map_[x,y] == "empty":
                    break
            else:
                continue

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
            yield token, forced
        elif len(options) > 0:
            huristic = lambda x: abs(map_.const - x[0])
            for loc in sorted(options, key=huristic):
                yield token, loc
        else:
            yield backup if backup else 0

    def result(self, alpha=-1, beta=1):
        if self.value is not None:
            return -abs(self.value)

        map_ = self.getMap().copy()
        map_.playerx = self.getStat("xPlayer", "ACT") >= 2
        map_.const = (map_.x - 1) / 2

        token = "x" if map_.playerx else "o"
        for x in range(map_.x):
            y = udebs_config.BOTTOM(map_, x)
            if y is not None:
                if udebs_config.win(map_, token, (x,y)) >= self.win_cond:
                    return 1

        return self.negamax(alpha, beta, map_)

    def play_next(self, map_, token, loc):
        new = map_.copy()
        new.playerx = not map_.playerx
        new.const = map_.const
        new[loc] = token
        return new

    @cache
    def negamax(self, alpha, beta, map_):
        current = -float("inf")
        for move in self.legalMoves(map_):
            try:
                token, loc = move
            except TypeError:
                result = -move
            else:
                result = -self.negamax(-beta, -alpha, self.play_next(map_, token, loc))

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

    print("nodes visited", counter)
    print(result)
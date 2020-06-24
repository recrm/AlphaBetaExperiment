import udebs
import functools
import udebs_config
from collections import OrderedDict
import data

special_data = data.results
for i in list(special_data.keys()):
    special_data[tuple(reversed(i))] = special_data[i]

# ~ 2gb of ram
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

        # Upper bound optimization magic
        upper = (map_.scored - 1) // 2
        if b_ > upper:
            b_ = upper
        # end magic

        if b_ < beta:
            beta = b_

        if alpha >= beta:
            if key in storage:
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

    @staticmethod
    def win_huristic(map_, token, loc):
        token = {token, "empty"}
        maxim = 0
        x, y = loc[0], loc[1]
        for x_, y_ in ((1,0), (0,1), (1,1), (1, -1)):
            sto = ["x"]
            for i in (None, None):
                try:
                    cx, cy = x + x_, y + y_
                    while map_[cx, cy] in token:
                        sto.append("_" if map_[cx, cy] == "empty" else "x")
                        cx, cy = cx + x_, cy + y_
                except IndexError:
                    pass

                sto = list(reversed(sto))
                x_ *= -1
                y_ *= -1

            maxim += special_data.get(tuple(sto), 0)

        return maxim

    def legalMoves(self, map_):
        yield map_.scored // 2

        token, other = ("x", "o") if map_.playerx else ("o", "x")
        options = []
        forced = False

        for x in range(map_.x):
            for y in range(map_.y -1, -1, -1):
                if map_[x,y] == "empty":
                    break
            else:
                continue

            loc = (x, y)

            if udebs_config.win(map_, other, loc) >= self.win_cond:
                if forced:
                    return

                options = []
                forced = loc

            if not forced or forced == loc:
                if y > 0 and udebs_config.win(map_, other, (x, y - 1)) >= self.win_cond:
                    # We cannot play here unless it is our only option
                    if forced:
                        return
                else:
                    options.append(loc)

        # Lower bound optimization magic
        if len(options) > 0 and not forced:
            if map_.scored >= 2:
                yield (map_.scored - 2) // 2
        # end magic

        if len(options) > 1:
            huristic = lambda x: (
                -self.win_huristic(map_, token, x),
                abs(map_.const - x[0])
            )
            options = sorted(options, key=huristic)

        for loc in options:
            yield token, loc

    def result(self, alpha=None, beta=None):
        map_ = self.getMap().copy()
        map_.playerx = self.getStat("xPlayer", "ACT") >= 2
        map_.scored = len(map_) - self.time
        map_.const = (map_.x - 1) / 2

        result = None
        if self.value is not None:
            result = -(map_.scored + 1) // 2
        else:
            # We have to check if we are one turn away from victory
            token = "x" if map_.playerx else "o"
            for x in range(map_.x):
                y = udebs_config.BOTTOM(map_, x)
                if y is not None:
                    if udebs_config.win(map_, token, (x,y)) >= self.win_cond:
                        result = (map_.scored + 1) // 2
                        break

        if result:
            if alpha and result < alpha:
                return alpha
            elif beta and result > beta:
                return beta
            return result

        if not beta:
            beta = (map_.scored - 1) // 2
        if not alpha:
            alpha = -beta

        return self.binary_search(alpha, beta, map_)

    def play_next(self, map_, token, loc):
        new = map_.copy()
        new.playerx = not map_.playerx
        new.scored = map_.scored - 1
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

    def binary_search(self, mini, maxi, map_):
        mid = (mini + maxi) // 2

        while mini < maxi:

            lq = (mini + mid + 1) // 2
            lower = self.negamax(lq - 1, lq, map_)
            if lower < lq:
                return self.binary_search(mini, lq - 1, map_)

            mini = lq

            uq = (maxi + mid) // 2
            upper = self.negamax(uq, uq + 1, map_)
            if upper > uq:
                return self.binary_search(uq + 1, maxi, map_)

            maxi = uq

        return mid

if __name__ == "__main__":
    main_map = udebs.battleStart(udebs_config.config, field=Connect4())
    main_map.printMap()

    with udebs.Timer():
        result = main_map.result(-1, 1)

    print("nodes visited", counter)
    print(result)
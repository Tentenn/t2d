import random
import sys

class Generator():
    def __init__(self):
        self.max_effects = 40

    def set_mode(self, mode: int):
        pass

    def _effect_mode_1(self, n):
        # Random number of effects
        effects = []
        for _ in range(n):
            effect_number = random.choice(range(1, self.max_effects))
            effects.append(f"e{effect_number}.svg")
        return effects

    def _effect_mode_2(self, n, r_alt, ):
        effects = []
        effect_numbers = [f"e{e}.svg" for e in random.sample(range(1, self.max_effects), k=r_alt)]
        # print(effect_numbers)
        if r_alt >= n:
            print("ERROR, r_alt same or larger than n, replacing with random")
            for _ in range(n):
                effect_number = random.choice(range(1, self.max_effects))
                effects.append(f"e{effect_number}.svg")
            return effects
        counter = 0
        for _ in range(n):
            effects.append(effect_numbers[counter])
            counter += 1
            if counter == r_alt:
                counter = 0
        return effects

    def _effect_mode_3(self, n, r_alt):
        # Sorted
        effects = []
        effect_numbers = [f"e{e}.svg" for e in random.sample(range(1, self.max_effects), k=r_alt)]
        effect_numbers.sort()
        # print(effect_numbers)
        if r_alt >= n:
            print("ERROR, r_alt same or larger than n, replacing with random")
            for _ in range(n):
                effect_number = random.choice(range(1, self.max_effects))
                effects.append(f"e{effect_number}.svg")
            return effects
        counter = 0
        for _ in range(n):
            effects.append(effect_numbers[counter])
            counter += 1
            if counter == r_alt:
                counter = 0
        effects.sort()
        return effects


    def new_effects(self, textline, mode: int = 2, r_alt: int = 2):
        # @returns: a list of integers corresponding to effects svgs.
        # @param r_alt:
        n = len(textline)
        if mode == 0: # Random
            return self._effect_mode_1(n)
        elif mode == 1: # Alternate
            return self._effect_mode_2(n, r_alt)
        elif mode == 2: # Alternate sorted
            return self._effect_mode_3(n, r_alt)
        else:
            assert False, f"mode {mode} not implemented."

import collections
import random
from typing import List, Tuple

from .game import Game

ODDS = {
    "🍒": 25,
    "🍊": 20,
    "🍉": 20,
    "🍆": 15,
    "💜": 13,
    "💰": 6,
}

THREE_REQUIRED = ["🍆", "💜", "💰"]

EMOTE_POOL = []


def seed():
    for emote, odds in ODDS.items():
        for _ in range(odds):
            EMOTE_POOL.append(emote)


seed()


def get_slots():
    random.shuffle(EMOTE_POOL)
    return random.choices(EMOTE_POOL, k=3)


def get_odds(emote: str, only_two: bool = False):
    probability = ODDS.get(emote)
    odds = 1 / (probability / 100)
    if only_two:
        return odds / 2
    return odds


def calculate_win(slots: List[str]) -> Tuple[List[str], float]:
    counts = collections.Counter(slots)
    for emote, count in counts.items():
        if count == 3:
            return slots, get_odds(emote)
        elif count == 2 and emote not in THREE_REQUIRED:
            return [emote, emote], get_odds(emote, only_two=True)
    return slots, 0


class Slots(Game):
    async def game(self) -> float:
        slots = get_slots()
        combo, odds = calculate_win(slots)
        win = self.amount * odds
        if odds:
            await self.ctx.send(f"{' '.join(slots)}\nNice! You bet {self.amount} and won {win}!")
        else:
            await self.ctx.send(f"{' '.join(slots)}\nOh no. You lost. Good luck next time!")
        return win

    @staticmethod
    def info():
        info = "```py\n"
        for emote, odds in ODDS.items():
            if emote not in THREE_REQUIRED:
                info += f"{emote*2:<5}: {get_odds(emote, only_two=True)}\n"
            info += f"{emote * 3:<5}: {get_odds(emote)}\n"
        return info + "```"

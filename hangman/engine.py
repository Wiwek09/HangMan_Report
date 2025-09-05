import random
import string
import time
from dataclasses import dataclass, field

# ------------------ Word sources ------------------
BASIC_WORDS = [
    "python", "variable", "module", "program", "object", "string",
    "game", "package", "australia", "boolean", "world", "happy", "dictionary",
]

INTERMEDIATE_PHRASES = [
    "open source software",
    "artificial intelligence",
    "once in a blue moon",
    "hangman game",
    "jaw dropping experience",
]

def _mask_char(ch: str) -> bool:
    return ch.lower() in string.ascii_lowercase

@dataclass
class GameState:
    answer: str
    masked: list[str]
    lives: int
    guesses: set[str] = field(default_factory=set)
    won: bool = False
    over: bool = False
    last_action_time: float = field(default_factory=time.time)
    time_limit: int = 15

class HangmanGame:
    """Core Hangman engine with timer and life deduction.
    Designed for unit testing—inject RNG and time provider.
    """
    def __init__(self, level: str = "basic", lives: int = 6, time_limit: int = 15,
                 rng: random.Random | None = None, time_provider=time.time):
        if level not in {"basic", "intermediate"}:
            raise ValueError("level must be 'basic' or 'intermediate'")
        self.level = level
        self.lives = lives
        self.time_limit = time_limit
        self.rng = rng or random.Random()
        self.time = time_provider
        self.state = self._new_state()

    # ----- internal helpers -----
    def _pick_answer(self) -> str:
        if self.level == "basic":
            return self.rng.choice(BASIC_WORDS)
        return self.rng.choice(INTERMEDIATE_PHRASES)

    def _mask(self, answer: str) -> list[str]:
        return [ "_" if _mask_char(ch) else ch for ch in answer ]

    def _new_state(self) -> GameState:
        answer = self._pick_answer()
        return GameState(
            answer=answer,
            masked=self._mask(answer),
            lives=self.lives,
            guesses=set(),
            won=False,
            over=False,
            last_action_time=self.time(),
            time_limit=self.time_limit,
        )

    # ----- properties -----
    @property
    def display(self) -> str:
        return "".join(self.state.masked)

    @property
    def answer(self) -> str:
        return self.state.answer

    @property
    def remaining_lives(self) -> int:
        return self.state.lives

    @property
    def guesses(self) -> set[str]:
        return set(self.state.guesses)

    # ----- game mechanics -----
    def _apply_timeout_if_any(self, now: float | None = None) -> bool:
        """Deduct life if time since last action exceeds time_limit.
        Returns True if a life was deducted."""
        now = self.time() if now is None else now
        if not self.state.over and (now - self.state.last_action_time) >= self.state.time_limit:
            self.deduct_life()
            self.state.last_action_time = now
            return True
        return False

    def tick(self, now: float | None = None) -> bool:
        """Call periodically to apply timeouts when no guess happens."""
        return self._apply_timeout_if_any(now)

    def guess(self, letter: str, now: float | None = None) -> dict:
        if self.state.over:
            return {"status": "over", "display": self.display, "lives": self.remaining_lives}

        # Before processing a guess, check timeout
        self._apply_timeout_if_any(now)

        if self.state.over:
            return {"status": "over", "display": self.display, "lives": self.remaining_lives}

        if not letter or len(letter) != 1 or letter.lower() not in string.ascii_lowercase:
            return {"status": "invalid", "reason": "Enter a single A-Z letter."}

        letter = letter.lower()
        if letter in self.state.guesses:
            # No penalty for repeated guesses
            return {"status": "repeat", "display": self.display, "lives": self.remaining_lives}

        self.state.guesses.add(letter)
        self.state.last_action_time = self.time() if now is None else now

        if letter in self.state.answer.lower():
            # reveal all positions
            for i, ch in enumerate(self.state.answer):
                if _mask_char(ch) and ch.lower() == letter:
                    self.state.masked[i] = ch  # preserve original case
            if "_" not in self.state.masked:
                self._finish(True)
            return {"status": "hit", "display": self.display, "lives": self.remaining_lives}
        else:
            self.deduct_life()
            return {"status": "miss", "display": self.display, "lives": self.remaining_lives}

    def deduct_life(self) -> None:
        """Deduct a life manually (used when timer runs out)."""
        if not self.state.over:
            self.state.lives -= 1
            if self.state.lives <= 0:
                self._finish(False)

    def _finish(self, won: bool) -> None:
        self.state.won = won
        self.state.over = True
        # Reveal the full answer on finish
        self.state.masked = list(self.state.answer)

    def is_over(self) -> bool:
        return self.state.over

    def is_won(self) -> bool:
        return self.state.won

    def reset(self) -> None:
        self.state = self._new_state()

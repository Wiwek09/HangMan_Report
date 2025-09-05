import unittest
import time
from engine import HangmanGame


class TestHangmanGame(unittest.TestCase):

    def setUp(self):
        # fixed seed for reproducibility
        self.rng = __import__("random").Random(42)
        self.game = HangmanGame(level="basic", lives=3, time_limit=2, rng=self.rng, time_provider=time.time)

    def test_initial_state(self):
        self.assertEqual(self.game.remaining_lives, 3)
        self.assertIn("_", self.game.display)
        self.assertFalse(self.game.is_over())

    def test_correct_guess(self):
        word = self.game.answer
        first_letter = word[0]
        result = self.game.guess(first_letter)
        self.assertEqual(result["status"], "hit")
        self.assertIn(first_letter, result["display"])

    def test_incorrect_guess(self):
        result = self.game.guess("z")
        self.assertEqual(result["status"], "miss")
        self.assertEqual(self.game.remaining_lives, 2)

    def test_repeat_guess(self):
        self.game.guess("a")
        result = self.game.guess("a")
        self.assertEqual(result["status"], "repeat")

    def test_invalid_guess(self):
        result = self.game.guess("1")
        self.assertEqual(result["status"], "invalid")

    def test_game_over_on_zero_lives(self):
        self.game.guess("z")
        self.game.guess("y")
        self.game.guess("x")  # should lose all lives
        self.assertTrue(self.game.is_over())
        self.assertFalse(self.game.is_won())

    def test_win_condition(self):
        word = self.game.answer
        for letter in set(word):  # guess all unique letters
            self.game.guess(letter)
        self.assertTrue(self.game.is_won())

    def test_timeout_deducts_life(self):
        now = time.time()
        # simulate timeout by moving time forward
        self.game._apply_timeout_if_any(now + 3)
        self.assertEqual(self.game.remaining_lives, 2)

    def test_reset_game(self):
        old_answer = self.game.answer
        self.game.reset()
        self.assertNotEqual(old_answer, self.game.answer)
        self.assertEqual(self.game.remaining_lives, 3)
        self.assertIn("_", self.game.display)


if __name__ == "__main__":
    unittest.main()

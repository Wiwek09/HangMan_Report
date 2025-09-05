import sys
import threading
import queue
import time
from engine import HangmanGame

def _input_thread(q: queue.Queue):
    try:
        q.put(sys.stdin.readline().strip())
    except Exception as e:
        q.put(None)

def get_input_with_timeout(prompt: str, timeout: int) -> str | None:
    """Read a line with a timeout. Shows a live countdown."""
    print(prompt, end="", flush=True)
    q = queue.Queue()
    t = threading.Thread(target=_input_thread, args=(q,), daemon=True)
    t.start()
    start = time.time()
    remaining = timeout
    while t.is_alive():
        t.join(timeout=1)
        elapsed = int(time.time() - start)
        remaining = max(0, timeout - elapsed)
        print(f"\rTime left: {remaining:2d}s  Enter a letter: ", end="", flush=True)
        if remaining == 0 and t.is_alive():
            return None
    try:
        return q.get_nowait()
    except queue.Empty:
        return None

def run(level: str = "basic") -> None:
    game = HangmanGame(level=level, lives=6, time_limit=15)
    print("\n=== Hangman ===")
    print(f"Level: {level.title()}  Lives: {game.remaining_lives}\n")
    while not game.is_over():
        print("Word:", game.display)
        user_input = get_input_with_timeout("Enter a letter: ", game.state.time_limit)
        if user_input is None or user_input == "":
            # timeout or blank -> will deduct via tick
            game.tick()
            if not game.is_over():
                print("\nTime's up! Life deducted. Lives:", game.remaining_lives)
            continue
        if user_input.lower() == "quit":
            print("\nQuitting...")
            break
        result = game.guess(user_input)
        if result.get("status") == "invalid":
            print("Invalid input. Enter a single A-Z letter.\n")
        elif result["status"] == "repeat":
            print("Already guessed. No penalty.\n")
        elif result["status"] == "miss":
            print("Wrong! Lives:", result["lives"],"\n")
        elif result["status"] == "hit":
            print("Good guess!\n")
    # game over
    if game.is_won():
        print("\nYou won! The answer was:", game.answer)
    else:
        print("\nGame over. The answer was:", game.answer)

if __name__ == "__main__":
    level = sys.argv[1] if len(sys.argv) > 1 else "basic"
    run(level)

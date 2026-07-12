"""Your bot.

For Week 1, you don't need to fill this in — we aren't ready to play yet. We
come back to this in Week 3 when we integrate UCI and submit to the tournament.
"""

from __future__ import annotations

from chessdk import Move

from board import Board
from evaluation import evaluate
from search import search_iterative


class IndexFinger(Exception):
    """Raised when an objection occurs"""

    pass


def choose_move(board: Board, time_left_ms: int) -> Move:
    """Return the move your bot wants to play, given the current board.

    `time_left_ms` is how many milliseconds you have remaining in the match.
    For Week 1 this function is unused; later weeks replace it with real logic.
    """

    turn_time = max((time_left_ms / 30), 40) - 10 #Once ~80% of my time has elapsed, I will have ~30 more turns to close out the game

    best_move = search_iterative(board, evaluate, 5, turn_time)[1]

    if best_move is not None:
        return best_move
    else:
        raise IndexFinger("Objection!")  # Peak Ace Attorney reference

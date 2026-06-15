"""Your bot.

For Week 1, you don't need to fill this in — we aren't ready to play yet. We
come back to this in Week 3 when we integrate UCI and submit to the tournament.
"""

from __future__ import annotations

from chessdk import Move

from board import Board
from evaluation import evaluate


def choose_move(board: Board, time_left_ms: int) -> Move:
    """Return the move your bot wants to play, given the current board.

    `time_left_ms` is how many milliseconds you have remaining in the match.
    For Week 1 this function is unused; later weeks replace it with real logic.
    """

    moves = board.legal_moves()
    for i, m in enumerate(board.legal_moves()):
        board.make_move(m)
        moves[i] = evaluate(board)
        board.undo_move()

    return board.legal_moves()[moves.index(max(moves))]

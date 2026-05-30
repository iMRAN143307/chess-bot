"""Your bot.

For Week 1, you don't need to fill this in — we aren't ready to play yet. We
come back to this in Week 3 when we integrate UCI and submit to the tournament.
"""

from __future__ import annotations

from random import choice

from chessdk import Move, min_attacker_value
from chessdk.evaluation import PIECE_VALUE

from board import Board


def choose_move(board: Board, time_left_ms: int) -> Move:
    """Return the move your bot wants to play, given the current board.

    `time_left_ms` is how many milliseconds you have remaining in the match.
    For Week 1 this function is unused; later weeks replace it with real logic.
    """

    def score(m: Move):
        pre_score = PIECE_VALUE[board.piece_at(m.to_sq).kind]
        board.make_move(m)
        if board.is_attacked(m.to_sq, board.state.side_to_move):
            min_val = (
                min_attacker_value(board, m.to_sq, board.state.side_to_move)
                if min_attacker_value(board, m.to_sq, board.state.side_to_move)
                is not None
                else 2001
            )
            if min_val < PIECE_VALUE[board.piece_at(m.to_sq).kind]:
                pre_score = pre_score - PIECE_VALUE[board.piece_at(m.to_sq).kind]
        board.undo_move()
        return pre_score

    moves = board.legal_moves()
    captures = [m for m in moves if board.piece_at(m.to_sq) is not None]
    if captures:
        scored_captures = [score(m) for m in captures]
        return captures[scored_captures.index(max(scored_captures))]
    else:
        return choice(moves)

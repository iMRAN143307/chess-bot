from chessdk import (
    Move,
    Color,
    parse_fen
)

from board import Board

def test_black_is_checkmated_evaluates_strongly_positive():
    """Black is back-rank mated; White has just won, so the eval should be
    enormous and positive (centipawns far above any material imbalance)."""
    # White rook on a8 delivers mate; Black king on g8 has nowhere to go.
    fen = "R5k1/5ppp/8/8/8/8/8/6K1 b - - 1 1"
    board = Board.from_fen(fen)
    score = evaluate(board)
    assert score >= 100_000, (
        f"expected a mate-magnitude positive score, got {score}"
    )

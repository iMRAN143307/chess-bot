"""Your evaluation function.

``evaluate(board)`` returns a centipawn score for the given position, from
White's point of view: positive means White is winning, negative means
Black is winning, zero means the position is even. Your bot calls this
function from ``bot.py`` to compare candidate moves; Phase 5's search code
will call it at the leaves of its lookahead tree.

Phase 4 builds this up incrementally: material counting, piece-square
tables, mobility, and any extra features you want to add for personality.
The kit ships canonical starting values for piece values and PSTs in
``chessdk`` that you may import and tune.
"""

from __future__ import annotations

from chessdk import (
    BISHOP,
    BISHOP_DIRECTIONS,
    BLACK,
    KING,
    KING_OFFSETS,
    KNIGHT,
    KNIGHT_OFFSETS,
    PAWN,
    QUEEN,
    QUEEN_DIRECTIONS,
    ROOK,
    ROOK_DIRECTIONS,
    WHITE,
    CastlingRights,
    Color,
    Kind,
    Move,
    MoveRecord,
    Piece,
    file_of,
    on_board,
    rank_of,
    sq,
    parse_square
)

from board import Board

def evaluate(board: Board) -> int:
    """Return a centipawn score for the position from White's point of view."""
    score = 0

    if board.legal_moves() == [] and board.side_to_move == Color.BLACK and board.is_in_check(Color.BLACK):
        score += 1_000_000
        return score
    if board.legal_moves() == [] and board.side_to_move == Color.WHITE and board.is_in_check(Color.WHITE):
        score -= 1_000_000
        return score

    for piece in board.pieces:
        if piece != None:
            if piece.color == Color.BLACK:
                pass
            if piece.color == Color.WHITE:
                pass

    return score

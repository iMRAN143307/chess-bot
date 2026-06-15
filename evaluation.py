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
    parse_square,
    pst_square,
    rank_of,
    sq,
)

from board import Board


def evaluate(board: Board) -> int:
    """Return a centipawn score for the position from White's point of view."""
    score = 0
    w_bishops = 0
    b_bishops = 0

    if (
        board.legal_moves() == []
        and board.side_to_move == Color.BLACK
        and board.is_in_check(Color.BLACK)
    ):
        score += 1_000_000
        return score
    if (
        board.legal_moves() == []
        and board.side_to_move == Color.WHITE
        and board.is_in_check(Color.WHITE)
    ):
        score -= 1_000_000
        return score
    if (
        board.legal_moves() == []
        and not board.is_in_check(Color.WHITE)
        and not board.is_in_check(Color.BLACK)
    ):
        score = 0
        return score

    for i, piece in enumerate(board.pieces):
        if piece is not None:
            if piece.color == Color.BLACK:
                if piece.kind == Kind.PAWN:
                    score -= 100
                    score -= pst_square(Kind.PAWN, Color.BLACK, i)
                elif piece.kind == Kind.BISHOP:
                    score -= 325
                    b_bishops += 1
                    score -= pst_square(Kind.BISHOP, Color.BLACK, i)
                elif piece.kind == Kind.KNIGHT:
                    score -= 325
                    score -= pst_square(Kind.KNIGHT, Color.BLACK, i)
                elif piece.kind == Kind.ROOK:
                    score -= 500
                    score -= pst_square(Kind.ROOK, Color.BLACK, i)
                elif piece.kind == Kind.QUEEN:
                    score -= 975
                    score -= pst_square(Kind.QUEEN, Color.BLACK, i)
                elif piece.kind == Kind.KING:
                    score -= pst_square(Kind.KING, Color.BLACK, i)
            if piece.color == Color.WHITE:
                if piece.kind == Kind.PAWN:
                    score += 100
                    score += pst_square(Kind.PAWN, Color.WHITE, i)
                elif piece.kind == Kind.BISHOP:
                    score += 325
                    w_bishops += 1
                    score += pst_square(Kind.BISHOP, Color.WHITE, i)
                elif piece.kind == Kind.KNIGHT:
                    score += 325
                    score += pst_square(Kind.KNIGHT, Color.WHITE, i)
                elif piece.kind == Kind.ROOK:
                    score += 500
                    score += pst_square(Kind.ROOK, Color.WHITE, i)
                elif piece.kind == Kind.QUEEN:
                    score += 975
                    score += pst_square(Kind.QUEEN, Color.WHITE, i)
                elif piece.kind == Kind.KING:
                    score += pst_square(Kind.KING, Color.WHITE, i)

    if b_bishops > 1:
        score -= 50
    if w_bishops > 1:
        score += 50

    return score

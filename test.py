"""Stage 23: quiescence resolves captures before the evaluator weighs in.

Using a material-only evaluator (so only the search is under test), we check:

  - In a quiet position with no captures available, quiescence returns the
    plain static score (the stand-pat baseline).
  - After a poisoned capture (a piece grabs a defended pawn), quiescence
    sees the recapture and scores the position near its true, bad value,
    well below the naive static count.
  - When a free capture is on offer, quiescence takes it and reflects the
    gain.
  - A depth-one search given a quiescent leaf evaluator declines the
    poisoned capture instead of walking into it.
  - On a six-ply forced exchange (the handout's worked example), a plain
    depth-3 search halts mid-chain a pawn up while the same search with a
    quiescent leaf resolves the exchange to level.
"""

from __future__ import annotations

from board import Board
from chessdk import PIECE_VALUE_CLASSIC, PIECE_VALUE_KAUFMAN, MATE_SCORE, WHITE, Color, Move


def order_moves(board: Board, moves: list[Move]) -> list[Move]:
    """Return ``moves`` sorted to put likely-strong moves first."""
    if moves != []:
        move_value_dict = dict()
        for move_obj in moves:
            move_value_dict[move_obj] = 0
            to_piece = board.pieces[move_obj.to_sq]
            from_piece = board.pieces[move_obj.from_sq]
            if to_piece is not None and from_piece is not None:
                move_value_dict[move_obj] += PIECE_VALUE_KAUFMAN[to_piece.kind]
                move_value_dict[move_obj] -= PIECE_VALUE_KAUFMAN[from_piece.kind] / 100
        sorted_move_value_dict = [
            k
            for k, v in sorted(
                move_value_dict.items(), key=lambda item: item[1], reverse=True
            )
        ]
        moves = sorted_move_value_dict

    return moves


def search(
    board: Board,
    depth: int,
    eval_fn,
    alpha: int = -1_000_000,
    beta: int = 1_000_000,
    preset_best = (0, None)
) -> tuple[int, Move | None]:
    """Return ``(best_score_for_position, best_move)`` after searching to
    the given depth."""

    legal = board.legal_moves()
    if board.side_to_move == Color.BLACK:
        best_move = (1_000_000, None)
    else:
        best_move = (-1_000_000, None)

    if (
        legal == []
        and board.side_to_move == Color.BLACK
        and board.is_in_check(Color.BLACK)
    ):
        return (1_000_000, None)
    if (
        legal == []
        and board.side_to_move == Color.WHITE
        and board.is_in_check(Color.WHITE)
    ):
        return (-1_000_000, None)
    if (
        legal == []
        and not board.is_in_check(Color.WHITE)
        and not board.is_in_check(Color.BLACK)
    ):
        return (0, None)
    if depth == 0:
        try:
            return (eval_fn(board, legal), None)
        except TypeError:
            return (eval_fn(board), None)
    legal = order_moves(board, legal)
    if preset_best[1] is not None:
        legal.insert(0, preset_best[1])
    for move in legal:
        board.make_move(move)
        if board.side_to_move == Color.BLACK:
            new_move = search(board, depth - 1, eval_fn, alpha, beta)
            alpha = max(alpha, new_move[0])
            if new_move[0] > 900_000:
                new_move = (new_move[0] - 1, move)
            elif new_move[0] < -900_000:
                new_move = (new_move[0] + 1, move)
            else:
                new_move = (new_move[0], move)
            best_move = [best_move, new_move]
            best_move = best_move[
                [move[0] for move in best_move].index(
                    max([move[0] for move in best_move])
                )
            ]
        else:
            new_move = search(board, depth - 1, eval_fn, alpha, beta)
            beta = min(beta, new_move[0])
            if new_move[0] > 900_000:
                new_move = (new_move[0] - 1, move)
            elif new_move[0] < -900_000:
                new_move = (new_move[0] + 1, move)
            else:
                new_move = (new_move[0], move)
            best_move = [best_move, new_move]
            best_move = best_move[
                [move[0] for move in best_move].index(
                    min([move[0] for move in best_move])
                )
            ]
        board.undo_move()
        if alpha >= beta:
            return best_move

    return best_move

def quiesce(board, alpha, beta, eval_fn):
    score = eval_fn(board)
    legal = board.legal_moves()

    if (
        legal == []
        and board.side_to_move == Color.BLACK
        and board.is_in_check(Color.BLACK)
    ):
        return 1_000_000
    if (
        legal == []
        and board.side_to_move == Color.WHITE
        and board.is_in_check(Color.WHITE)
    ):
        return -1_000_000
    if (
        legal == []
        and not board.is_in_check(Color.WHITE)
        and not board.is_in_check(Color.BLACK)
    ):
        return 0

    if board.side_to_move == Color.WHITE:
        if score >= beta:
            return score
        elif score > alpha:
            alpha = score
            for capture in [m for m in legal if board.piece_at(m.to_sq) is not None]:
                board.make_move(capture)
                score = quiesce(board, alpha, beta, eval_fn)
                if score > 100:
                    print(score)
                    print(capture)
                alpha = max(alpha, score)
                board.undo_move()
                if alpha >= beta:
                    break
    elif board.side_to_move == Color.BLACK:
        if score <= alpha:
            return score
        elif score < beta:
            beta = score
            for capture in [m for m in legal if board.piece_at(m.to_sq) is not None]:
                board.make_move(capture)
                score = quiesce(board, alpha, beta, eval_fn)
                if score > 100:
                    print(score)
                    print(capture)
                beta = min(beta, score)
                board.undo_move()
                if beta <= alpha:
                    break

    return score



def _material(board) -> int:
    total = 0
    for piece in board.pieces:
        if piece is None:
            continue
        sign = 1 if piece.color == WHITE else -1
        total += sign * PIECE_VALUE_CLASSIC[piece.kind]
    return total

# A six-ply forced exchange on e5 (the handout's worked example): White's
# d4 pawn, Nf3 and Re1 contest the e5 pawn, which Black's d6 pawn, Nc6, Bg7
# and Re8 defend. If both sides keep capturing (1.dxe5 dxe5 2.Nxe5 Nxe5
# 3.Rxe5 Bxe5) the material swings +1, 0, +1, -2, +1, -4: every odd ply
# reads "White up a pawn" and every even ply reads level, so a fixed-depth
# search oscillates as it deepens and never settles until the captures
# resolve.
DEEP_EXCHANGE = "4r1k1/ppp2pbp/2np4/4p3/3P4/5N2/PPP2PPP/2B1R1K1 w - - 0 1"

def quiescent_eval(b):
    return quiesce(b, -MATE_SCORE, MATE_SCORE, _material)

"""A six-ply forced exchange: a depth-3 search stops mid-chain (just
after 2.Nxe5) and reads White up a pawn; quiescence plays the captures
out and sees the exchange is level."""

plain, _ = search(Board.from_fen(DEEP_EXCHANGE), 3, _material)
quiesced, _ = search(Board.from_fen(DEEP_EXCHANGE), 3, quiescent_eval)
assert plain == 100, (
    f"a plain depth-3 search halts just after 2.Nxe5 and should read "
    f"exactly a pawn up (+100); got {plain}"
)
assert quiesced == 0, (
    f"with a quiescent leaf the same search resolves the exchange to "
    f"level (0); got {quiesced}"
)
assert quiesced < plain

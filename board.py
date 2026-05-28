"""Your Board class.

This file lives in your own working directory after `chess-cli init`. Edit it
freely. Tests (`chess-cli test`) import `Board` from this file; the UCI
wrapper in later weeks will import your `choose_move` from `bot.py`, which
will in turn use this `Board`.

Square layout: indices 0..63, with 0 = a1 and 63 = h8. See
`chessdk.squares` for helpers (`sq(file, rank)`, `file_of(sq)`, etc.) and
offset constants (`KNIGHT_OFFSETS`, `BISHOP_DIRECTIONS`, etc.).
"""

from __future__ import annotations

import copy

# WE ARE IMPORTING FROM THE FUTURE!!!
from typing import Iterator

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
)
from chessdk.base import BaseBoard


class Board(BaseBoard):
    """A chess board with move generation. You implement the methods below."""

    def __init__(self, state=None):
        super().__init__(state)
        self._history = []

    # === Stage 1: Squares and Pieces ===

    def piece_at(self, square: int) -> Piece | None:
        """Return the Piece on the given square, or None if empty."""
        if not on_board(file_of(square), rank_of(square)):
            return None
        return self.pieces[square]

    def pieces_of(
        self, color: Color, kind: Kind | None = None
    ) -> Iterator[tuple[int, Piece]]:
        """Yield (square, piece) pairs for every piece of the given color."""
        for square, piece in enumerate(self.pieces):
            if piece and piece.color == color:
                if (kind is None) or piece.kind == kind:
                    yield (square, piece)

    # === Stage 2: Leapers ===

    def _leaper_moves(self, color: Color, piece, offsets) -> list[Move]:
        moves = []
        for square, _ in self.pieces_of(color, piece):
            for df, dr in offsets:
                target_file, target_rank = file_of(square) + df, rank_of(square) + dr
                target_square = sq(target_file, target_rank)
                if on_board(target_file, target_rank) and (
                    self.piece_at(target_square) is None
                    or self.piece_at(target_square).color != color
                ):
                    moves.append(Move(square, target_square))
        return moves

    def _knight_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal knight moves for `color`."""
        moves = self._leaper_moves(color, KNIGHT, KNIGHT_OFFSETS)
        return moves

    def _king_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal king moves for `color`. (No castling yet.)"""
        moves = self._leaper_moves(color, KING, KING_OFFSETS)
        return moves

    # === Stage 3: Sliders ===

    def _slider_moves(self, color: Color, piece, offsets) -> list[Move]:
        moves = []
        cont = 0
        for square, _ in self.pieces_of(color, piece):
            for df, dr in offsets:
                cont = 1
                target_file, target_rank = file_of(square), rank_of(square)
                target_square = sq(target_file, target_rank)
                while cont == 1:
                    target_file, target_rank = target_file + df, target_rank + dr
                    target_square = sq(target_file, target_rank)
                    if on_board(target_file, target_rank) and (
                        self.piece_at(target_square) is None
                    ):
                        moves.append(Move(square, target_square))
                    elif on_board(target_file, target_rank) and (
                        self.piece_at(target_square).color != color
                    ):
                        moves.append(Move(square, target_square))
                        cont = 0
                    else:
                        cont = 0
        return moves

    def _bishop_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal bishop moves for `color`."""
        moves = self._slider_moves(color, BISHOP, BISHOP_DIRECTIONS)
        return moves

    def _rook_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal rook moves for `color`."""
        moves = self._slider_moves(color, ROOK, ROOK_DIRECTIONS)
        return moves

    def _queen_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal queen moves for `color`."""
        moves = self._slider_moves(color, QUEEN, QUEEN_DIRECTIONS)
        return moves

    # === Stage 4: Pawns ===

    def _pawn_moves(self, color: Color) -> list[Move]:
        """Pseudo-legal pawn moves for `color`."""
        moves = []

        for square, _ in self.pieces_of(color, PAWN):
            if color == WHITE:
                target_file, target_rank = file_of(square) + 0, rank_of(square) + 1
                target_square = sq(target_file, target_rank)
                if on_board(target_file, target_rank) and (
                    self.piece_at(target_square) is None
                ):
                    moves.append(Move(square, target_square))
                target_file, target_rank = file_of(square) + 1, rank_of(square) + 1
                target_square = sq(target_file, target_rank)
                if on_board(target_file, target_rank) and (
                    self.piece_at(target_square) is not None
                ):
                    if self.piece_at(target_square).color != color:
                        moves.append(Move(square, target_square))
                target_file, target_rank = file_of(square) - 1, rank_of(square) + 1
                target_square = sq(target_file, target_rank)
                if on_board(target_file, target_rank) and (
                    self.piece_at(target_square) is not None
                ):
                    if self.piece_at(target_square).color != color:
                        moves.append(Move(square, target_square))
                target_file, target_rank = file_of(square) + 0, rank_of(square) + 2
                target_square = sq(target_file, target_rank)
                if (
                    on_board(target_file, target_rank)
                    and (self.piece_at(target_square) is None)
                    and (self.piece_at(target_square - 8) is None)
                ):
                    if target_rank == 3:
                        moves.append(Move(square, target_square))
                for offsets in [(1, 1), (-1, 1)]:
                    target_file, target_rank = (
                        file_of(square) + offsets[0],
                        rank_of(square) + offsets[1],
                    )
                    target_square = sq(target_file, target_rank)
                    if self.state.en_passant == target_square:
                        moves.append(Move(square, target_square))
            if color == BLACK:
                target_file, target_rank = file_of(square) + 0, rank_of(square) - 1
                target_square = sq(target_file, target_rank)
                if on_board(target_file, target_rank) and (
                    self.piece_at(target_square) is None
                ):
                    moves.append(Move(square, target_square))
                target_file, target_rank = file_of(square) + 1, rank_of(square) - 1
                target_square = sq(target_file, target_rank)
                if on_board(target_file, target_rank) and (
                    self.piece_at(target_square) is not None
                ):
                    if self.piece_at(target_square).color != color:
                        moves.append(Move(square, target_square))
                target_file, target_rank = file_of(square) - 1, rank_of(square) - 1
                target_square = sq(target_file, target_rank)
                if on_board(target_file, target_rank) and (
                    self.piece_at(target_square) is not None
                ):
                    if self.piece_at(target_square).color != color:
                        moves.append(Move(square, target_square))
                target_file, target_rank = file_of(square) + 0, rank_of(square) - 2
                target_square = sq(target_file, target_rank)
                if (
                    on_board(target_file, target_rank)
                    and (self.piece_at(target_square) is None)
                    and (self.piece_at(target_square - 8) is None)
                ):
                    if target_rank == 4:
                        moves.append(Move(square, target_square))
                for offsets in [(1, -1), (-1, -1)]:
                    target_file, target_rank = (
                        file_of(square) + offsets[0],
                        rank_of(square) + offsets[1],
                    )
                    target_square = sq(target_file, target_rank)
                    if self.state.en_passant == target_square:
                        moves.append(Move(square, target_square))
        promo = []
        to_rm = []
        for m in moves:
            if (
                rank_of(m.to_sq) == 0
                and self.side_to_move == Color.BLACK
                and not m.promotion
            ):
                promo.append(Move(m.from_sq, m.to_sq, Kind.KNIGHT))
                promo.append(Move(m.from_sq, m.to_sq, Kind.BISHOP))
                promo.append(Move(m.from_sq, m.to_sq, Kind.ROOK))
                promo.append(Move(m.from_sq, m.to_sq, Kind.QUEEN))
                to_rm.append(m)
            elif (
                rank_of(m.to_sq) == 7
                and self.side_to_move == Color.WHITE
                and not m.promotion
            ):
                promo.append(Move(m.from_sq, m.to_sq, Kind.KNIGHT))
                promo.append(Move(m.from_sq, m.to_sq, Kind.BISHOP))
                promo.append(Move(m.from_sq, m.to_sq, Kind.ROOK))
                promo.append(Move(m.from_sq, m.to_sq, Kind.QUEEN))
                to_rm.append(m)
        if promo != []:
            moves.extend(promo)
        if to_rm != []:
            for move_obj in to_rm:
                moves.remove(move_obj)
        return moves

    # === Wiring ===

    def pseudo_legal_moves(self) -> list[Move]:
        """All pseudo-legal moves for the side to move."""
        moves = []
        color = self.side_to_move
        moves.extend(self._pawn_moves(color))
        moves.extend(self._queen_moves(color))
        moves.extend(self._rook_moves(color))
        moves.extend(self._bishop_moves(color))
        moves.extend(self._king_moves(color))
        moves.extend(self._knight_moves(color))

        return moves

    def make_move(self, move: Move) -> None:
        halfmove = self.state.halfmove_clock
        if (
            self.piece_at(move.to_sq) is not None
            or self.pieces[move.from_sq].kind == Kind.PAWN
        ):
            halfmove = 0
        else:
            halfmove += 1
        MR = MoveRecord(
            move,
            self.piece_at(move.to_sq),
            move.to_sq,
            self.state.castling.copy(),
            self.state.en_passant,
            self.state.halfmove_clock,
        )
        self.state.halfmove_clock = halfmove
        if self.pieces[move.from_sq].kind == Kind.KING and (
            move.from_sq == move.to_sq + 2 or move.from_sq == move.to_sq - 2
        ):
            if move.to_sq == 2:
                self.pieces[3] = copy.deepcopy(self.pieces[0])
                self.pieces[0] = None
            elif move.to_sq == 6:
                self.pieces[5] = copy.deepcopy(self.pieces[7])
                self.pieces[7] = None
            elif move.to_sq == 58:
                self.pieces[59] = copy.deepcopy(self.pieces[56])
                self.pieces[56] = None
            elif move.to_sq == 62:
                self.pieces[61] = copy.deepcopy(self.pieces[63])
                self.pieces[63] = None
        self.pieces[move.to_sq] = copy.deepcopy(self.pieces[move.from_sq])
        self.pieces[move.from_sq] = None
        if self.state.side_to_move == Color.BLACK:
            self.state.fullmove_number += 1
        self.state.side_to_move = self.state.side_to_move.other
        self._history.append(MR)
        if move.to_sq == self.state.en_passant:
            if self.state.side_to_move.other == Color.WHITE:
                self.pieces[move.to_sq - 8] = None
            else:
                self.pieces[move.to_sq + 8] = None
        if self.pieces[move.to_sq].kind == Kind.PAWN:
            if (
                self.state.side_to_move.other == Color.WHITE
                and move.from_sq + 16 == move.to_sq
            ):
                self.state.en_passant = move.from_sq + 8
            elif (
                self.state.side_to_move.other == Color.BLACK
                and move.from_sq - 16 == move.to_sq
            ):
                self.state.en_passant = move.from_sq - 8
        else:
            self.state.en_passant = None
        piece_promoted_to = move.promotion
        if self.pieces[move.to_sq].kind == Kind.PAWN:
            if (
                rank_of(move.to_sq) == 7
                and self.state.side_to_move.other == Color.WHITE
            ):
                self.pieces[move.to_sq] = Piece(
                    piece_promoted_to, self.state.side_to_move.other
                )
            elif (
                rank_of(move.to_sq) == 0
                and self.state.side_to_move.other == Color.BLACK
            ):
                self.pieces[move.to_sq] = Piece(
                    piece_promoted_to, self.state.side_to_move.other
                )

        if not self.pieces[7]:
            self.state.castling.white_kingside = False
        elif (
            not self.pieces[7].color == Color.WHITE
            or not self.pieces[7].kind == Kind.ROOK
        ):
            self.state.castling.white_kingside = False
        if not self.pieces[0]:
            self.state.castling.white_queenside = False
        elif (
            not self.pieces[0].color == Color.WHITE
            or not self.pieces[0].kind == Kind.ROOK
        ):
            self.state.castling.white_queenside = False
        if not self.pieces[4]:
            self.state.castling.white_kingside = False
            self.state.castling.white_queenside = False
        elif (
            not self.pieces[4].color == Color.WHITE
            or not self.pieces[4].kind == Kind.KING
        ):
            self.state.castling.white_kingside = False
            self.state.castling.white_queenside = False
        if not self.pieces[63]:
            self.state.castling.black_kingside = False
        elif (
            not self.pieces[63].color == Color.BLACK
            or not self.pieces[63].kind == Kind.ROOK
        ):
            self.state.castling.black_kingside = False
        if not self.pieces[56]:
            self.state.castling.black_queenside = False
        elif (
            not self.pieces[56].color == Color.BLACK
            or not self.pieces[56].kind == Kind.ROOK
        ):
            self.state.castling.black_queenside = False
        if not self.pieces[60]:
            self.state.castling.black_kingside = False
            self.state.castling.black_queenside = False
        elif (
            not self.pieces[60].color == Color.BLACK
            or not self.pieces[60].kind == Kind.KING
        ):
            self.state.castling.black_kingside = False
            self.state.castling.black_queenside = False

    def undo_move(self) -> None:
        mr = self._history.pop()
        if self.pieces[mr.move.to_sq].kind == Kind.KING and (
            mr.move.from_sq == mr.move.to_sq + 2 or mr.move.from_sq == mr.move.to_sq - 2
        ):
            if mr.move.to_sq == 2:
                self.pieces[0] = copy.deepcopy(self.pieces[3])
                self.pieces[3] = None
            elif mr.move.to_sq == 6:
                self.pieces[7] = copy.deepcopy(self.pieces[5])
                self.pieces[5] = None
            elif mr.move.to_sq == 58:
                self.pieces[56] = copy.deepcopy(self.pieces[59])
                self.pieces[59] = None
            elif mr.move.to_sq == 62:
                self.pieces[63] = copy.deepcopy(self.pieces[61])
                self.pieces[61] = None
        self.pieces[mr.move.from_sq] = copy.deepcopy(self.pieces[mr.move.to_sq])
        self.pieces[mr.captured_square] = mr.captured
        self.state.halfmove_clock = mr.prev_halfmove
        if self.state.side_to_move == Color.WHITE:
            self.state.fullmove_number -= 1
        self.state.side_to_move = self.state.side_to_move.other
        self.state.castling = mr.prev_castling
        if mr.move.promotion:
            self.pieces[mr.move.from_sq] = Piece(Kind.PAWN, self.state.side_to_move)
        self.state.en_passant = mr.prev_en_passant
        if (self.state.en_passant == mr.move.to_sq) and self.pieces[mr.move.from_sq].kind == Kind.PAWN:
            if self.state.side_to_move == Color.WHITE:
                self.pieces[mr.move.to_sq - 8] = Piece(
                    Kind.PAWN, self.state.side_to_move.other
                )
            else:
                self.pieces[mr.move.to_sq + 8] = Piece(
                    Kind.PAWN, self.state.side_to_move.other
                )

    def is_attacked(self, square: int, by_color: Color) -> bool:
        # True if any piece of 'by_color' attacks 'square'.
        def leaper_attacking_square(self, offsets, square, color, piece_kind):
            for df, dr in offsets:
                target_file, target_rank = file_of(square) + df, rank_of(square) + dr
                target_square = sq(target_file, target_rank)
                if on_board(target_file, target_rank):
                    if self.piece_at(target_square) is not None:
                        if self.piece_at(target_square).color == color:
                            if self.piece_at(target_square).kind == piece_kind:
                                return True
            return False

        def slider_attacking_square(self, offsets, square, color, piece_type):
            for df, dr in offsets:
                cont = 1
                target_file, target_rank = file_of(square), rank_of(square)
                target_square = sq(target_file, target_rank)
                while cont == 1:
                    target_file, target_rank = target_file + df, target_rank + dr
                    target_square = sq(target_file, target_rank)
                    if on_board(target_file, target_rank) and (
                        self.piece_at(target_square) is None
                    ):
                        pass
                    elif on_board(target_file, target_rank) and (
                        self.piece_at(target_square).color == color
                    ):
                        if self.piece_at(target_square).kind == piece_type:
                            return True
                        else:
                            cont = 0
                    else:
                        cont = 0
            return False

        def pawn_attacking_square(self, square, color, piece_type):
            if self.piece_at(square - 7) is not None:
                if (
                    self.piece_at(square - 7).color == WHITE
                    and self.piece_at(square - 7).color == color
                    and self.piece_at(square - 7).kind == piece_type
                ):
                    return True
            if self.piece_at(square - 9) is not None:
                if (
                    self.piece_at(square - 9).color == WHITE
                    and self.piece_at(square - 9).color == color
                    and self.piece_at(square - 9).kind == piece_type
                ):
                    return True
            if self.piece_at(square + 7) is not None:
                if (
                    self.piece_at(square + 7).color == BLACK
                    and self.piece_at(square + 7).color == color
                    and self.piece_at(square + 7).kind == piece_type
                ):
                    return True
            if self.piece_at(square + 9) is not None:
                if (
                    self.piece_at(square + 9).color == BLACK
                    and self.piece_at(square + 9).color == color
                    and self.piece_at(square + 9).kind == piece_type
                ):
                    return True
            return False

        if leaper_attacking_square(self, KNIGHT_OFFSETS, square, by_color, KNIGHT):
            return True
        if leaper_attacking_square(self, KING_OFFSETS, square, by_color, KING):
            return True
        if slider_attacking_square(self, BISHOP_DIRECTIONS, square, by_color, BISHOP):
            return True
        if slider_attacking_square(self, ROOK_DIRECTIONS, square, by_color, ROOK):
            return True
        if slider_attacking_square(self, QUEEN_DIRECTIONS, square, by_color, QUEEN):
            return True
        if pawn_attacking_square(self, square, by_color, PAWN):
            return True
        else:
            return False

    def is_in_check(self, color: Color | None = None) -> bool:
        if color is None:
            color = self.side_to_move
        square = next(self.pieces_of(color, KING), [404])[0]
        if square != 404:
            if self.is_attacked(square, color.other):
                return True
            else:
                return False
        else:
            return False

    def castling_moves(self, color: Color | None = None):
        moves = []
        CastlingRights.white_kingside = self.state.castling.white_kingside
        CastlingRights.white_queenside = self.state.castling.white_queenside
        CastlingRights.black_kingside = self.state.castling.black_kingside
        CastlingRights.black_queenside = self.state.castling.black_queenside
        if color is None:
            color = self.side_to_move
        if color == WHITE:
            if CastlingRights.white_kingside:
                if self.piece_at(5) is None and self.piece_at(6) is None:
                    if not self.is_in_check():
                        if not self.is_attacked(
                            5, color.other
                        ) and not self.is_attacked(6, color.other):
                            moves.append(Move(4, 6))
            if CastlingRights.white_queenside:
                if (
                    self.piece_at(2) is None
                    and self.piece_at(3) is None
                    and self.piece_at(1) is None
                ):
                    if not self.is_in_check():
                        if not self.is_attacked(
                            2, color.other
                        ) and not self.is_attacked(3, color.other):
                            moves.append(Move(4, 2))
        elif color == BLACK:
            if CastlingRights.black_kingside:
                if self.piece_at(61) is None and self.piece_at(62) is None:
                    if not self.is_in_check():
                        if not self.is_attacked(
                            61, color.other
                        ) and not self.is_attacked(62, color.other):
                            moves.append(Move(60, 62))
            if CastlingRights.black_queenside:
                if (
                    self.piece_at(59) is None
                    and self.piece_at(58) is None
                    and self.piece_at(57) is None
                ):
                    if not self.is_in_check():
                        if not self.is_attacked(
                            59, color.other
                        ) and not self.is_attacked(58, color.other):
                            moves.append(Move(60, 58))
        return moves

    def legal_moves(self):
        pseudo_legal_moves = self.pseudo_legal_moves()
        moves = []
        for move in pseudo_legal_moves:
            self.make_move(move)
            if not self.is_in_check(self.side_to_move.other):
                moves.append(move)
            self.undo_move()
        moves.extend(self.castling_moves())
        return moves

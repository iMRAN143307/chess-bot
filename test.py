from chessdk import (
    Move,
    parse_fen
)

from board import Board

my_board = Board(parse_fen("k7/8/3R1P2/6PP/4P3/PPB3K1/2B5/1R6 b - - 12 78"))
print(my_board.legal_moves())
print(my_board.is_attacked())

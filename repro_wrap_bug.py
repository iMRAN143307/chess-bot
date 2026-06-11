"""Minimal reproduction of the phantom-pawn-attack (file-wrap) bug.

Position: white king g5, black king f8, black pawn a6. White to move.

    8 | . . . . . k . .
    7 | . . . . . . . .
    6 | p . . . . . . .
    5 | . . . . . . K .
    4 | . . . . . . . .       Kg5-h4 is legal: no black piece
    3 | . . . . . . . .       attacks h4.
    2 | . . . . . . . .
    1 | . . . . . . . .
        a b c d e f g h

But `pawn_attacking_square` in board.py checks for attacking pawns with raw
index arithmetic (square +/- 7 and +/- 9), which wraps around the board edge:
h4 is square 31, and 31 + 9 = 40 = a6. So the a6 pawn appears to "attack" h4,
and legal_moves() wrongly drops Kh4.

In the arena this is what gets you flagged for illegal moves: when the
*opponent* legally plays a king move like this, the UCI wrapper replays the
game through YOUR legal_moves(), can't find the move, and your internal board
silently stops updating -- so your next move comes from a stale position.
(I should fix this on my end in the arena too, if your bot rejects a valid move
the arena should just stop the bot right there and raise that warning. I'll get that
fixed up later today)

Run from your repo root:  python repro_wrap_bug.py
"""

from board import Board
from chessdk import BLACK
from chessdk.squares import parse_square

FEN = "5k2/8/p7/6K1/8/8/8/8 w - - 0 1"

board = Board.from_fen(FEN)
h4 = parse_square("h4")

mine = sorted(m.uci() for m in board.legal_moves())
print(f"position:                    {FEN}")
print(f"your legal_moves():          {mine}")
print(
    f"your is_attacked(h4, BLACK): {board.is_attacked(h4, BLACK)}   <- should be False"
)

# Same position through the kit's reference board, for comparison.
from chessdk.reference import Board as ReferenceBoard

ref = sorted(m.uci() for m in ReferenceBoard.from_fen(FEN).legal_moves())
print(f"reference legal_moves():     {ref}")

assert "g5h4" in mine, (
    "BUG reproduced: Kg5-h4 is legal but missing from legal_moves() -- "
    "the a6 pawn (square 40 = 31 + 9) phantom-attacks h4 across the board edge"
)
print("OK: g5h4 present -- bug is fixed")

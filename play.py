#!/usr/bin/env python3

from typing import List, Optional, Tuple

Board = List[List[Optional[str]]]


def create_starting_board() -> Board:
    board: Board = [[None for _ in range(8)] for _ in range(8)]

    def back_rank(color: str, row: int):
        pieces = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        for col, p in enumerate(pieces):
            board[row][col] = color + p

    back_rank("b", 0)
    for col in range(8):
        board[1][col] = "bP"

    back_rank("w", 7)
    for col in range(8):
        board[6][col] = "wP"

    return board


def print_board(board: Board) -> None:
    print("\n   a  b  c  d  e  f  g  h")
    print("  ------------------------")
    for row in range(8):
        rank = 8 - row
        line = f"{rank} |"
        for col in range(8):
            piece = board[row][col]
            if piece is None:
                line += " . "
            else:
                color, kind = piece[0], piece[1]
                symbol = kind.upper() if color == "w" else kind.lower()
                line += f" {symbol} "
        line += f"| {rank}"
        print(line)
    print("  ------------------------")
    print("   a  b  c  d  e  f  g  h\n")


def algebraic_to_coords(sq: str) -> Optional[Tuple[int, int]]:
    if len(sq) != 2:
        return None
    file, rank = sq[0], sq[1]
    if file < "a" or file > "h":
        return None
    if rank < "1" or rank > "8":
        return None
    col = ord(file) - ord("a")
    row = 8 - int(rank)
    return row, col


def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < 8 and 0 <= c < 8


def is_path_clear(board: Board, r1: int, c1: int, r2: int, c2: int) -> bool:
    """Check that all squares between (r1,c1) and (r2,c2) are empty."""
    dr = r2 - r1
    dc = c2 - c1
    step_r = (dr > 0) - (dr < 0)
    step_c = (dc > 0) - (dc < 0)
    r, c = r1 + step_r, c1 + step_c
    while (r, c) != (r2, c2):
        if board[r][c] is not None:
            return False
        r += step_r
        c += step_c
    return True


def is_square_attacked_by(board: Board, row: int, col: int, attacker_color: str) -> bool:
    """Return True if the square (row,col) is attacked by any piece of attacker_color."""
    other = attacker_color

    bishop_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    rook_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    pawn_dir = -1 if other == "w" else 1
    for dc in (-1, 1):
        r = row + pawn_dir
        c = col + dc
        if in_bounds(r, c):
            piece = board[r][c]
            if piece == other + "P":
                return True

    # Knights
    knight_jumps = [
        (-2, -1), (-2, 1),
        (-1, -2), (-1, 2),
        (1, -2), (1, 2),
        (2, -1), (2, 1),
    ]
    for dr, dc in knight_jumps:
        r = row + dr
        c = col + dc
        if in_bounds(r, c):
            piece = board[r][c]
            if piece == other + "N":
                return True

    # Bishops / Queens (diagonals)
    for dr, dc in bishop_dirs:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            piece = board[r][c]
            if piece is not None:
                if piece[0] == other and piece[1] in ("B", "Q"):
                    return True
                break
            r += dr
            c += dc

    # Rooks / Queens (straight)
    for dr, dc in rook_dirs:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            piece = board[r][c]
            if piece is not None:
                if piece[0] == other and piece[1] in ("R", "Q"):
                    return True
                break
            r += dr
            c += dc

    # Kings (adjacent squares)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r = row + dr
            c = col + dc
            if in_bounds(r, c):
                piece = board[r][c]
                if piece == other + "K":
                    return True

    return False


def find_king(board: Board, color: str) -> Optional[Tuple[int, int]]:
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == color + "K":
                return r, c
    return None


def is_in_check(board: Board, color: str) -> bool:
    king_pos = find_king(board, color)
    if king_pos is None:
        return False
    kr, kc = king_pos
    enemy_color = "b" if color == "w" else "w"
    return is_square_attacked_by(board, kr, kc, enemy_color)


def can_piece_move(board: Board, r1: int, c1: int, r2: int, c2: int, color: str) -> bool:
    """Check piece-specific movement rules, ignoring check on the king."""
    piece = board[r1][c1]
    if piece is None or piece[0] != color:
        return False
    kind = piece[1]
    dr = r2 - r1
    dc = c2 - c1
    abs_dr = abs(dr)
    abs_dc = abs(dc)
    dest = board[r2][c2]
    dest_color = dest[0] if dest else None

    if kind == "P":
        direction = -1 if color == "w" else 1
        start_row = 6 if color == "w" else 1

        if dc == 0:
            if dr == direction and dest is None:
                return True
              
            if r1 == start_row and dr == 2 * direction:
                mid_r = r1 + direction
                if board[mid_r][c1] is None and dest is None:
                    return True
            return False
          
        if abs_dc == 1 and dr == direction and dest is not None and dest_color != color:
            return True
        return False

    if kind == "N":
        return (abs_dr, abs_dc) in [(1, 2), (2, 1)] and (dest is None or dest_color != color)

    if kind == "B":
        if abs_dr == abs_dc and abs_dr != 0 and is_path_clear(board, r1, c1, r2, c2):
            return dest is None or dest_color != color
        return False

    if kind == "R":
        if (dr == 0 or dc == 0) and (dr != 0 or dc != 0) and is_path_clear(board, r1, c1, r2, c2):
            return dest is None or dest_color != color
        return False

    if kind == "Q":
        if (
            (abs_dr == abs_dc and abs_dr != 0) or
            ((dr == 0 or dc == 0) and (dr != 0 or dc != 0))
        ) and is_path_clear(board, r1, c1, r2, c2):
            return dest is None or dest_color != color
        return False

    if kind == "K":
        if max(abs_dr, abs_dc) == 1:
            return dest is None or dest_color != color
        return False

    return False


def copy_board(board: Board) -> Board:
    return [row[:] for row in board]


def is_legal_move(board: Board, r1: int, c1: int, r2: int, c2: int, color: str) -> bool:
    if not in_bounds(r1, c1) or not in_bounds(r2, c2):
        return False
    if r1 == r2 and c1 == c2:
        return False
    piece = board[r1][c1]
    if piece is None or piece[0] != color:
        return False

    if not can_piece_move(board, r1, c1, r2, c2, color):
        return False

    new_board = copy_board(board)
    move_piece(new_board, r1, c1, r2, c2)
    if is_in_check(new_board, color):
        return False
    return True


def move_piece(board: Board, r1: int, c1: int, r2: int, c2: int) -> None:
    piece = board[r1][c1]
    board[r1][c1] = None

    if piece is not None and piece[1] == "P":
        color = piece[0]
        if (color == "w" and r2 == 0) or (color == "b" and r2 == 7):
            piece = color + "Q"

    board[r2][c2] = piece


def has_any_legal_moves(board: Board, color: str) -> bool:
    for r1 in range(8):
        for c1 in range(8):
            piece = board[r1][c1]
            if piece is None or piece[0] != color:
                continue
            for r2 in range(8):
                for c2 in range(8):
                    if is_legal_move(board, r1, c1, r2, c2, color):
                        return True
    return False


def parse_move(move_str: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    s = move_str.strip().lower().replace(" ", "")
    if len(s) != 4:
        return None
    from_sq = s[0:2]
    to_sq = s[2:4]
    start = algebraic_to_coords(from_sq)
    end = algebraic_to_coords(to_sq)
    if start is None or end is None:
        return None
    return start, end


def main():
    print("Simple Console Chess (two players)")
    print("Move format: e2e4 or 'e2 e4'. Type 'quit' to exit.\n")

    board = create_starting_board()
    current_color = "w"

    while True:
        print_board(board)

        if is_in_check(board, current_color):
            if not has_any_legal_moves(board, current_color):
                winner = "Black" if current_color == "w" else "White"
                print(f"Checkmate! {winner} wins.")
                break
            else:
                print("You are in check!")
        else:
            if not has_any_legal_moves(board, current_color):
                print("Stalemate! It's a draw.")
                break

        player = "White" if current_color == "w" else "Black"
        move_str = input(f"{player} to move: ").strip()
        if move_str.lower() in ("quit", "exit"):
            print("Game ended.")
            break

        parsed = parse_move(move_str)
        if not parsed:
            print("Invalid move format. Use e2e4 or 'e2 e4'.")
            continue

        (r1, c1), (r2, c2) = parsed
        if not is_legal_move(board, r1, c1, r2, c2, current_color):
            print("Illegal move. Try again.")
            continue

        move_piece(board, r1, c1, r2, c2)
        current_color = "b" if current_color == "w" else "w"


if __name__ == "__main__":
    main()
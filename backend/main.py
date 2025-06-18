from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import copy

app = FastAPI()

# CORS 설정 (프론트엔드에서 요청 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 오델로 보드 초기화
EMPTY, BLACK, WHITE = 0, 1, 2
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1), (1, 0),  (1, 1)]

def initial_board():
    board = [[EMPTY] * 8 for _ in range(8)]
    board[3][3], board[4][4] = WHITE, WHITE
    board[3][4], board[4][3] = BLACK, BLACK
    return board

game_state = {
    "board": initial_board(),
    "current_player": BLACK
}

def is_valid_move(board, row, col, player):
    if board[row][col] != EMPTY:
        return False
    opponent = WHITE if player == BLACK else BLACK
    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        flipped = False
        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent:
            r += dr
            c += dc
            flipped = True
        if flipped and 0 <= r < 8 and 0 <= c < 8 and board[r][c] == player:
            return True
    return False

def apply_move(board, row, col, player):
    opponent = WHITE if player == BLACK else BLACK
    board[row][col] = player
    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        to_flip = []
        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent:
            to_flip.append((r, c))
            r += dr
            c += dc
        if to_flip and 0 <= r < 8 and 0 <= c < 8 and board[r][c] == player:
            for r2, c2 in to_flip:
                board[r2][c2] = player

@app.get("/state")
def get_state():
    return game_state

@app.post("/move")
def make_move(row: int, col: int):
    board = game_state["board"]
    player = game_state["current_player"]
    if not is_valid_move(board, row, col, player):
        return {"valid": False, "message": "Invalid move"}
    apply_move(board, row, col, player)
    game_state["current_player"] = WHITE if player == BLACK else BLACK
    return {"valid": True, "board": game_state["board"], "current_player": game_state["current_player"]}

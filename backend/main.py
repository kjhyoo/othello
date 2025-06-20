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

# 게임 히스토리를 위한 변수들
game_history = []
current_move_index = -1

def save_game_state():
    """현재 게임 상태를 히스토리에 저장"""
    global game_history, current_move_index
    state_copy = {
        "board": copy.deepcopy(game_state["board"]),
        "current_player": game_state["current_player"]
    }
    
    # 현재 인덱스 이후의 히스토리를 제거 (새로운 분기)
    game_history = game_history[:current_move_index + 1]
    game_history.append(state_copy)
    current_move_index = len(game_history) - 1

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

def has_valid_moves(board, player):
    """특정 플레이어가 놓을 수 있는 유효한 수가 있는지 확인"""
    for row in range(8):
        for col in range(8):
            if is_valid_move(board, row, col, player):
                return True
    return False

def check_and_switch_turn():
    """현재 플레이어가 놓을 수 있는 수가 없으면 상대방 턴으로 넘기기"""
    current_player = game_state["current_player"]
    opponent = WHITE if current_player == BLACK else BLACK
    
    # 현재 플레이어가 놓을 수 있는 수가 없으면
    if not has_valid_moves(game_state["board"], current_player):
        # 상대방도 놓을 수 있는 수가 없으면 게임 종료
        if not has_valid_moves(game_state["board"], opponent):
            return check_game_end()
        else:
            # 상대방 턴으로 넘기기
            game_state["current_player"] = opponent
            return {"turn_switched": True, "message": f"{'Black' if current_player == BLACK else 'White'}이 놓을 수 있는 수가 없어 {('White' if opponent == WHITE else 'Black')} 턴으로 넘어갑니다."}
    
    return {"turn_switched": False}

def count_pieces(board):
    """보드의 각 색깔 돌 개수를 세기"""
    black_count = 0
    white_count = 0
    empty_count = 0
    
    for row in range(8):
        for col in range(8):
            if board[row][col] == BLACK:
                black_count += 1
            elif board[row][col] == WHITE:
                white_count += 1
            else:
                empty_count += 1
    
    return black_count, white_count, empty_count

def check_game_end():
    """게임 종료 조건 확인 및 승자 판정"""
    black_count, white_count, empty_count = count_pieces(game_state["board"])
    
    # 게임 종료 조건: 보드가 가득 찼거나 더 이상 둘 곳이 없는 경우
    if empty_count == 0 or (not has_valid_moves(game_state["board"], BLACK) and not has_valid_moves(game_state["board"], WHITE)):
        if black_count > white_count:
            winner = "Black"
            result = "승리"
        elif white_count > black_count:
            winner = "White"
            result = "승리"
        else:
            winner = "무승부"
            result = "무승부"
        
        message = f"게임 종료! Black: {black_count}개, White: {white_count}개\n{winner} {result}!"
        
        return {
            "game_over": True, 
            "message": message,
            "black_count": black_count,
            "white_count": white_count,
            "winner": winner
        }
    
    return {"game_over": False}

@app.get("/state")
def get_state():
    black_count, white_count, empty_count = count_pieces(game_state["board"])
    
    # 게임 종료 상태 확인
    game_end_info = check_game_end()
    
    response = {
        "board": game_state["board"],
        "current_player": game_state["current_player"],
        "black_count": black_count,
        "white_count": white_count,
        "empty_count": empty_count
    }
    
    # 게임이 종료된 경우 추가 정보 포함
    if game_end_info["game_over"]:
        response["game_over"] = True
        response["winner"] = game_end_info["winner"]
    
    return response

@app.post("/move")
def make_move(row: int, col: int):
    board = game_state["board"]
    player = game_state["current_player"]
    if not is_valid_move(board, row, col, player):
        return {"valid": False, "message": "놓을 수 없는 위치입니다."}
    
    # 수를 적용한 후의 상태를 히스토리에 저장
    apply_move(board, row, col, player)
    game_state["current_player"] = WHITE if player == BLACK else BLACK
    
    # 수를 둔 후의 상태를 히스토리에 저장
    save_game_state()
    
    # 턴 체크 및 자동 턴 넘기기
    turn_check = check_and_switch_turn()
    
    response = {
        "valid": True, 
        "board": game_state["board"], 
        "current_player": game_state["current_player"]
    }
    
    # 턴이 넘어갔거나 게임이 종료된 경우 메시지 추가
    if turn_check["turn_switched"] or turn_check.get("game_over"):
        response["message"] = turn_check["message"]
        response["turn_switched"] = turn_check["turn_switched"]
        response["game_over"] = turn_check.get("game_over", False)
    
    return response

@app.post("/pass")
def pass_turn():
    """무르기 기능 - 마지막에 둔 수를 취소"""
    global game_history, current_move_index, game_state
    
    # 히스토리가 없거나 첫 번째 상태인 경우
    if current_move_index <= 0:
        return {"valid": False, "message": "무를 수 있는 상태가 없습니다."}
    
    # 이전 상태로 되돌리기 (마지막에 둔 수 취소)
    current_move_index -= 1
    previous_state = game_history[current_move_index]
    
    # 게임 상태 복원
    game_state["board"] = copy.deepcopy(previous_state["board"])
    game_state["current_player"] = previous_state["current_player"]
    
    return {
        "valid": True, 
        "board": game_state["board"], 
        "current_player": game_state["current_player"],
        "message": "무르기 성공!"
    }

@app.post("/reset")
def reset_game():
    """게임 초기화"""
    global game_history, current_move_index, game_state
    
    # 게임 상태 초기화
    game_state["board"] = initial_board()
    game_state["current_player"] = BLACK
    
    # 히스토리 초기화
    game_history = []
    current_move_index = -1
    
    # 초기 상태를 히스토리에 저장
    save_game_state()
    
    return {
        "valid": True,
        "board": game_state["board"],
        "current_player": game_state["current_player"],
        "message": "게임이 초기화되었습니다!"
    }

# 게임 초기화 시 초기 상태를 히스토리에 저장
save_game_state()

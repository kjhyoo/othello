<!DOCTYPE html>
<html>
<head>
  <title>Othello</title>
  <style>
    table { border-collapse: collapse; }
    td {
      width: 50px; height: 50px;
      border: 1px solid #444;
      text-align: center;
      font-size: 24px;
    }
    .black { background-color: black; border-radius: 50%; width: 40px; height: 40px; margin: auto; }
    .white { background-color: white; border-radius: 50%; width: 40px; height: 40px; margin: auto; }
    .board {
      background-color: #228B22; /* 진한 초록색 */
      border: 2px solid #333;
      display: grid;
      grid-template-columns: repeat(8, 40px);
      grid-template-rows: repeat(8, 40px);
      gap: 2px;
    }
    .cell {
      width: 40px;
      height: 40px;
      background-color: #228B22; /* 셀도 초록색 */
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 4px;
      border: 1px solid #333;
    }
    .stone.black {
      background: black;
      border-radius: 50%;
      width: 32px;
      height: 32px;
    }
    .stone.white {
      background: white;
      border-radius: 50%;
      width: 32px;
      height: 32px;
      border: 2px solid #333; /* 흰돌 테두리 추가 */
    }
  </style>
</head>
<body>
  <h1>Othello Game</h1>
  <p id="player-turn"></p>
  <table id="board"></table>

  <script>
    const boardEl = document.getElementById('board');
    const playerTurnEl = document.getElementById('player-turn');
    const apiBase = "https://othello-o36e.onrender.com";

    function renderBoard(board, currentPlayer) {
      boardEl.innerHTML = '';
      playerTurnEl.textContent = `Current Player: ${currentPlayer === 1 ? "Black" : "White"}`;
      for (let r = 0; r < 8; r++) {
        const row = document.createElement('tr');
        for (let c = 0; c < 8; c++) {
          const cell = document.createElement('td');
          if (board[r][c] === 1) {
            const piece = document.createElement('div');
            piece.className = 'black';
            cell.appendChild(piece);
          } else if (board[r][c] === 2) {
            const piece = document.createElement('div');
            piece.className = 'white';
            cell.appendChild(piece);
          }
          cell.onclick = () => makeMove(r, c);
          row.appendChild(cell);
        }
        boardEl.appendChild(row);
      }
    }

    async function fetchState() {
      const res = await fetch(`${apiBase}/state`);
      const data = await res.json();
      renderBoard(data.board, data.current_player);
    }

    async function makeMove(row, col) {
      const res = await fetch(`${apiBase}/move?row=${row}&col=${col}`, { method: 'POST' });
      const data = await res.json();
      if (!data.valid) {
        alert(data.message);
      }
      fetchState();
    }

    fetchState();
  </script>
</body>
</html>

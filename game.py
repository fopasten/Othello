
def copy_board(board):
    return [row[:] for row in board]

class Move:
    def __init__(self, coordinates, points):
        self.coordinates = coordinates
        self.points = points

class Othello:
    def __init__(self, P1, P2, board_size, difficulty):
        self.P1 = P1
        self.P2 = P2

        self.P1_score = 2
        self.P2_score = 2

        self.turn = None

        self.P1_skip = False
        self.P2_skip = False

        self.P1_stones = int(((board_size**2)-4)/2)
        self.P2_stones = int(((board_size**2)-4)/2)

        self.space = 'space'
        self.board_size = board_size
        self.difficulty = difficulty
        self.MAX_SCORE = board_size**2
        self.MIN_SCORE = -self.MAX_SCORE
        
        self.moves_analized = []

        self.current_board = []
        self.valid_moves = []

    def move(self, board, player, depth = None):
        if not depth:
            depth = self.difficulty
        self.valid_moves = self.get_valid_moves(board, player)
        if not self.valid_moves:
            return None
        move = self.alpha_beta_search(player, board, self.MIN_SCORE, self.MAX_SCORE, depth)
        return move.coordinates

    def alpha_beta_search(self, stone, board, alpha, beta, depth):
        # recursion base case
        if depth == 0:
            return Move(None, self.calc_score(board, stone))

        valid_moves = self.get_valid_moves(board, stone)
        if not valid_moves:
            # no more valid moves evaluate oponents next play
            if not self.get_valid_moves(board, self.opponent_stone(stone)):
                # no more moves for either player, return final state
                return Move(None, self.final_value(stone, board))
            # opponent has valid moves, return points for that move
            val = -self.alpha_beta_search(self.opponent_stone(stone), board, -beta, -alpha, depth - 1).points 
            return Move(None, val)

        best_move = valid_moves[0]
        best_move.points = alpha
        for move in valid_moves:
            if beta <= alpha:
                # Prune nodes that aren't worth visiting
                break
            sim_move_board = self.simulate_move(board, move.coordinates, stone)
            val = -self.alpha_beta_search(self.opponent_stone(stone), sim_move_board, -beta, -alpha, depth - 1).points 
            if val > alpha:
                # new max
                alpha = val
                best_move = move
                best_move.points = alpha
            self.moves_analized.append(move)
        return best_move

    def final_value(self, stone, board):
        # if player wins return max score so adv search uses this branch
        score = self.calc_score(board, stone)
        if score < 0:
            return self.MIN_SCORE
        elif score > 0:
            return self.MAX_SCORE
        return score

    def opponent_stone(self, symbol):
        if symbol == self.P1:
            return self.P2
        elif symbol == self.P2:
            return self.P1
        else:
            return self.space

    def calc_score(self, board, stone):
        score = 0
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j] == stone:
                    score += 1
                elif board[i][j] == self.opponent_stone(stone):
                    score -= 1
        return score

    def get_valid_moves(self, board, stone):
        valid_moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                # explore free spaces only
                if board[i][j] == self.space:
                    gain = self.check_move(board, i, j, stone)
                    if gain > 0:
                        valid_moves.append(Move((i, j), gain))
        if not valid_moves:
            return None
        else:
            return valid_moves

    def check_move(self, board, row, column, stone):
        points = 0
        directions = [-1, 0, 1]
        for hrzn in directions:
            for vrtc in directions:
                if vrtc != 0 or hrzn != 0:
                    if in_bounds(row + hrzn, column + vrtc, self.board_size):
                        examined = board[row + hrzn][column + vrtc]
                        if examined != self.space and examined != stone:
                            points += self.count_points(board, row + hrzn, column + vrtc, hrzn, vrtc)
                        # The move is valid if stones can be flipped
                        if points > 0:
                            return points
        return points

    def count_points(self, board, row, column, hrzn, vrtc):
        stone = board[row][column]
        count = 1
        # scalar value allows iteration in (hrzn, vrtc) direction
        for scalar in range(1, self.board_size + 1):
            if in_bounds(row + scalar * hrzn, column + scalar * vrtc, self.board_size):
                if board[row + scalar * hrzn][column + scalar * vrtc] == self.space:
                    return 0
                elif board[row + scalar * hrzn][column + scalar * vrtc] == stone:
                    count += 1
                else:
                    return count
            else:
                return 0
        return count

    def simulate_move(self, board, move, stone):
        if move == None:
            return board
        row, col = move

        # Needed to not modify original board
        board_copy = copy_board(board)
        board_copy[row][col] = stone
        
        directions = [-1, 0, 1]
        # this combination checks surrounding cells
        for vrtc in directions:
            for hrzn in directions:
                stones = []
                if vrtc == hrzn == 0:
                    continue
                lrow = row
                lcol = col
                lrow += vrtc
                lcol += hrzn
                while in_bounds(lrow, lcol, self.board_size):
                    # if stone is opponents color append to flip later
                    if board_copy[lrow][lcol] != stone and board_copy[lrow][lcol] != self.space:
                        stones.append((lrow, lcol))
                    # space breaks direct line, no stones flipped
                    elif board_copy[lrow][lcol] == self.space:
                        break
                    # if same color stone found, flip all stones in between
                    elif board_copy[lrow][lcol] == stone:
                        for a, b in stones:
                            board_copy[a][b] = stone
                        break
                    lrow += vrtc
                    lcol += hrzn
        return board_copy

    # Game flow helper functions

    def ai_turn(self):
        self.moves_analized = []

        ai_move = self.move(self.current_board, self.P2)

        if ai_move:
            return ai_move, self.P2, len(self.moves_analized)

    def change_turn(self, skipped = False):
        if turn := self.turn:
            if turn == self.P1:
                self.P1_skip = skipped
                self.turn = self.P2
                if not skipped: self.P1_stones -= 1 
            elif turn == self.P2:
                self.P2_skip = skipped
                self.turn = self.P1
                if not skipped: self.P2_stones -= 1 

    def calc_scores(self):
        p1score = 0
        p2score = 0
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.current_board[i][j] == self.P1:
                    p1score += 1
                elif self.current_board[i][j] == self.P2:
                    p2score += 1

        self.P1_score = p1score
        self.P2_score = p2score
        
        return p1score, p2score

    def check_game_conditions(self):
        score = abs(self.P1_score - self.P2_score)
        output = ""
        if self.P1_skip == self.P2_skip == True:
            output += 'No hay mas movimientos, partida finalizada\n'
        elif self.P1_stones == 0 and self.P2_stones == 0:
            output += 'Tablero completo, partida finalizada\n'
        elif self.P1_score == 0 or self.P2_score == 0:
            output += 'No hay mas movimientos, partida finalizada\n'
        if output:
            if self.P1_score < self.P2_score:
                output+='Ganador: Computadora\n'
            elif self.P1_score > self.P2_score:
                output+='Ganador: Jugador\n'
            else:
                output+='Empate\n'
            output+=f'Puntaje obtenido: {score}'
            return output

def in_bounds(r, c, n):
    # needed for manual input
    return 0 <= r < n and 0 <= c < n


# Tests
if __name__ == "__main__":
    sample_board = [
        ['space', 'space', 'space', 'space', 'space', 'space', 'space', 'white'],
        ['space', 'space', 'space', 'black', 'space', 'space', 'white', 'space'],
        ['space', 'space', 'space', 'space', 'black', 'white', 'black', 'black'],
        ['space', 'space', 'space', 'white', 'white', 'black', 'space', 'space'],
        ['space', 'space', 'white', 'white', 'white', 'black', 'space', 'space'],
        ['space', 'space', 'white', 'white', 'white', 'space', 'space', 'space'],
        ['space', 'space', 'white', 'space', 'white', 'space', 'space', 'space'],
        ['space', 'space', 'space', 'space', 'space', 'space', 'space', 'space'],
    ]
    player = Othello('black', 'white', 8, 9)
    for row in sample_board:
        print(row)

    pmove = player.move(sample_board,'black')
    for item in player.valid_moves:
        sample_board[item.coordinates[0]][item.coordinates[1]] = "xxxxx"

    for row in sample_board:
        print(row)

    for item in player.valid_moves:
        print(item.coordinates, " - ", item.points)

    print(f'nodes visited {len(player.moves_analized)}')

    print("returned: ", pmove)

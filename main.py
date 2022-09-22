import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, \
                            QTextEdit, QTabWidget, QVBoxLayout, QHBoxLayout, \
                            QGridLayout, QLabel, QCheckBox, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from time import perf_counter

from game import Othello

# http://cs.indstate.edu/~aaljubran/paper.pdf

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Othello'
        self.left = 300
        self.top = 200
        self.width = 770
        self.height = 800
        self.setFixedSize(self.width, self.height)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.table_widget = GameWidget(self)
        self.setCentralWidget(self.table_widget)
        
        self.show()

class BoardCell(QPushButton):
    
    def __init__(self, coordinates, func, *args, **kwargs):
        super(QPushButton, self).__init__(*args, **kwargs)
        self.setStyleSheet('width: 100%; height: 100%; background-color: #407936 !important;')
        self.setStyleSheet(self.styleSheet() + ' color: rgba(0, 0, 0, 0);')
        self.stone = 'space'
        self.coordinates = coordinates
        self.clicked.connect(lambda: func(self))

    def setStone(self, color):
        if color == 'black':
            self.setStyleSheet(self.styleSheet() + f' border-image: url(./sprites/{color}.svg);')
        elif color == 'white':
            self.setStyleSheet(self.styleSheet() + f' border-image: url(./sprites/{color}.svg);')
        self.stone = color
        self.setDisabled(True)

    def flipStone(self):
        if self.stone == 'black':
            self.setStyleSheet(self.styleSheet().replace('black', 'white'))
            self.stone = 'white'
        elif self.stone == 'white':
            self.setStyleSheet(self.styleSheet().replace('white', 'black'))
            self.stone = 'black'

    def suggestMove(self):
        self.setDisabled(True)
        old_style = self.styleSheet()
        self.setStyleSheet(old_style + ' border-image: url(./sprites/star.svg);')
        QTimer.singleShot(1000, lambda: self.setStyleSheet(old_style))
        QTimer.singleShot(1000, lambda: self.setEnabled(True))


    
class GameWidget(QWidget):
    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.game = None
        
        # Initialize tab screen
        self.tabs = QTabWidget(self)
        self.tab1 = QWidget(self)
        self.tab2 = QWidget(self)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Juego")
        self.tabs.addTab(self.tab2,"Opciones")
        
        # Create first tab

        self.tab1.layout = QVBoxLayout()
        self.tab1.setLayout(self.tab1.layout)
        self.gameheader = QWidget(self.tab1)
        self.gameheader.layout = QHBoxLayout()
        self.gameheader.setLayout(self.gameheader.layout)
        self.gameheader.setFixedHeight(50)
        self.P1score = QLabel(self)
        self.P2score = QLabel(self)
        qss = 'font-size: 24px;'
        self.P1score.setStyleSheet(qss)
        self.P2score.setStyleSheet(qss)

        self.suggest_move_btn = QPushButton('Sugerir Jugada', self)
        self.suggest_move_btn.setDisabled(True)
        self.suggest_move_btn.clicked.connect(self.suggest_moves)

        self.skip_turn_btn = QPushButton('Saltar Turno', self)
        self.skip_turn_btn.setDisabled(True)
        self.skip_turn_btn.clicked.connect(self.skip_turn)

        self.gameheader.layout.addWidget(self.P1score, alignment= Qt.AlignLeft)
        self.gameheader.layout.addWidget(self.suggest_move_btn)
        self.gameheader.layout.addWidget(self.skip_turn_btn)
        self.gameheader.layout.addWidget(self.P2score, alignment= Qt.AlignRight)
        self.tab1.layout.addWidget(self.gameheader)

        self.P2stones = QWidget(self.tab1)
        self.P2stones.layout = QVBoxLayout()
        self.P2stones.setLayout(self.P2stones.layout)
        self.P2stones.layout.setAlignment(self.P2stones, Qt.AlignTop)
        self.P2stones.setFixedSize(68,550)
        self.P2stones.setStyleSheet('.QWidget{border-image: url(./sprites/background.jpg)}')

        self.P1stones = QWidget(self.tab1)
        self.P1stones.layout = QVBoxLayout()
        self.P1stones.setLayout(self.P1stones.layout)
        self.P1stones.layout.setAlignment(self.P1stones, Qt.AlignBottom)
        self.P1stones.setFixedSize(68,550)
        self.P1stones.setStyleSheet('.QWidget{border-image: url(./sprites/background.jpg)}')
    
        self.board_stones = QWidget(self.tab1)
        self.board_stones.layout = QHBoxLayout()
        self.board_stones.setLayout(self.board_stones.layout)


        self.board = QWidget(self.tab1)
        self.board.setFixedSize(550, 550)
        self.board.setStyleSheet('.QWidget{border-image: url(./sprites/background.jpg)}')
        self.board.layout = QGridLayout()
        self.board.setLayout(self.board.layout)

        self.board_stones.layout.addWidget(self.P2stones)
        self.board_stones.layout.addWidget(self.board)
        self.board_stones.layout.addWidget(self.P1stones)

        self.tab1.layout.addWidget(self.gameheader)
        self.tab1.layout.addWidget(self.board_stones,alignment=Qt.AlignCenter)

        self.output_box = QTextEdit(self.tab1)
        self.output_box.setReadOnly(True)
        self.output_box.setTextInteractionFlags(Qt.NoTextInteraction)
        self.tab1.layout.addWidget(self.output_box)

        self.tab1.setLayout(self.tab1.layout)

        #################################################
        # Second Tab

        self.tab2.layout = QVBoxLayout()
        self.tab2.layout.setContentsMargins(20,20,20,20)
        self.tab2.layout.setAlignment(self.tab2, Qt.AlignTop)

        self.optionsbanner = QLabel(self)
        banner = QPixmap('./sprites/banner.jpg')
        self.optionsbanner.setPixmap(banner)
        self.tab2.layout.addWidget(self.optionsbanner, alignment=Qt.AlignCenter)

        text_instructions = "<h3>Instrucciones de uso</h3>" \
                            '<p align="justify">El juego comienza con 4 fichas en el centro intercaladas'\
                            ', y un numero igual de fichas para cada uno, el jugador con '\
                            "fichas negras tiene el primer turno, las fichas solo se pueden posicionar " \
                            "donde genere puntaje, se voltearán todas las fichas del color opuesto entre " \
                            "dos fichas en linea diagonal u ortogonal. Si un jugador no tiene movimientos " \
                            "validos, cede su turno. La partida finaliza cuando ningún jugador tiene " \
                            "movimientos validos o el tablero está lleno, gana quien tiene más fichas.</p>" 

        self.instructions_lbl = QLabel(text_instructions, self)
        self.instructions_lbl.setWordWrap(True)
        self.instructions_lbl.setAlignment(Qt.AlignTop)
        self.tab2.layout.addWidget(self.instructions_lbl)

        self.board_size_lbl = QLabel(self.tab2)
        self.board_size_lbl.setText("Selecciona tamaño del tablero: ")
        self.board_size_lbl.setFixedWidth(200)

        self.brd_chk_ly = QWidget(self)
        self.brd_chk_ly.layout = QHBoxLayout()
        self.brd_chk_ly.layout.setContentsMargins(0,0,0,0)

        self.cb1 = QCheckBox("6 x 6", self.brd_chk_ly)
        self.cb1.setChecked(True)
        self.cb1.stateChanged.connect(lambda:self.cb2.setChecked(not self.cb1.checkState()))
        
        self.cb2 = QCheckBox("8 x 8", self.brd_chk_ly)
        self.cb2.stateChanged.connect(lambda:self.cb1.setChecked(not self.cb2.checkState()))
        
        self.brd_chk_ly.layout.addWidget(self.board_size_lbl, alignment=Qt.AlignLeft)
        self.brd_chk_ly.layout.addWidget(self.cb1)        
        self.brd_chk_ly.layout.addWidget(self.cb2)
        self.brd_chk_ly.layout.addStretch(0)
        
        self.brd_chk_ly.setLayout(self.brd_chk_ly.layout)
        self.tab2.layout.addWidget(self.brd_chk_ly)

        self.difficulty_lbl = QLabel(self.tab2)
        self.difficulty_lbl.setText("Selecciona la dificultad: ")
        self.difficulty_lbl.setFixedWidth(200)
        self.tab2.layout.addWidget(self.difficulty_lbl)

        self.difficulty_cbox = QComboBox(self.tab2)
        self.difficulty_cbox.addItems(['Muy Facil', 'Facil', 'Media', 'Dificil', 'Muy Dificil', 'T-800'])
        self.tab2.layout.addWidget(self.difficulty_cbox)

        self.help_lbl = QLabel(self.tab2)
        self.help_lbl.setText("Nivel de IA para sugerir movimientos: ")
        self.help_lbl.setFixedWidth(300)
        self.tab2.layout.addWidget(self.help_lbl)

        self.ai_help_cbox = QComboBox(self.tab2)
        self.ai_help_cbox.addItems(['Muy Facil', 'Facil', 'Media', 'Dificil', 'Muy Dificil', 'T-800'])
        self.tab2.layout.addWidget(self.ai_help_cbox)

        self.player_stone_lbl = QLabel(self.tab2)
        self.player_stone_lbl.setText("Selecciona el color de ficha: ")
        self.player_stone_lbl.setFixedWidth(200)
        self.tab2.layout.addWidget(self.player_stone_lbl)

        self.player_stone_cbox = QComboBox(self.tab2)
        self.player_stone_cbox.addItems(['Negra', 'Blanca'])
        self.tab2.layout.addWidget(self.player_stone_cbox)

        #################################################

        self.game_buttons = QWidget(self)
        self.game_buttons.layout = QHBoxLayout()

        self.b1 = QPushButton("Iniciar Juego", self.game_buttons)
        self.b1.setChecked(True)
        self.b1.clicked.connect(lambda:self.new_game())
        
        self.b2 = QPushButton("Reiniciar", self.game_buttons)
        self.b2.setDisabled(True)
        self.b2.clicked.connect(lambda:self.delete_board())
        
        self.game_buttons.layout.addWidget(self.b1)        
        self.game_buttons.layout.addWidget(self.b2)
        
        self.game_buttons.setLayout(self.game_buttons.layout)
        self.tab2.layout.addStretch()
        self.tab2.layout.addWidget(self.game_buttons)

        self.tab2.setLayout(self.tab2.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.tabs.setCurrentIndex(1)

    def try_move(self, button):
        if self.game.turn == self.game.P1:
            if self.game.P1_stones > 0:
                score = self.game.check_move(self.game.current_board, *button.coordinates, self.game.P1)
                if score > 0:
                    self.player_turn(button)
                    QTimer.singleShot(1000, lambda: self.ai_turn())
            else:
                self.send_output('Se acabaron las fichas, debes saltar turno')

    def skip_turn(self):
        if not self.game.get_valid_moves(self.game.current_board, self.game.P1) or self.game.P1_stones == 0:
            self.game.change_turn(skipped=True)
            self.check_game_conditions()
            self.ai_turn()
        else:
            self.send_output('No se puede saltar el turno, existen movimientos validos')

    def player_turn(self, button):
        button.setStone(self.game.P1)
        self.remove_stone(self.P1stones.layout, 1)
        delay = 200
        QTimer.singleShot(delay, lambda: self.process_move_ui(button.coordinates, button.stone))
        QTimer.singleShot(delay, lambda: self.game.change_turn())
        QTimer.singleShot(delay+50, lambda: self.check_game_conditions())
        

    def ai_turn(self):
        self.send_output(f'Turno de Computadora')
        t1 = perf_counter()
        ai_move = self.game.ai_turn()
        t2 = perf_counter()
        if ai_move and self.game.P2_stones:
            coordinates, stone, moves_analized = ai_move
            self.board.layout.itemAtPosition(*coordinates).widget().setStone(stone)
            self.remove_stone(self.P2stones.layout, 0)
            delay = 200
            QTimer.singleShot(delay, lambda: self.process_move_ui(coordinates, stone))
            QTimer.singleShot(delay, lambda: self.game.change_turn())
            QTimer.singleShot(delay, lambda: self.send_output(f'[AI] {moves_analized} movimientos analizados en {t2-t1:.8f} segundos'))            
            QTimer.singleShot(delay, lambda: self.send_output(f'Turno de Jugador'))            
            QTimer.singleShot(delay+50, lambda: self.check_game_conditions())            
        else:
            self.send_output(f'[AI] No hay jugadas validas, saltando turno')
            self.game.change_turn(skipped=True)
            self.send_output(f'Turno de Jugador')
            self.check_game_conditions()

    def send_output(self, text):
        self.output_box.insertPlainText(text + "\n")
        self.output_box.verticalScrollBar().setValue(self.output_box.verticalScrollBar().maximum())

    def process_move_ui(self, coordinates, stone):
        new_board = self.game.simulate_move(self.game.current_board, coordinates, stone)
        n = self.game.board_size
        for i in range(n):
            for j in range(n):
                if (btn := self.board.layout.itemAtPosition(i,j).widget()).stone != (new_color := new_board[i][j]):
                    if btn.stone == 'space':
                        btn.setStone(new_color)
                    else:
                        btn.flipStone()
        self.game.current_board = new_board
        self.update_score()

    def suggest_moves(self):
        suggested_move= self.game.move(self.game.current_board, self.game.P1, self.ai_help_cbox.currentIndex()+1)
        if suggested_move:
            i, j = suggested_move
            self.board.layout.itemAtPosition(i,j).widget().suggestMove()
        else:
            self.send_output('No hay jugadas disponibles, debes saltar el turno')

    def check_game_conditions(self):
        output = self.game.check_game_conditions()
        if output:
            self.send_output(output)
            self.suggest_move_btn.setEnabled(False)
            self.skip_turn_btn.setEnabled(False)

    def update_score(self):
        p1, p2 = self.game.calc_scores()
        self.P1score.setText(f'Jugador 1 | {p1}')
        self.P2score.setText(f'{p2} | Jugador 2')

    def remove_stone(self, layout, pos):
        child = layout.takeAt(pos)
        childWidget = child.widget()
        if childWidget:
            childWidget.setParent(None)
            childWidget.deleteLater()

    def switch_menu_items(self):
        status = self.b1.isEnabled()
        self.b2.setEnabled(status)
        self.ai_help_cbox.setDisabled(status)
        self.difficulty_cbox.setDisabled(status)
        self.player_stone_cbox.setDisabled(status)
        self.cb1.setCheckable(not status)
        self.cb2.setCheckable(not status)
        self.suggest_move_btn.setEnabled(status)
        self.skip_turn_btn.setEnabled(status)
        self.b1.setDisabled(status)

    def delete_board(self):
        clearLayout(self.board.layout)
        clearLayout(self.P1stones.layout)
        clearLayout(self.P2stones.layout)

        self.game = None

        self.switch_menu_items()


    def new_game(self):
        clearLayout(self.board.layout)
        clearLayout(self.P1stones.layout)
        clearLayout(self.P2stones.layout)

        n, starting_stones = self.set_initial_stones()

        if n:
            stones = ['black','white']
            if self.player_stone_cbox.currentIndex() == 1:
                stones = stones[::-1]
            self.game = Othello(*stones, n, self.difficulty_cbox.currentIndex()+1)
            
            self.game.current_board = self.build_board(n, starting_stones)

            self.fill_player_stones(n)
            
            self.P1score.setText('Jugador 1 | 2')
            self.P2score.setText('2 | Jugador 2')

            self.switch_menu_items()
            self.tabs.setCurrentIndex(0)
            self.first_turn()


    def set_initial_stones(self):
        n, starting_stones = None, {}
        if self.cb1.isChecked():
            n = 6
            starting_stones = {
                '14': 'black',
                '15': 'white',
                '20': 'white',
                '21': 'black',
            }

        elif self.cb2.isChecked():
            n = 8
            starting_stones = {
                '27': 'black',
                '28': 'white',
                '35': 'white',
                '36': 'black',
            }
        return n, starting_stones

    def build_board(self, n, starting_stones):
        board_matrix = []
        for i in range(n):
            temp = []
            for j in range(n):
                cell = str(n*i+j)
                button = BoardCell((i, j), self.try_move, cell, self.tab1)
                if cell in starting_stones:
                    color = starting_stones[cell]
                    button.setStone(color)
                    temp.append(color)
                else:
                    temp.append('space')
                
                self.board.layout.addWidget(button, i, j, 1, 1)
                self.board.layout.setSpacing(2)
            board_matrix.append(temp)

        return board_matrix
            
    def fill_player_stones(self, n):
        self.P1stones.layout.addStretch(0)
        for _ in range(int(((n**2)-4)/2)):
            stone = QPixmap('./sprites/vstone.svg')
            P1stone = QLabel(self)
            P1stone.setPixmap(stone)
            P2stone = QLabel(self)
            P2stone.setPixmap(stone)
            self.P1stones.layout.addWidget(P1stone)
            self.P1stones.layout.setSpacing(2)
            self.P2stones.layout.addWidget(P2stone)
            self.P2stones.layout.setSpacing(2)
            
        self.P2stones.layout.addStretch(0)

    def first_turn(self):
        self.send_output('### Inicia nueva partida ###')
        if self.player_stone_cbox.currentIndex() == 1:
            self.send_output('Computadora tiene el primer turno')
            self.game.turn = self.game.P2
            QTimer.singleShot(2000, lambda: self.ai_turn())
        else:
            self.send_output('Jugador tiene el primer turno')
            self.game.turn = self.game.P1


def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        childWidget = child.widget()
        if childWidget:
            childWidget.setParent(None)
            childWidget.deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
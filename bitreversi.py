
def rc_to_move(row, col):
    return 1 << (row * 8 + col)
def move_to_rc(move: int) -> tuple[int, int]:
    if move == 0:
        raise ValueError("Cannot convert move=0 to coordinates (no bit set).")
    index = move.bit_length() - 1
    return divmod(index, 8)

def bitboard_to_rc_list(bitboard: int):
    return [(i // 8, i % 8) for i in range(64) if (bitboard >> i) & 1]


class BitboardReversi:
    # Directions (shift amounts)
    DIRS = [8, -8, 1, -1, 9, 7, -7, -9]
    MASK_LEFT = 0xfefefefefefefefe
    MASK_RIGHT = 0x7f7f7f7f7f7f7f7f
    MASK_ALL = 0xffffffffffffffff

    DIR_MASKS = {
        1: MASK_RIGHT,
        -1: MASK_LEFT,
        9: MASK_RIGHT,
        -9: MASK_LEFT,
        7: MASK_LEFT,
        -7: MASK_RIGHT,
        8: MASK_ALL,
        -8: MASK_ALL
    }

    def __init__(self):
        """ 
            Implémentation simple du jeu de reversi (Othello) : https://fr.wikipedia.org/wiki/Othello_(jeu). 
        """

        self.black = 0x0000000810000000
        self.white = 0x0000001008000000

    def reset(self):
        """
            Initialisation d'un jeu
        """

        self.black = 0x0000000810000000
        self.white = 0x0000001008000000

    def _shift(self, bb, d):
        mask = self.DIR_MASKS[d]
        return ((bb << d) if d > 0 else bb >> -d) & mask

    def valid_moves(self, player):
        """
            Renvoie la liste des coups valides pour un joueur (1 ou -1)
        """

        P = self.black if player == 1 else self.white
        O = self.white if player == 1 else self.black
        empty = ~(P | O) & self.MASK_ALL

        moves = 0
        for d in self.DIRS:
            mask = self.DIR_MASKS[d]
            x = self._shift(P, d) & O
            x |= self._shift(x, d) & O
            x |= self._shift(x, d) & O
            x |= self._shift(x, d) & O
            x |= self._shift(x, d) & O
            x |= self._shift(x, d) & O
            moves |= self._shift(x, d) & empty
        return bitboard_to_rc_list(moves) 
    
    def make_move(self, row, col, player):
        """ 
            Joue le coup pour le joueur
        """
        if row<0 or col <0:
            return False
        P = self.black if player == 1 else self.white
        O = self.white if player == 1 else self.black
        move = rc_to_move(row, col)

        if (P | O) & move:
            return False  # La case est déjà occupée

        flipped = 0
        for d in self.DIRS:
            x = self._shift(move, d)
            captured = 0
            while x & O:
                captured |= x
                x = self._shift(x, d)
            if x & P:
                flipped |= captured

        if flipped:
            P |= move | flipped
            O &= ~flipped
            if player == 1:
                self.black, self.white = P, O
            else:
                self.white, self.black = P, O
            return True
        return False
    
    def print_board(self):
        """
            Affichage du plateau
        """

        b, w = self.black, self.white
        for i in range(64):
            bit = 1 << i
            print('B' if b & bit else 'W' if w & bit else '.', end=' ')
            if (i + 1) % 8 == 0:
                print()
        print()

    def score(self):
        """
            Renvoie le score
        """

        return self.black.bit_count()-self.white.bit_count()

    def board_to_int(self):
        """
            Renvoie la représentation sous la forme d'un couple d'entier de la configuration d'un plateau
        """
        return self.black, self.white
    def bitboards_to_board(self,player1, player2):
        """
            Reconstitue un plateau à partir de la représentation en entier
        """
        self.black = player1
        self.white = player2

    def copy(self):
        """
            Réalise le clone de la partie
        """

        game = BitboardReversi()
        game.white = self.white
        game.black = self.black
        return game
    def game_over(self):
        """
            Teste si le jeu est fini
        """

        occupied = self.black | self.white
        if occupied == 0xffffffffffffffff:
            return True
        return len(self.valid_moves(1))==0 and len(self.valid_moves(-1))==0

    def nb_moves(self):
        """
            Renvoie le nombre de coups joués
        """
        return self.white.bit_count()+self.black.bit_count()-4

# ── Compatibilité agents_mcts.py ──────────────────────────────────────────────
# agents_mcts fait "from bitreversi import *" et appelle :
#   Reversi()            → alias vers BitboardReversi
#   plateau.board.sum()  → nombre total de pions (pour déduire le tour)

import numpy as _np

def _board_property(self):
    """Reconstruit un tableau numpy 8x8 depuis les bitboards (pour .board.sum())."""
    arr = _np.zeros((8, 8), dtype=int)
    for i in range(64):
        x, y = divmod(i, 8)
        if (self.black >> i) & 1:
            arr[x][y] = 1
        elif (self.white >> i) & 1:
            arr[x][y] = -1
    return arr

BitboardReversi.board = property(_board_property)

# Alias attendu par agents_mcts
Reversi = BitboardReversi

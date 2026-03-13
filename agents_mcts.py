from bitreversi import *
from mc_utils import *
import numpy as np
import random

class AgentFlatMCTS:
    def __init__(self,board,nb_simu):
        self.nb_simu=nb_simu
        self.board=board

    def play(self,player):
        List = self.board.valid_moves(player)
        list_res =[0 for i in range(len(List))]
        index=0
        if len(List) == 0:
            return (-1,-1)
        for move in List:
            a1,a2=move
            copy=self.board.copy()
            copy.make_move(a1,a2,player)
            simu=simu_mc(copy,-player,self.nb_simu)
            for s in simu:
                p1,p2=s
                copy.bitboards_to_board(p1,p2)
                res=copy.score()
                if player == 1:
                    if res > 0:
                        list_res[index]=list_res[index]+1
                else:
                    if res < 0:
                        list_res[index]=list_res[index]+1 
            index+=1    
        return List[np.argmax(list_res)]

class MCTSNode:
    def __init__(self, game, player, parent=None):
        self.player = player
        self.parent = parent
        self.children = {}
        self.config = game.board_to_int()
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = game.valid_moves(player)

    def is_fully_expanded(self):
        return self.untried_moves == []

    def best_move(self, K):
        """Renvoie le meilleur enfant selon la formule UCB1."""
        T = max(1, self.visits)
        best_score = -float('inf')
        best_mv = None
        best_child = None

        for mv, child in self.children.items():
            if child.visits == 0:
                score = float('inf')  # priorité aux enfants jamais visités
            else:
                moy = child.wins / child.visits
                score = moy + K * np.sqrt(np.log(T) / child.visits)

            if score > best_score:
                best_score = score
                best_mv = mv
                best_child = child

        return best_mv, best_child


class AgentMCTS:
    def __init__(self, board, nb_simu=1000, K=1.41, rollout_moves=100):
        self.game = board
        self.nb_simu = nb_simu
        self.K = K
        self.rollout_moves = rollout_moves
        self.nodes = {}

    # Amélioration ajoutée : rollout biaisé (coins > bords > random)
   
    def _biased_rollout(self, board, turn, limit=100):
        """Simulation aléatoire mais avec biais pour favoriser les coins."""
        COINS = {(0, 0), (0, 7), (7, 0), (7, 7)}
        steps = 0
        while not board.game_over() and steps < limit:
            moves = board.valid_moves(turn)
            if not moves:
                # passe
                turn = -turn
                steps += 1
                continue
            # 1) priorité aux coins
            coins = [m for m in moves if m in COINS]
            if coins:
                mv = random.choice(coins)
            else:
                # 2) sinon, bords
                edges = [m for m in moves if m[0] in (0, 7) or m[1] in (0, 7)]
                mv = random.choice(edges) if edges else random.choice(moves)
            board.make_move(mv[0], mv[1], turn)
            turn = -turn
            steps += 1
        # résultat final
        sc = board.score()
        if sc > 0:
            return 1
        elif sc < 0:
            return -1
        else:
            return 0

    def play(self, player):
        cle = (self.game.board_to_int(), player)
        if cle not in self.nodes:
            self.nodes[cle] = MCTSNode(self.game, player)
        racine = self.nodes[cle]

        if not racine.untried_moves and not racine.children:
            return (-1, -1)

        for _ in range(self.nb_simu):
            noeud = racine
            p1, p2 = noeud.config

            plateau = Reversi()
            plateau.bitboards_to_board(p1, p2)
            # déterminer automatiquement le joueur courant
            nb_pions = plateau.board.sum()
            tour = 1 if nb_pions % 2 == 0 else -1

            #  Sélection 
            while noeud.is_fully_expanded() and not plateau.game_over() and noeud.children:
                coup, noeud = noeud.best_move(self.K)
                if coup != (-1, -1):
                    plateau.make_move(coup[0], coup[1], tour)
                tour = -tour

            #  Expansion 
            if not plateau.game_over() and noeud.untried_moves:
                coup = noeud.untried_moves.pop()
                if coup != (-1, -1):
                    plateau.make_move(coup[0], coup[1], tour)
                enfant = MCTSNode(plateau, -tour, parent=noeud)
                noeud.children[coup] = enfant
                noeud = enfant
                tour = -tour

            # Simulation (biaisée)
            gagnant = self._biased_rollout(plateau.copy(), tour, limit=self.rollout_moves)

            # Backpropagation
            while noeud:
                noeud.visits += 1
                if gagnant == 0:
                    noeud.wins += 0.5
                elif gagnant == noeud.player:
                    noeud.wins += 1.0
                noeud = noeud.parent

        if not racine.children:
            return (-1, -1)
        return max(racine.children.items(), key=lambda kv: kv[1].visits)[0]



        

        

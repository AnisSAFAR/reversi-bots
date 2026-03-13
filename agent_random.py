import random

class AgentRandom:
    def __init__(self,b):
        self.board=b

    def play(self,player):
        List = self.board.valid_moves(player)
        if len(List) == 0:
            return (-1,-1)
        i = random.randint(0,len(List)-1)
        return List[i]



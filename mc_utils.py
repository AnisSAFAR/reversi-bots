import agent_random as agent_random_mod
from reversi import *


def get_mask_one(x,y):
    l=[0 for i in range(64)]
    l[8*x+y]=1
    res=0
    for i in range(64):
        if l[i]==1:
            res=res+2**i
    return res

#une deuxième version de la fonction :
def get_mask_one2(x,y):
    game = Reversi()
    game.board = np.zeros((8,8))
    game.board[x,y]=1
    p1,p2 = game.board_to_int()
    return p1



def get_mask(l):
    res=0
    for i in l :
        x,y=i
        res|=get_mask_one(x,y)
    return res

def rollout(game,turn=1,nb_moves=100):
    player_1 = agent_random_mod.AgentRandom(game)
    nb=0
    while(not game.game_over() and nb<nb_moves):
        (x,y)=player_1.play(turn)
        if not (x,y)==(-1,-1):
            game.make_move(x,y,turn)
        turn=-turn
    return game.board_to_int()

def simu_mc(game,turn=1,nb=1000,moves=100):
    l=[]
    i=0
    while i<nb:
        c=game.copy()
        l.append(rollout(c,turn,moves))
        i+=1
    return l

def estime_coins(simus,nb_coins):
    l_coins = [(0,0),(0,7),(7,0),(7,7)]
    number_masques = get_mask(l_coins)
    plat_actuel= Reversi()
    nb_parties_avec_nb_coins = 0
    nb_parties_gagnee_avec_nb_coins = 0

    for partie in simus :
        p1,p2 = partie
        plat_actuel.bitboards_to_board(p1,p2)
        score = plat_actuel.score()
        if (score > 0 ) : #cas joueur  : 1
            if((p2 & number_masques).bit_count()==nb_coins):
                nb_parties_avec_nb_coins +=1
            
            if ((p1 & number_masques).bit_count()==nb_coins):
                nb_parties_gagnee_avec_nb_coins +=1
                nb_parties_avec_nb_coins +=1

        elif (score == 0 ) : #partie nulle 
            if (((p1 & number_masques).bit_count()==nb_coins) or ((p2 & number_masques).bit_count()==nb_coins)):
                nb_parties_avec_nb_coins +=1
            
        else :
                if ((p2 & number_masques).bit_count()==nb_coins):
                    nb_parties_gagnee_avec_nb_coins +=1
                    nb_parties_avec_nb_coins +=1
                if ((p1 & number_masques).bit_count()==nb_coins):
                    nb_parties_avec_nb_coins +=1
                    
               
    return nb_parties_gagnee_avec_nb_coins / nb_parties_avec_nb_coins



def  cdt_one_corner(game):
    c=get_mask([(0,0),(0,7),(7,0),(7,7)])
    p1,p2=game.board_to_int()
    return ((p1 & c).bit_count() == 1)and((p2 & c).bit_count() ==0)or((p2 & c).bit_count() == 1)and((p1 & c).bit_count() ==0 )

def play_until(game,cdt,turn):
    player_1 = agent_random_mod.AgentRandom(game)
    while(not game.game_over() and  not cdt(game)):
        (x,y)=player_1.play(turn)
        if not (x,y)==(-1,-1):
            game.make_move(x,y,turn)
        turn=-turn
    return game


def find_game(cdt):
    game= Reversi()
    play_until(game,cdt,1)
    if game.game_over() and not cdt(game):
        return find_game(cdt)
    else :
        return game

def  compute_win_cdt(cdt,nb_games,nb_simu):
    lres = []
    for i in range(nb_games):
        game=find_game(cdt)
        list_sim=simu_mc(game,-1,nb_simu,100)
        for simu in list_sim:
            game= Reversi()
            p1,p2 = simu
            game.bitboards_to_board(p1,p2)
            if game.score()>0:  #partie gangée 
                lres.append(1)
            else:
                lres.append(0)
    return sum(lres)/len(lres)


#deuxième version de la fonction 
def  compute_win_cdt2(cdt,nb_games,nb_simu):
    list_games=[find_game(cdt) for i in range(nb_games)]
    list_sim=[simu_mc(g,-1,nb_simu,100) for g in list_games]
    list_res=[]
    for lol in list_sim :
        for plat in lol:
            game=Reversi()
            x,y=plat
            game.bitboards_to_board(x,y)
            if game.score()>0:
                list_res.append(1)
            else:
                list_res.append(0)
    return sum(list_res)/len(list_res)


        
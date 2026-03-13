"""
tournament.py — Comparaison et tournoi entre les agents Reversi
================================================================
Agents disponibles :
  - AgentRandom     : coups aléatoires parmi les coups valides
  - AgentFlatMCTS   : Monte-Carlo plat (simulation pure)
  - AgentMCTS       : MCTS arborescent avec rollout biaisé (coins > bords > random)

Usage :
  python tournament.py                  → tournoi complet entre tous les agents
  python tournament.py --quick          → version rapide (moins de simulations)
  python tournament.py --agent1 Random --agent2 MCTS  → duel spécifique
"""

import argparse
import time
from collections import defaultdict

# ---------- imports agents ----------
from agent_random import AgentRandom

try:
    from agents_mcts import AgentFlatMCTS, AgentMCTS
    MCTS_AVAILABLE = True
except ImportError:
    MCTS_AVAILABLE = False
    print("[AVERTISSEMENT] agents_mcts.py nécessite bitreversi/reversi — MCTS désactivé.")

try:
    from reversi import Reversi
    REVERSI_CLASS = Reversi
except ImportError:
    try:
        from bitreversi import Reversi
        REVERSI_CLASS = Reversi
    except ImportError:
        REVERSI_CLASS = None
        print("[ERREUR] Impossible d'importer Reversi. Vérifiez reversi.py / bitreversi.py.")


# ============================================================
#  FABRIQUE D'AGENTS
# ============================================================

def make_agent(name: str, board, nb_simu: int = 200):
    """Crée un agent par son nom."""
    name = name.lower()
    if name == "random":
        return AgentRandom(board)
    elif name == "flatmcts" and MCTS_AVAILABLE:
        return AgentFlatMCTS(board, nb_simu)
    elif name == "mcts" and MCTS_AVAILABLE:
        return AgentMCTS(board, nb_simu=nb_simu)
    else:
        raise ValueError(f"Agent inconnu ou non disponible : {name}")


# ============================================================
#  UNE PARTIE
# ============================================================

def play_game(agent1_name: str, agent2_name: str,
              nb_simu: int = 200, verbose: bool = False) -> int:
    """
    Joue une partie complète entre agent1 (joueur +1) et agent2 (joueur -1).
    Retourne : +1 si agent1 gagne, -1 si agent2 gagne, 0 si nul.
    """
    if REVERSI_CLASS is None:
        raise RuntimeError("Reversi non disponible.")

    board = REVERSI_CLASS()

    # Chaque agent a sa propre référence au plateau
    a1 = make_agent(agent1_name, board, nb_simu)
    a2 = make_agent(agent2_name, board, nb_simu)

    turn = 1  # +1 commence toujours
    moves_played = 0
    consecutive_passes = 0

    while not board.game_over():
        agent = a1 if turn == 1 else a2
        move = agent.play(turn)

        if move == (-1, -1):
            consecutive_passes += 1
            if consecutive_passes >= 2:
                break  # les deux passent → partie terminée
        else:
            consecutive_passes = 0
            board.make_move(move[0], move[1], turn)
            moves_played += 1

        if verbose:
            print(f"  Tour {moves_played:02d} | Joueur {'+1' if turn==1 else '-1'} "
                  f"({agent1_name if turn==1 else agent2_name}) → {move}")

        turn = -turn

    score = board.score()
    if verbose:
        print(f"  Score final : {score:+d} "
              f"({'agent1 gagne' if score > 0 else 'agent2 gagne' if score < 0 else 'nul'})")
    return 1 if score > 0 else (-1 if score < 0 else 0)


# ============================================================
#  DUEL (N parties avec alternance des couleurs)
# ============================================================

def duel(name1: str, name2: str, n_games: int = 20,
         nb_simu: int = 200) -> dict:
    """
    Fait s'affronter name1 vs name2 sur n_games parties.
    Les couleurs alternent à chaque partie pour l'équité.
    Retourne un dict de statistiques.
    """
    wins1 = wins2 = draws = 0
    total_time1 = total_time2 = 0.0

    print(f"\n  ⚔  {name1}  vs  {name2}  ({n_games} parties, {nb_simu} simul.)")
    print("  " + "─" * 50)

    for i in range(n_games):
        # Alternance : parties paires → name1=+1, impaires → name1=-1
        if i % 2 == 0:
            a1, a2 = name1, name2
            swap = False
        else:
            a1, a2 = name2, name1
            swap = True

        t0 = time.perf_counter()
        result = play_game(a1, a2, nb_simu=nb_simu)
        elapsed = time.perf_counter() - t0

        # Résultat du point de vue de name1
        if swap:
            result = -result

        if result == 1:
            wins1 += 1
            sym = "✓"
        elif result == -1:
            wins2 += 1
            sym = "✗"
        else:
            draws += 1
            sym = "="

        print(f"  Partie {i+1:02d}/{n_games}  {sym}  ({elapsed:.1f}s)")

    total = wins1 + wins2 + draws
    print(f"\n  Résultats finaux :")
    print(f"    {name1:<12} : {wins1:2d} victoires  ({100*wins1/total:.0f}%)")
    print(f"    {name2:<12} : {wins2:2d} victoires  ({100*wins2/total:.0f}%)")
    print(f"    Nuls        : {draws:2d}")

    return {
        "agent1": name1, "agent2": name2,
        "wins1": wins1, "wins2": wins2, "draws": draws,
        "winrate1": wins1 / total if total else 0,
        "winrate2": wins2 / total if total else 0,
    }


# ============================================================
#  TOURNOI COMPLET (round-robin)
# ============================================================

def round_robin(agents: list, n_games: int = 20, nb_simu: int = 200):
    """
    Tournoi round-robin : chaque agent affronte tous les autres.
    Affiche un classement final.
    """
    print("\n" + "═" * 60)
    print("  TOURNOI ROUND-ROBIN — Reversi Bots")
    print("═" * 60)

    scores = defaultdict(lambda: {"points": 0, "wins": 0, "losses": 0, "draws": 0})
    results = []

    for i, a1 in enumerate(agents):
        for a2 in agents[i+1:]:
            r = duel(a1, a2, n_games=n_games, nb_simu=nb_simu)
            results.append(r)

            # Points : 3 par victoire, 1 par nul
            scores[a1]["wins"]   += r["wins1"]
            scores[a1]["losses"] += r["wins2"]
            scores[a1]["draws"]  += r["draws"]
            scores[a1]["points"] += 3 * r["wins1"] + r["draws"]

            scores[a2]["wins"]   += r["wins2"]
            scores[a2]["losses"] += r["wins1"]
            scores[a2]["draws"]  += r["draws"]
            scores[a2]["points"] += 3 * r["wins2"] + r["draws"]

    # Classement
    print("\n" + "═" * 60)
    print("  CLASSEMENT FINAL")
    print("═" * 60)
    print(f"  {'Agent':<14} {'Pts':>4} {'V':>4} {'N':>4} {'D':>4}")
    print("  " + "─" * 38)

    classement = sorted(scores.items(), key=lambda x: x[1]["points"], reverse=True)
    medals = ["🥇", "🥈", "🥉"]
    for rank, (agent, s) in enumerate(classement):
        medal = medals[rank] if rank < 3 else "  "
        print(f"  {medal} {agent:<12} {s['points']:>4}  "
              f"{s['wins']:>3}V  {s['draws']:>3}N  {s['losses']:>3}D")

    return classement


# ============================================================
#  MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Tournoi entre agents Reversi")
    parser.add_argument("--quick", action="store_true",
                        help="Mode rapide (10 parties, 100 simulations)")
    parser.add_argument("--agent1", default=None,
                        help="Nom du 1er agent pour un duel : Random / FlatMCTS / MCTS")
    parser.add_argument("--agent2", default=None,
                        help="Nom du 2e agent pour un duel")
    parser.add_argument("--games", type=int, default=20,
                        help="Nombre de parties par duel (défaut: 20)")
    parser.add_argument("--simu", type=int, default=200,
                        help="Simulations Monte-Carlo par coup (défaut: 200)")
    args = parser.parse_args()

    if REVERSI_CLASS is None:
        print("Impossible de lancer le tournoi sans Reversi. Arrêt.")
        return

    n_games = 10 if args.quick else args.games
    nb_simu = 100 if args.quick else args.simu

    # Agents disponibles
    available = ["Random"]
    if MCTS_AVAILABLE:
        available += ["FlatMCTS", "MCTS"]

    print(f"Agents disponibles : {', '.join(available)}")
    print(f"Parties / duel : {n_games}  |  Simulations / coup : {nb_simu}")

    if args.agent1 and args.agent2:
        # Duel spécifique
        duel(args.agent1, args.agent2, n_games=n_games, nb_simu=nb_simu)
    else:
        # Tournoi complet
        round_robin(available, n_games=n_games, nb_simu=nb_simu)


if __name__ == "__main__":
    main()

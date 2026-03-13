"""
tournament.py — Comparaison et tournoi entre les agents Reversi
================================================================
Agents disponibles :
  - Random     : coups aléatoires parmi les coups valides
  - FlatMCTS   : Monte-Carlo plat (simulation pure par coup)
  - MCTS       : MCTS arborescent avec rollout biaisé (coins > bords > random)

Usage :
  python tournament.py                           # tournoi complet round-robin
  python tournament.py --quick                   # rapide (10 parties, 100 simu)
  python tournament.py --agent1 Random --agent2 MCTS
  python tournament.py --games 30 --simu 500
  python tournament.py --verbose                 # affiche le plateau
"""

import argparse
import time
from collections import defaultdict

from reversi import Reversi, play_game
from agent_random import AgentRandom
from agents_mcts import AgentFlatMCTS, AgentMCTS

AGENT_NAMES = ["Random", "FlatMCTS", "MCTS"]

# ============================================================
#  FABRIQUE D'AGENTS
# ============================================================

def make_agent(name: str, board: Reversi, nb_simu: int = 200):
    n = name.lower()
    if n == "random":
        return AgentRandom(board)
    elif n == "flatmcts":
        return AgentFlatMCTS(board, nb_simu)
    elif n == "mcts":
        return AgentMCTS(board, nb_simu=nb_simu)
    else:
        raise ValueError(f"Agent inconnu : '{name}'. Choix : {AGENT_NAMES}")


# ============================================================
#  DUEL
# ============================================================

def duel(name1: str, name2: str, n_games: int = 20,
         nb_simu: int = 200, verbose: bool = False) -> dict:
    """Affronte name1 vs name2 sur n_games parties avec alternance des couleurs."""
    wins1 = wins2 = draws = 0

    print(f"\n  ⚔  {name1}  vs  {name2}  —  {n_games} parties  |  {nb_simu} simul/coup")
    print("  " + "─" * 54)

    for i in range(n_games):
        board = Reversi()

        if i % 2 == 0:
            a1 = make_agent(name1, board, nb_simu)
            a2 = make_agent(name2, board, nb_simu)
            swap = False
        else:
            a1 = make_agent(name2, board, nb_simu)
            a2 = make_agent(name1, board, nb_simu)
            swap = True

        t0 = time.perf_counter()
        score = play_game(board, a1, a2, display=verbose)
        dt = time.perf_counter() - t0

        raw = 1 if score > 0 else (-1 if score < 0 else 0)
        result = -raw if swap else raw

        if result == 1:
            wins1 += 1
            sym = f"✓  {name1} gagne"
        elif result == -1:
            wins2 += 1
            sym = f"✗  {name2} gagne"
        else:
            draws += 1
            sym = "=  nul"

        print(f"  Partie {i+1:02d}/{n_games}  {sym:<22}  score={score:+d}  ({dt:.1f}s)")

    total = wins1 + wins2 + draws
    pct1 = 100 * wins1 / total if total else 0
    pct2 = 100 * wins2 / total if total else 0

    print(f"\n  ┌─ Résultats ──────────────────────────────────────┐")
    print(f"  │  {name1:<14} {wins1:2d} victoires  ({pct1:.0f}%)              │")
    print(f"  │  {name2:<14} {wins2:2d} victoires  ({pct2:.0f}%)              │")
    print(f"  │  Nuls          {draws:2d}                                │")
    print(f"  └────────────────────────────────────────────────────┘")

    return {
        "agent1": name1, "agent2": name2,
        "wins1": wins1, "wins2": wins2, "draws": draws,
        "winrate1": wins1 / total if total else 0,
        "winrate2": wins2 / total if total else 0,
    }


# ============================================================
#  TOURNOI ROUND-ROBIN
# ============================================================

def round_robin(agents: list, n_games: int = 20, nb_simu: int = 200) -> list:
    print("\n" + "═" * 60)
    print("  TOURNOI ROUND-ROBIN — Reversi Bots")
    print(f"  Agents : {', '.join(agents)}")
    print(f"  {n_games} parties / duel  |  {nb_simu} simulations / coup")
    print("═" * 60)

    scores = defaultdict(lambda: {"points": 0, "wins": 0, "losses": 0, "draws": 0})

    for i, a1 in enumerate(agents):
        for a2 in agents[i + 1:]:
            r = duel(a1, a2, n_games=n_games, nb_simu=nb_simu)
            scores[a1]["wins"]   += r["wins1"]
            scores[a1]["losses"] += r["wins2"]
            scores[a1]["draws"]  += r["draws"]
            scores[a1]["points"] += 3 * r["wins1"] + r["draws"]
            scores[a2]["wins"]   += r["wins2"]
            scores[a2]["losses"] += r["wins1"]
            scores[a2]["draws"]  += r["draws"]
            scores[a2]["points"] += 3 * r["wins2"] + r["draws"]

    print("\n" + "═" * 60)
    print("  CLASSEMENT FINAL")
    print("═" * 60)
    print(f"  {'Agent':<14} {'Pts':>5} {'V':>4} {'N':>4} {'D':>4}  Winrate")
    print("  " + "─" * 46)

    classement = sorted(scores.items(), key=lambda x: x[1]["points"], reverse=True)
    medals = ["🥇", "🥈", "🥉"]

    for rank, (agent, s) in enumerate(classement):
        medal = medals[rank] if rank < 3 else "  "
        total = s["wins"] + s["losses"] + s["draws"]
        wr = s["wins"] / total * 100 if total else 0
        print(f"  {medal} {agent:<12} {s['points']:>5}  "
              f"{s['wins']:>3}V  {s['draws']:>3}N  {s['losses']:>3}D  {wr:.0f}%")

    return classement


# ============================================================
#  MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Tournoi entre agents Reversi")
    parser.add_argument("--quick", action="store_true",
                        help="Mode rapide : 10 parties, 100 simulations")
    parser.add_argument("--agent1", default=None,
                        help="Agent 1 pour un duel : Random / FlatMCTS / MCTS")
    parser.add_argument("--agent2", default=None,
                        help="Agent 2 pour un duel")
    parser.add_argument("--games", type=int, default=20,
                        help="Nombre de parties par duel (défaut : 20)")
    parser.add_argument("--simu", type=int, default=200,
                        help="Simulations Monte-Carlo par coup (défaut : 200)")
    parser.add_argument("--verbose", action="store_true",
                        help="Affiche le plateau après chaque coup")
    args = parser.parse_args()

    n_games = 10  if args.quick else args.games
    nb_simu = 100 if args.quick else args.simu

    print(f"\n  Agents disponibles : {', '.join(AGENT_NAMES)}")
    print(f"  Parties / duel : {n_games}  |  Simulations / coup : {nb_simu}")

    if args.agent1 and args.agent2:
        duel(args.agent1, args.agent2,
             n_games=n_games, nb_simu=nb_simu, verbose=args.verbose)
    else:
        round_robin(AGENT_NAMES, n_games=n_games, nb_simu=nb_simu)


if __name__ == "__main__":
    main()

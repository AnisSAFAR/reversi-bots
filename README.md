# Reversi Bots — IA & Monte-Carlo

Agents intelligents pour le jeu **Reversi (Othello)** — Sorbonne Université, cours d'IA.

## Structure du projet

```
reversi-bots/
├── reversi.py          # Moteur numpy (plateau 8x8, play_game)
├── bitreversi.py       # Moteur bitboard (représentation entière 64 bits)
├── agent_random.py     # Agent aléatoire — baseline
├── mc_utils.py         # Utilitaires Monte-Carlo (rollout, simu_mc, masques)
├── bandit.py           # Algorithmes multi-bandits (Glouton, ε-greedy, UCB)
├── agents_mcts.py      # Agents MCTS (FlatMCTS + MCTS arborescent)
├── tournament.py       # Tournoi et comparaison des agents
└── README.md
```

## Agents implémentés

| Agent | Fichier | Description |
|-------|---------|-------------|
| `AgentRandom` | `agent_random.py` | Coup valide aléatoire — baseline |
| `AgentFlatMCTS` | `agents_mcts.py` | Monte-Carlo plat : simule N parties par coup |
| `AgentMCTS` | `agents_mcts.py` | MCTS arborescent + rollout biaisé (coins → bords → random) |
| `AgentGlouton` | `bandit.py` | Exploitation pure (meilleure moyenne) |
| `AgentEpsilon` | `bandit.py` | ε-greedy (ε=0.1) |
| `AgentUCB` | `bandit.py` | Upper Confidence Bound |

## Lancer un tournoi

```bash
# Tournoi complet round-robin entre tous les agents
python tournament.py

# Mode rapide (10 parties, 100 simulations/coup)
python tournament.py --quick

# Duel spécifique
python tournament.py --agent1 Random --agent2 MCTS

# Paramètres personnalisés
python tournament.py --games 30 --simu 500

# Voir le plateau après chaque coup
python tournament.py --agent1 Random --agent2 FlatMCTS --verbose
```

> **Note sur les temps** : FlatMCTS et MCTS sont lents par nature —
> chaque coup nécessite N simulations complètes. `--simu 50` suffit pour tester.

## Dépendances

```bash
pip install numpy
```

## Résultats attendus

```
🥇 MCTS       > FlatMCTS  >  Random
```

Le MCTS arborescent surpasse le Monte-Carlo plat grâce à la réutilisation de l'arbre
de recherche et à la priorité accordée aux coins (cases stratégiques au Reversi).

## Auteur

**Anis SAFAR** — L3 Informatique → M1 SSI, Sorbonne Université  
[anissafar.github.io](https://anissafar.github.io) · [github.com/AnisSAFAR](https://github.com/AnisSAFAR)

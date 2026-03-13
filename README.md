# Reversi Bots — IA & Monte-Carlo

Implémentation de plusieurs agents intelligents pour le jeu **Reversi (Othello)** dans le cadre du cours d'IA à Sorbonne Université.

## Structure

```
reversi-bots/
├── agent_random.py     # Agent aléatoire (baseline)
├── mc_utils.py         # Utilitaires Monte-Carlo (rollout, simulations)
├── bandit.py           # Algorithmes multi-bandits (Glouton, ε-greedy, UCB)
├── agents_mcts.py      # Agents MCTS (Flat Monte-Carlo + MCTS arborescent)
├── tournament.py       # Tournoi et comparaison des agents
└── README.md
```

## Agents implémentés

### `AgentRandom` (`agent_random.py`)
Joue un coup valide au hasard. Sert de **baseline** pour évaluer les autres agents.

### `AgentFlatMCTS` (`agents_mcts.py`)
Monte-Carlo **plat** : pour chaque coup légal, simule `nb_simu` parties aléatoires et choisit le coup avec le meilleur taux de victoire.

### `AgentMCTS` (`agents_mcts.py`)
**MCTS arborescent** complet avec les 4 phases classiques :
- **Sélection** — UCB1 pour naviguer dans l'arbre
- **Expansion** — ajout d'un nouveau nœud
- **Simulation** — rollout biaisé (priorité coins → bords → aléatoire)
- **Rétropropagation** — mise à jour des statistiques

### Agents Bandit (`bandit.py`)
Algorithmes multi-bandits pour l'exploration/exploitation :
- `AgentBanditRandom` — sélection aléatoire
- `AgentGlouton` — exploitation pure (meilleure moyenne)
- `AgentEpsilon` — ε-greedy (exploration avec probabilité ε=0.1)
- `AgentUCB` — Upper Confidence Bound

## Lancer un tournoi

```bash
# Tournoi complet entre tous les agents (round-robin)
python tournament.py

# Mode rapide (10 parties, 100 simulations)
python tournament.py --quick

# Duel spécifique
python tournament.py --agent1 Random --agent2 MCTS

# Personnaliser le nombre de parties et simulations
python tournament.py --games 30 --simu 500
```

## Dépendances

```bash
pip install numpy
```

Le fichier `reversi.py` ou `bitreversi.py` (moteur du jeu) doit être présent dans le même dossier.

## Résultats attendus

| Agent | Force estimée |
|-------|--------------|
| Random | Baseline |
| FlatMCTS (200 simu) | ++ |
| MCTS (200 simu) | +++ |

Le MCTS arborescent avec rollout biaisé surpasse généralement le Monte-Carlo plat grâce à la réutilisation de l'arbre de recherche et à la priorité accordée aux coins (cases stratégiques au Reversi).

## Auteur
**Anis SAFAR** — L3 Informatique, Sorbonne Université  
[anissafar.github.io](https://anissafar.github.io) · [GitHub](https://github.com/AnisSAFAR)

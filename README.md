# OrDomino

Un lanceur de testsuite Python, configurable, avec gestion de dépendances entre
suites (DAG) et génération d'une trace XML exploitable ensuite dans une UI web.

## Pourquoi ce projet

Dans mes projets scolaires (ex: **Tiger**, avec ses suites lexer / parser /
binding / type-checker, **42sh**, avec toutes les catégories), je me retrouvais
à retaper à chaque fois la même mécanique : lancer les tests dans le bon ordre,
ne pas lancer le parser si le lexer est cassé, bricoler un petit script pour
orchestrer tout ça.

`OrDomino` existe pour ne plus jamais refaire ce travail : un seul outil,
installé une fois, réutilisable sur n'importe quel projet — il suffit d'y
ajouter un fichier `ordomino.yaml` qui décrit les suites et leurs
dépendances.

## Installation

Le launcher est un package Python installable, séparé de tes projets. Aucun
code n'est copié dans les repos qui l'utilisent : ils contiennent seulement
leur fichier `ordomino.yaml`.

```bash
# depuis GitHub, version taggée (recommandé)
pipx install git+https://github.com/<user>/ordomino.git@v0.1.0

# ou la dernière version sur main
pipx install git+https://github.com/<user>/ordomino.git
```

En développement (modifs prises en compte immédiatement) :

```bash
git clone https://github.com/<user>/ordomino.git
pip install -e ./ordomino
```

## Utilisation rapide

Dans un projet, à la racine, un fichier `ordomino.yaml` :

```yaml
defaults:
  timeout: 60

suites:
  lexer:
    runner: tests/lexer/run.sh
    depends_on: []

  parser:
    runner: tests/parser/run.sh
    depends_on: [lexer]

  semantic:
    runner: tests/semantic/run.sh
    depends_on: [parser]

  codegen:
    runner: tests/codegen/run.sh
    depends_on: [parser, semantic]
```

Puis :

```bash
ordomino run                 # exécute tout le DAG dans l'ordre
ordomino run --only parser   # exécute une seule suite (sans ses dépendances)
ordomino run --from parser   # exécute cette suite + tout ce qui en dépend
ordomino run --dry-run       # affiche l'ordre prévu et ce qui serait skip
ordomino validate            # vérifie le YAML (cycles, suites manquantes...)
```

## Concepts

### DAG de dépendances

Chaque suite déclare `depends_on: [...]`. Ce n'est pas une simple chaîne : une
suite peut dépendre de plusieurs autres (ex: `codegen` dépend à la fois de
`parser` et de `semantic`). Le launcher calcule un ordre topologique
d'exécution, et détecte les dépendances circulaires au moment du `validate`.

### Convention `runner`

En v1 (MVP), chaque suite pointe vers un `runner` (script ou exécutable),
peu importe le langage. Convention simple : **exit code 0 = succès**, tout
le reste = échec. Ça permet d'utiliser `OrDomino` sur des projets Python,
C, Java... sans rien connaître de leur framework de test interne.

### Propagation d'échec

Si une suite échoue, ses dépendantes sont **skip** par défaut (pas
exécutées), et le rapport final distingue clairement "échec réel" de
"skip à cause d'une dépendance".

## Fichier `ordomino.yaml` — référence complète (v1, MVP)

| Champ | Niveau | Obligatoire | Description |
|---|---|---|---|
| `defaults.timeout` | global | non | Timeout par défaut (secondes) pour toute suite sans `timeout` propre |
| `suites.<nom>.runner` | suite | **oui** | Script/exécutable qui lance les tests de la suite |
| `suites.<nom>.depends_on` | suite | non (défaut `[]`) | Liste des suites requises avant de lancer celle-ci |
| `suites.<nom>.enabled` | suite | non (défaut `true`) | Désactive une suite sans la supprimer de la config |
| `suites.<nom>.args` | suite | non | Arguments passés au `runner` |
| `suites.<nom>.working_dir` | suite | non (défaut `.`) | Dossier d'exécution du runner |
| `suites.<nom>.timeout` | suite | non | Override du timeout global pour cette suite |

## Roadmap (v2+)

Ces fonctionnalités sont pensées et documentées mais volontairement absentes
du MVP, pour valider le moteur DAG + exécution avant d'ajouter du confort :

- **Trace XML + historique** : chaque run écrit dans `history/<date>/trace.xml`
  (graphe de dépendances tel qu'exécuté, timestamps, statut par suite/test,
  stdout/stderr capturé). Objectif : une page web séparée qui lit ces traces
  pour afficher l'état des runs et leur historique dans le temps.
- **Artifacts** : copie de fichiers (logs, coverage...) dans
  `history/<date>/artifacts/<suite>/`, au même endroit que la trace, pour
  que l'UI web puisse tout retrouver ensemble.
- **Formats de résultat riches** : `result_format: junit | json | tap` en plus
  du simple exit code, pour récupérer le détail test-par-test plutôt qu'un
  simple pass/fail de la suite entière.
- **`on_dependency_failure`** : `skip` (défaut) / `warn` (exécute quand même,
  marqué "at risk") / `fail-fast` (arrête tout le run).
- **`min_pass_rate`** : tolérance de réussite partielle d'une dépendance
  (ex: 95% du lexer suffit pour lancer le parser).
- **Hooks** : `before_suite` / `after_suite` par suite, et `before_all` /
  `after_all` / `on_failure` globaux (ex: compiler avant de tester le
  codegen).
- **Tags et profils** : `tags: [fast, core, slow]` par suite, et des
  `profiles` nommés (`ci`, `full`...) pour lancer des sous-ensembles du DAG
  sans changer la config à chaque fois.
- **Parallélisation** : exécuter en parallèle les suites indépendantes du
  DAG (calculées via le tri topologique).
- **Cache / re-run intelligent** : ne relancer une suite que si les fichiers
  concernés ont changé (hash de fichiers), + mode watch.
- **Auto-discovery** : scanner un dossier `tests/` pour proposer un
  squelette de config YAML à valider/compléter sur un nouveau projet.
- **Binaire autonome** : packaging via `pyinstaller`/`shiv` si besoin
  d'utiliser `OrDomino` sans environnement Python préinstallé.

## Structure du repo

```
OrDomino/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── OrDomino/
│       ├── __init__.py
│       ├── cli.py        # points d'entrée : run / validate / list
│       ├── dag.py        # résolution des dépendances, tri topologique
│       ├── config.py     # parsing + validation du YAML
│       └── runner.py     # exécution d'une suite (subprocess, timeout, exit code)
└── tests/
    └── ...
```

## Statut

Projet personnel, en développement. Le MVP (DAG + exécution + exit code)
est la priorité ; les fonctionnalités listées en roadmap seront ajoutées au
fur et à mesure des besoins réels rencontrés sur mes projets.

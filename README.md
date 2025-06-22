# Projet d'Optimisation d'Ordonnancement de Tâches en Usine

Ce projet a pour but de développer et comparer des heuristiques pour résoudre un problème d'ordonnancement de tâches (jobs) sur un parc de machines. L'objectif est de trouver des plannings qui optimisent à la fois la durée totale (makespan) et la consommation d'énergie, en tenant compte des contraintes de précédence, des temps de préparation des machines (setup) et de leur consommation énergétique variable.

## Prérequis

Pour exécuter ce projet, vous aurez besoin de :

- **Python** : Version 3.10 ou supérieure (recommandé : 3.11).
- **Un IDE (Environnement de Développement Intégré)** : [PyCharm](https://www.jetbrains.com/pycharm/) ou [Visual Studio Code](https://code.visualstudio.com/) sont fortement recommandés pour leur gestion des environnements virtuels et leurs outils de débogage.
- **Les bibliothèques Python nécessaires** : Pour l'instant, seule `matplotlib` est requise pour la génération des diagrammes de Gantt.

## Installation et Configuration

Il est fortement conseillé d'utiliser un environnement virtuel Python pour isoler les dépendances de ce projet et éviter les conflits avec d'autres projets sur votre machine.

### 1. Cloner le Dépôt

Si vous êtes sur GitHub, clonez le projet sur votre machine locale :
```bash
git clone [URL_DE_VOTRE_DEPOT_GIT]
cd [NOM_DU_DOSSIER_DU_PROJET]
```

### 2. Créer et Activer un Environnement Virtuel

Un environnement virtuel (`venv`) est un dossier qui contient une installation de Python spécifique à votre projet.

**Sur macOS ou Linux :**
```bash
# Créer l'environnement virtuel (un dossier nommé "venv" sera créé)
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate
```
*(Votre invite de commande devrait maintenant afficher `(venv)` au début pour indiquer que l'environnement est actif.)*

**Sur Windows (CMD ou PowerShell) :**
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\activate
```
*(Votre invite de commande devrait maintenant afficher `(venv)` au début.)*

### 3. Installer les Dépendances

Créez un fichier `requirements.txt` à la racine de votre projet avec le contenu suivant :
```
matplotlib
```

Ensuite, avec votre environnement virtuel activé, installez les bibliothèques nécessaires :
```bash
pip install -r requirements.txt
```

## Exécution du Projet

Le projet contient des blocs d'exécution d'exemple dans les fichiers `constructive.py` et `local_search.py`. Pour les lancer, assurez-vous que votre terminal est à la racine du projet et que l'environnement virtuel est activé.

Exemple pour lancer les heuristiques constructives :
```bash
# Cette commande exécute le bloc if __name__ == "__main__": du fichier constructive.py
python -m src.scheduling.optim.constructive
```
*(Note : Le chemin `-m src.scheduling.optim.constructive` peut dépendre de la structure exacte de votre projet et de la configuration de votre PYTHONPATH dans votre IDE).*

Les diagrammes de Gantt générés seront sauvegardés à la racine du projet sous forme de fichiers `.png`.
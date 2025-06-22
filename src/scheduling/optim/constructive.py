'''
Constructive heuristics that returns preferably **feasible** solutions.

@author: Vassilissa Lehoux
'''
from typing import Dict
import random

from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution
from src.scheduling.optim.heuristics import Heuristic


class Greedy(Heuristic):
    '''
    A deterministic greedy method to return a solution.
    '''

    def __init__(self, params: Dict=dict()):
        '''
        Constructor
        @param params: The parameters of your heuristic method if any as a
               dictionary. Implementation should provide default values in the function.
        '''
        super().__init__(params)

    def run(self, instance: Instance, params: Dict=dict()) -> Solution:
        '''
        Computes a solution for the given instance.
        Implementation should provide default values in the function
        (the function will be evaluated with an empty dictionary).

        @param instance: the instance to solve
        @param params: the parameters for the run
        '''
        # Stratégie de sélection déterministe : trier par ID et prendre la première.
        deterministic_selection = lambda ops: sorted(ops, key=lambda o: o.operation_id)[0]

        return self._construct_solution(instance, deterministic_selection)


class NonDeterminist(Heuristic):
    '''
    Heuristic that returns different values for different runs with the same parameters
    (or different values for different seeds and otherwise same parameters)
    '''

    def __init__(self, params: Dict=dict()):
        '''
        Constructor
        @param params: The parameters of your heuristic method if any as a
               dictionary. Implementation should provide default values in the function.
        '''
        super().__init__(params)

    def run(self, instance: Instance, params: Dict=dict()) -> Solution:
        '''
        Computes a solution for the given instance.
        Implementation should provide default values in the function
        (the function will be evaluated with an empty dictionary).

        @param instance: the instance to solve
        @param params: the parameters for the run
        '''
        # Initialisation de la solution
        # Stratégie de sélection non-déterministe : choisir au hasard.
        random_selection = lambda ops: random.choice(ops)

        return self._construct_solution(instance, random_selection)


if __name__ == "__main__":
    # Cet exemple est fourni pour jouer avec les heuristiques. Il est nécessaire
    # d'avoir le dossier de tests et les données correspondantes.
    # On importe les données de test
    import os
    from src.scheduling.tests.test_utils import TEST_FOLDER_DATA
    from matplotlib import pyplot as plt

    inst = Instance.from_file(os.path.join(TEST_FOLDER_DATA, "jsp1"))

    # --- Heuristique gloutonne ---
    print("--- Lancement de l'heuristique gloutonne déterministe ---")
    greedy_heuristique = Greedy()
    solution_greedy = greedy_heuristique.run(inst)
    print(solution_greedy)

    # Génération du Gantt pour la solution gloutonne
    try:
        print("Création du Gantt pour la solution gloutonne...")
        plt_greedy = solution_greedy.gantt("viridis")
        plt_greedy.savefig("gantt_greedy.png")
        plt_greedy.close()  # Important pour nettoyer la figure
        print("-> Gantt sauvegardé dans 'gantt_greedy.png'")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du Gantt : {e}")

    # --- Heuristique non-déterministe (Run 1) ---
    inst = Instance.from_file(os.path.join(TEST_FOLDER_DATA, "jsp1"))

    print("\n--- Lancement de l'heuristique non-déterministe (Run 1) ---")
    nondet_heuristique = NonDeterminist()
    solution_nondet1 = nondet_heuristique.run(inst)
    print(solution_nondet1)

    # Génération du Gantt pour la première solution non-déterministe
    try:
        print("Création du Gantt pour la Run 1 non-déterministe...")
        plt_nondet1 = solution_nondet1.gantt("plasma")
        plt_nondet1.savefig("gantt_nondet1.png")
        plt_nondet1.close()
        print("-> Gantt sauvegardé dans 'gantt_nondet1.png'")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du Gantt : {e}")

    # --- Heuristique non-déterministe (Run 2) ---
    inst = Instance.from_file(os.path.join(TEST_FOLDER_DATA, "jsp1"))

    print("\n--- Lancement de l'heuristique non-déterministe (Run 2) ---")
    solution_nondet2 = nondet_heuristique.run(inst)
    print(solution_nondet2)

    # Génération du Gantt pour la seconde solution non-déterministe
    try:
        print("Création du Gantt pour la Run 2 non-déterministe...")
        plt_nondet2 = solution_nondet2.gantt("magma")
        plt_nondet2.savefig("gantt_nondet2.png")
        plt_nondet2.close()
        print("-> Gantt sauvegardé dans 'gantt_nondet2.png'")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du Gantt : {e}")

    # --- Comparaison ---
    if solution_nondet1.cmax != solution_nondet2.cmax or solution_nondet1.total_energy_consumption != solution_nondet2.total_energy_consumption:
        print("\nLes deux solutions non-déterministes sont bien différentes, comme attendu.")
    else:
        print("\nAttention : les deux solutions non-déterministes sont identiques (cela peut arriver par hasard).")

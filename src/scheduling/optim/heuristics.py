'''
Mother class for heuristics.

@author: Vassilissa Lehoux
'''
from typing import Dict, Callable, List
import random

from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution
from src.scheduling.instance.operation import Operation

class Heuristic(object):
    '''
    classdocs
    '''

    def __init__(self, params: Dict=dict()):
        '''
        Constructor
        @param params: The parameters of your heuristic method if any as a
               dictionary. Implementation should provide default values in the function.
        '''
        self.params = params

    def run(self, instance: Instance, params: Dict=dict()) -> Solution:
        '''
        Computes a solution for the given instance.
        Implementation should provide default values in the function
        (the function will be evaluated with an empty dictionary).
        @param instance: the instance to solve
        @param params: the parameters for the run
        '''
        raise NotImplementedError("Cette méthode doit être implémentée par les classes filles.")

    def _construct_solution(self, instance: Instance,
                            selection_strategy: Callable[[List[Operation]], Operation]) -> Solution:
        """
        Méthode qui contient la logique commune de construction d'une solution pour les heuristiques se
        trouvant dans le fichier constructive.py.
        A savoir l'algorithme glouton et le non déterministe.

        @param instance: l'instance du problème.
        @param selection_strategy: une fonction qui prend une liste d'opérations
               disponibles et en retourne une seule selon une stratégie précise
               (ex: la première, une au hasard, etc.).
        """
        # Initialisation de la solution
        solution = Solution(instance)

        # Tant qu'il y a des opérations disponibles à planifier
        while len(solution.available_operations) > 0:
            # On choisit l'opération à planifier en fonction de la stratégie de sélection donnée en paramètre
            op_to_schedule = selection_strategy(solution.available_operations)

            # Le reste du code est la logique commune de recherche de la meilleure machine
            best_machine = None
            earliest_completion_time = float('inf')

            # On va parcourir les machines disponibles pour cette opération et trouver la première sur laquelle on peut la planifier
            for machine_id in op_to_schedule.get_machine_options().keys():
                machine = instance.get_machine(machine_id)

                # On calcule le temps de début possible pour l'opération en fonction de la disponibilité de la machine et du temps de préparation
                pred_ready_time = op_to_schedule.min_start_time
                if not machine.scheduled_operations:
                    machine_ready_time = machine.set_up_time
                else:
                    machine_ready_time = machine.available_time
                start_time = max(pred_ready_time, machine_ready_time)

                # On calcule la durée de l'opération sur cette machine
                duration = op_to_schedule.get_processing_time_on_machine(machine_id)
                # On calcule le temps de fin de l'opération
                completion_time = start_time + duration
                # On cherche la machine qui permet de finir l'opération le plus tôt
                if completion_time < earliest_completion_time:
                    earliest_completion_time = completion_time
                    best_machine = machine

            # Si on a trouvé une machine, on planifie l'opération dessus
            if best_machine:
                solution.schedule(op_to_schedule, best_machine)
            else:
                raise RuntimeError(f"Aucune machine trouvée pour l'opération {op_to_schedule.operation_id}")

        return solution
        

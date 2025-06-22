'''
Neighborhoods for solutions.
They must derive from the Neighborhood class.

@author: Vassilissa Lehoux
'''
import copy
import random
from typing import Dict, Iterator

from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution


class Neighborhood(object):
    '''
    Base neighborhood class for solutions of a given instance.
    Do not modify!!!
    '''

    def __init__(self, instance: Instance, params: Dict=dict()):
        '''
        Constructor
        '''
        self._instance = instance

    def best_neighbor(self, sol: Solution) -> Solution:
        '''
        Returns the best solution in the neighborhood of the solution.
        Can be the solution itself.
        '''
        raise "Not implemented error"

    def first_better_neighbor(self, sol: Solution):
        '''
        Returns the first solution in the neighborhood of the solution
        that improves other it and the solution itself if none is better.
        '''
        raise "Not implemented error"


class MyNeighborhood1(Neighborhood):
    '''
    Échange de deux opérations adjacentes sur la même machine.
    '''

    def __init__(self, instance: Instance, params: Dict=dict()):
        '''
        Constructor
        '''
        super().__init__(instance, params)

    def best_neighbor(self, sol: Solution) -> Solution:
        '''
        Returns the best solution in the neighborhood of the solution.
        Can be the solution itself.
        '''
        best_sol = sol
        best_obj = sol.objective
        for neighbor in self._iter_neighbors(sol):
            if neighbor.objective < best_obj:
                best_obj = neighbor.objective
                best_sol = neighbor
        return best_sol

    def first_better_neighbor(self, sol: Solution) -> Solution:
        '''
        Returns the first solution in the neighborhood of the solution
        that improves other it and the solution itself if none is better.
        '''
        current_obj = sol.objective
        for neighbor in self._iter_neighbors(sol):
            if neighbor.objective < current_obj:
                return neighbor
        return sol

    def _iter_neighbors(self, sol: Solution) -> Iterator[Solution]:
        """Méthode qui contient la logique métier de l'échange de deux opérations adjacentes sur la même machine."""

        for machine in self._instance.machines:
            # On ne peut faire l'échange que si la machine a au moins deux opérations planifiées
            if len(machine.scheduled_operations) < 2:
                continue

            # On parcourt les opérations planifiées sur la machine
            for i in range(len(machine.scheduled_operations) - 1):
                # On prend les deux opérations adjacentes
                op1 = machine.scheduled_operations[i]
                op2 = machine.scheduled_operations[i + 1]

                # On peut échanger les opérations si l'opération suivante peut commencer avant que l'opération précédente ne se termine
                if op2.min_start_time <= op1.start_time:
                    neighbor_sol = copy.deepcopy(sol)
                    m_copy = neighbor_sol.inst.get_machine(machine.machine_id)

                    # On inverse les opérations dans la liste
                    m_copy.scheduled_operations[i], m_copy.scheduled_operations[i + 1] = \
                        m_copy.scheduled_operations[i + 1], m_copy.scheduled_operations[i]

                    # Il faut replanifier les opérations à partir de l'opération échangée
                    previous_op_end_time = m_copy.scheduled_operations[i - 1].end_time if i > 0 else 0

                    # On replanifie l'opération 1
                    for j in range(i, len(m_copy.scheduled_operations)):
                        op_to_reschedule = m_copy.scheduled_operations[j]
                        start_time = max(op_to_reschedule.min_start_time, previous_op_end_time)
                        op_to_reschedule.schedule(m_copy.machine_id, start_time, check_success=False)
                        previous_op_end_time = op_to_reschedule.end_time

                    neighbor_sol._objective_value = None

                    yield neighbor_sol


class MyNeighborhood2(Neighborhood):
    '''
    Déplace une opération vers une autre machine.
    Oon choisit une opération au hasard et on teste toutes ses autres machines possibles
    '''

    def __init__(self, instance: Instance, params: Dict=dict()):
        '''
        Constructor
        '''
        super().__init__(instance, params)

    def best_neighbor(self, sol: Solution) -> Solution:
        '''
        Returns the best solution in the neighborhood of the solution.
        Can be the solution itself.
        '''
        best_sol = sol
        best_obj = sol.objective
        for neighbor in self._iter_neighbors(sol):
            if neighbor.objective < best_obj:
                best_obj = neighbor.objective
                best_sol = neighbor
        return best_sol

    def first_better_neighbor(self, sol: Solution) -> Solution:
        '''
        Returns the first solution in the neighborhood of the solution
        that improves other it and the solution itself if none is better.
        '''
        current_obj = sol.objective
        for neighbor in self._iter_neighbors(sol):
            if neighbor.objective < current_obj:
                return neighbor
        return sol

    def _iter_neighbors(self, sol: Solution) -> Iterator[Solution]:
        """Méthode qui contient la logique métier de déplacement d'une opération vers une autre machine."""

        # On choisit une opération au hasard dans la solution
        op_to_move = random.choice(sol.all_operations)
        current_machine_id = op_to_move.assigned_to

        for new_machine_id in op_to_move.get_machine_options():
            # On ne peut pas déplacer l'opération sur la même machine
            if new_machine_id == current_machine_id:
                continue

            # Création d'une copie pour la modification
            neighbor_sol = copy.deepcopy(sol)
            op_copy = neighbor_sol.inst.get_operation(op_to_move.operation_id)
            old_machine_copy = neighbor_sol.inst.get_machine(current_machine_id)
            new_machine_copy = neighbor_sol.inst.get_machine(new_machine_id)

            # On retire l'opération et tous ses successeurs du même job
            ops_to_reschedule = []
            curr_op = op_copy
            while curr_op is not None:
                ops_to_reschedule.append(curr_op)
                # On retire l'op de sa machine actuelle dans la copie
                if curr_op.assigned:
                    m = neighbor_sol.inst.get_machine(curr_op.assigned_to)
                    if curr_op in m.scheduled_operations:
                        m.scheduled_operations.remove(curr_op)
                # On la réinitialise
                curr_op.reset()
                curr_op = curr_op.successors[0] if curr_op.successors else None

            # Il faut replanifier l'opération sur la nouvelle machine
            neighbor_sol.schedule(op_copy, new_machine_copy)

            # Il faut aussi replanifier toutes les opérations qui étaient planifiées après l'opération déplacée
            # On le fait sur la machine d'origine pour la simplicité
            for op_reschedule in ops_to_reschedule[1:]:
                original_machine_id_for_op = sol.inst.get_operation(op_reschedule.operation_id).assigned_to
                machine_to_use = neighbor_sol.inst.get_machine(original_machine_id_for_op)
                neighbor_sol.schedule(op_reschedule, machine_to_use)

            neighbor_sol._objective_value = None

            yield neighbor_sol
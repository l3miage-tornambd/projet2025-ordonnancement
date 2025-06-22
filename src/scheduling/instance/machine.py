'''
Machine on which operation are executed.

@author: Vassilissa Lehoux
'''
from typing import List
from src.scheduling.instance.operation import Operation


class Machine(object):
    '''
    Machine class.
    When operations are scheduled on the machine, contains the relative information. 
    '''

    def __init__(self, machine_id: int, set_up_time: int, set_up_energy: int, tear_down_time: int,
                 tear_down_energy:int, min_consumption: int, end_time: int):
        '''
        Constructor
        Machine is stopped at the beginning of the planning and need to
        be started before executing any operation.
        @param end_time: End of the schedule on this machine: the machine must be
          shut down before that time.
        '''
        self._machine_id : int = machine_id
        self._set_up_time : int = set_up_time
        self._set_up_energy : int = set_up_energy
        self._tear_down_time : int = tear_down_time
        self._tear_down_energy : int = tear_down_energy
        self._min_consumption : int = min_consumption
        self._max_end_time : int = end_time

        self._scheduled_operations : List[Operation] = []
        self._start_times : List[int] = []
        self._stop_times : List[int] = []

        self.reset()

    def reset(self):
        for op in self._scheduled_operations:
            op.reset()

        self._scheduled_operations: List[Operation] = []
        self._start_times: List[int] = []
        self._stop_times: List[int] = []

    @property
    def set_up_time(self) -> int:
        return self._set_up_time

    @property
    def tear_down_time(self) -> int:
        return self._tear_down_time

    @property
    def machine_id(self) -> int:
        return self._machine_id

    @property
    def scheduled_operations(self) -> List:
        '''
        Returns the list of the scheduled operations on the machine.
        '''
        return self._scheduled_operations

    @property
    def available_time(self) -> int:
        """
        Returns the next time at which the machine is available
        after processing its last operation of after its last set up.
        """
        # S'il n'y a pas d'opérations planifiées, la machine est disponible dès le début
        # Cas la machine a été démarrée mais n'a pas d'opération
        if len(self._start_times) > len(self._stop_times) and not self._scheduled_operations:
            return self._start_times[-1] + self._set_up_time

        # Cas la machine est en marche et a déjà des opérations
        if self._scheduled_operations:
            last_op = self._scheduled_operations[-1]
            return last_op.end_time

        # Cas la machine est éteinte, elle est dispo à partir du dernier arrêt.
        if self._stop_times:
            return self._stop_times[-1]

        # Cas initial, la machine est dispo à t=0
        return 0

    def add_operation(self, operation: Operation, start_time: int) -> int:
        '''
        Adds an operation on the machine, at the end of the schedule,
        as soon as possible after time start_time.
        Returns the actual start time.
        '''
        # Note importante : toute la logique métier a été déporté dans l'ochestrateur à savoir
        # la méthode schedule qui se trouve dans solution.py

        self._scheduled_operations.append(operation)
        self._scheduled_operations.sort(key=lambda op: op.start_time) # On garde les opérations triées par ordre de démarrage
        return start_time
  
    def stop(self, at_time):
        """
        Stops the machine at time at_time.
        """
        if not self._start_times:
            raise ValueError("Cannot stop a machine that has not been started.")

        if at_time < self.available_time:
            raise ValueError(
                f"Machine {self.machine_id} cannot be stopped at {at_time} because it is busy until {self.available_time}.")

        # On remplace la dernière heure d'arrêt (qui était la valeur par défaut)
        self._stop_times[-1] = at_time
        self._stop_times.sort()

    def start(self, at_time: int):
        # Méthode pour gérer l'ajout d'un démarrage de machine
        self._start_times.append(at_time)
        self._start_times.sort()
        self._stop_times.append(self._max_end_time) # On initialise le stop_time à l'horizon de la machine

    @property
    def working_time(self) -> int:
        '''
        Total time during which the machine is running
        '''
        if not self.start_times:
            return 0

        # Le nombre d'élément dans _start_times et _stop_times est toujours le même donc on peut les parcourir ensemble
        total_running_time = 0
        for start, stop in zip(self.start_times, self.stop_times):
            total_running_time += (stop - start)

        return total_running_time

    @property
    def start_times(self) -> List[int]:
        """
        Returns the list of the times at which the machine is started
        in increasing order
        """
        return self._start_times

    @property
    def stop_times(self) -> List[int]:
        """
        Returns the list of the times at which the machine is stopped
        in increasing order
        """
        return self._stop_times

    @property
    def total_energy_consumption(self) -> int:
        """
        Total energy consumption of the machine during planning exectution.
        """
        # Il y a le coup de démarrage et d'arrêt de la machine
        energy_setup = len(self.start_times) * self._set_up_energy
        energy_teardown = len(self.stop_times) * self._tear_down_energy

        # Il y a aussi l'énergie consommée par les opérations
        energy_processing = sum(op.energy for op in self._scheduled_operations)

        # Il y a l'énergie de la machine à vide
        # On calcule le temps de fonctionnement de la machine
        total_on_time = 0
        for i in range(len(self._stop_times)):
            total_on_time += self._stop_times[i] - self._start_times[i]

        # Pareil ici on calcul le temps de fonctionnement de la dernière opération si la machine est encore en marche pour calculer le temps à vide
        total_setup_time = len(self.start_times) * self._set_up_time
        total_teardown_time = len(self.stop_times) * self._tear_down_time

        # Pareil temps total de traitement des opérations pour le calcul du temps à vide
        total_processing_time = sum(op.processing_time for op in self._scheduled_operations)

        # Calcul du temps d'inactivité
        total_idle_time = total_on_time - total_setup_time - total_teardown_time - total_processing_time

        # Calcule de l'énergie consommée à vide
        energy_idle = max(0, total_idle_time) * self._min_consumption

        return energy_setup + energy_teardown + energy_processing + energy_idle

    def __str__(self):
        return f"M{self.machine_id}"

    def __repr__(self):
        return str(self)

'''
Operation of a job.
Its duration and energy consumption depends on the machine on which it is executed.
When operation is scheduled, its schedule information is updated.

@author: Vassilissa Lehoux
'''
from typing import List, Dict, Tuple, Optional


class OperationScheduleInfo(object):
    '''
    Informations known when the operation is scheduled
    '''

    def __init__(self, machine_id: int, start_time: int, duration: int, energy_consumption: int):
        self.machine_id : int = machine_id
        self.start_time : int = start_time
        self.duration : int = duration
        self.energy_consumption : int = energy_consumption


class Operation(object):
    '''
    Operation of the jobs
    '''

    def __init__(self, job_id, operation_id):
        '''
        Constructor
        '''
        self._job_id : int = job_id
        self._operation_id : int = operation_id
        self._processing_data: Dict[int, Tuple[int, int]] = {}  # {machine_id: (duration, energy)}
        self._predecessors: List[Operation] = []
        self._successors: List[Operation] = []
        self._schedule_info: Optional[OperationScheduleInfo] = None

    def __str__(self):
        '''
        Returns a string representing the operation.
        '''
        base_str = f"O{self.operation_id}_J{self.job_id}"
        if self._schedule_info:
            return base_str + f"_M{self.assigned_to}_ci{self.processing_time}_e{self.energy}"
        else:
            return base_str

    def __repr__(self):
        return str(self)

    def reset(self):
        '''
        Removes scheduling informations
        '''
        self._schedule_info = None

    def add_predecessor(self, operation):
        '''
        Adds a predecessor to the operation
        '''
        if operation not in self._predecessors:
            self._predecessors.append(operation)

    def add_successor(self, operation):
        '''
        Adds a successor operation
        '''
        if operation not in self._successors:
            self._successors.append(operation)

    def get_machine_options(self) -> Dict[int, Tuple[int, int]]:
        """Returns all machine options for this operation."""
        return self._processing_data

    def add_machine_option(self, machine_id: int, duration: int, energy: int) -> None:
        """
        Adds a machine option for the operation.
        @param machine_id: ID of the machine
        @param duration: processing time on the machine
        @param energy: energy consumption on the machine
        """
        self._processing_data[machine_id] = (duration, energy)

    @property
    def operation_id(self) -> int:
        return self._operation_id

    @property
    def job_id(self) -> int:
        return self._job_id

    @property
    def predecessors(self) -> List:
        """
        Returns a list of the predecessor operations
        """
        return self._predecessors

    @property
    def successors(self) -> List:
        '''
        Returns a list of the successor operations
        '''
        return self._successors

    @property
    def assigned(self) -> bool:
        '''
        Returns True if the operation is assigned
        and False otherwise
        '''
        return self._schedule_info is not None

    @property
    def assigned_to(self) -> int:
        '''
        Returns the machine ID it is assigned to if any
        and -1 otherwise
        '''
        return self._schedule_info.machine_id if self.assigned else -1

    @property
    def processing_time(self) -> int:
        '''
        Returns the processing time if is assigned,
        -1 otherwise
        '''
        return self._schedule_info.duration if self.assigned else -1

    @property
    def start_time(self) -> int:
        '''
        Returns the start time if is assigned,
        -1 otherwise
        '''
        return self._schedule_info.start_time if self.assigned else -1

    @property
    def end_time(self) -> int:
        '''
        Returns the end time if is assigned,
        -1 otherwise
        '''
        if not self.assigned:
            return -1
        return self.start_time + self.processing_time

    @property
    def energy(self) -> int:
        '''
        Returns the energy consumption if is assigned,
        -1 otherwise
        '''
        return self._schedule_info.energy_consumption if self.assigned else -1

    def is_ready(self, at_time) -> bool:
        '''
        Returns True if all the predecessors are assigned
        and processed before at_time.
        False otherwise
        '''
        for pred in self.predecessors:
            if not pred.assigned or pred.end_time > at_time:
                return False
        return True

    def schedule(self, machine_id: int, at_time: int, check_success=True) -> bool:
        '''
        Schedules an operation. Updates the schedule information of the operation
        @param check_success: if True, check if all the preceeding operations have
          been scheduled and if the schedule time is compatible
        '''
        if machine_id not in self._processing_data:
            return False

        if check_success and not self.is_ready(at_time):
            return False

        duration, energy = self._processing_data[machine_id]
        self._schedule_info = OperationScheduleInfo(machine_id, at_time, duration, energy)
        return True

    @property
    def min_start_time(self) -> int:
        '''
        Minimum start time given the precedence constraints
        '''
        if not self.predecessors:
            return 0

        predecessors_end_times = [p.end_time for p in self.predecessors]
        if not all(t != -1 for t in predecessors_end_times):
            return 0

        return max(predecessors_end_times) if predecessors_end_times else 0

    def schedule_at_min_time(self, machine_id: int, min_time: int) -> bool:
        '''
        Try and schedule the operation af or after min_time.
        Return False if not possible
        '''
        if machine_id not in self._processing_data:
            return False

        start_time = max(min_time, self.min_start_time)

        return self.schedule(machine_id, start_time, check_success=False)

    def get_processing_time_on_machine(self, machine_id: int) -> int:
        """
        Retourne la durée de traitement (processing time) de cette opération
        si elle était exécutée sur la machine spécifiée.
        Retourne une valeur très grande si la machine n'est pas une option valide.
        """
        if machine_id in self._processing_data:
            # La durée est le premier élément du tuple
            return self._processing_data[machine_id][0]
        else:
            # Si la machine ne peut pas exécuter cette opération, on retourne l'infini
            # pour que les calculs de type `min` ou `max` l'ignorent
            return float('inf')

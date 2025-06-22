'''
Job. It is composed of several operations.

@author: Vassilissa Lehoux
'''
from typing import List

from src.scheduling.instance.operation import Operation


class Job(object):
    '''
    Job class.
    Contains information on the next operation to schedule for that job
    '''

    def __init__(self, job_id: int):
        '''
        Constructor
        '''
        self._job_id : int = job_id
        self._operations: List[Operation] = []
        self._next_op_idx_to_schedule : int = 0
        
    @property
    def job_id(self) -> int:
        '''
        Returns the id of the job.
        '''
        return self._job_id

    def reset(self):
        '''
        Resets the planned operations
        '''
        for op in self._operations:
            op.reset()

        self._next_op_idx_to_schedule = 0

    @property
    def operations(self) -> List[Operation]:
        '''
        Returns a list of operations for the job
        '''
        return self._operations

    @property
    def next_operation(self) -> Operation:
        '''
        Returns the next operation to be scheduled
        '''
        if self.planned:
            return None

        return self._operations[self._next_op_idx_to_schedule]

    def schedule_operation(self):
        '''
        Updates the next_operation to schedule
        '''
        if not self.planned:
            self._next_op_idx_to_schedule += 1

    @property
    def planned(self):
        '''
        Returns true if all operations are planned
        '''
        return self._next_op_idx_to_schedule >= self.operation_nb

    @property
    def operation_nb(self) -> int:
        '''
        Returns the nb of operations of the job
        '''
        return len(self._operations)

    def add_operation(self, operation: Operation):
        '''
        Adds an operation to the job at the end of the operation list,
        adds the precedence constraints between job operations.
        '''
        if self._operations:
            last_op = self._operations[-1]
            last_op.add_successor(operation)
            operation.add_predecessor(last_op)

        self._operations.append(operation)

    @property
    def completion_time(self) -> int:
        '''
        Returns the job's completion time
        '''
        if not self.operations:
            return 0

        return self.operations[-1].end_time

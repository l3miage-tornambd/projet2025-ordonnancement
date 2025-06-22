'''
Information for the instance of the optimization problem.

@author: Vassilissa Lehoux
'''
from typing import List, Dict
import os
import csv

from src.scheduling.instance.job import Job
from src.scheduling.instance.operation import Operation
from src.scheduling.instance.machine import Machine


class Instance(object):
    '''
    classdocs
    '''

    def __init__(self, instance_name):
        '''
        Constructor
        '''
        self._instance_name = instance_name
        self._machines: List[Machine] = []
        self._jobs: List[Job] = []
        self._operations: List[Operation] = []

        self._machine_map: Dict[int, Machine] = {}
        self._job_map: Dict[int, Job] = {}
        self._operation_map: Dict[int, Operation] = {}

    @classmethod
    def from_file(cls, folderpath):
        inst = cls(os.path.basename(folderpath))

        op_file_path = os.path.join(folderpath, f"{inst._instance_name}_op.csv")
        mach_file_path = os.path.join(folderpath, f"{inst._instance_name}_mach.csv")

        temp_ops: Dict[tuple, Operation] = {}  # (job_id, op_id) -> Operation

        # Lecture des opérations
        with open(op_file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                job_id = int(row['job'])
                op_id = int(row['operation'])

                # Création d'une opération si elle n'existe pas déjà
                if (job_id, op_id) not in temp_ops:
                    operation = Operation(job_id, op_id)
                    temp_ops[(job_id, op_id)] = operation

                # Ajout des options de machine à l'opération
                operation = temp_ops[(job_id, op_id)]
                operation.add_machine_option(
                    machine_id=int(row['machine']),
                    duration=int(row['processing_time']),
                    energy=int(row['energy_consumption'])
                )

        # Lecture des machines
        with open(mach_file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                machine = Machine(
                    machine_id=int(row['machine_id']),
                    set_up_time=int(row['set_up_time']),
                    set_up_energy=int(row['set_up_energy']),
                    tear_down_time=int(row['tear_down_time']),
                    tear_down_energy=int(row['tear_down_energy']),
                    min_consumption=int(row['min_consumption']),
                    end_time=int(row['end_time'])
                )
                inst._machines.append(machine)
                inst._machine_map[machine.machine_id] = machine

        # Création des jobs et des opérations
        sorted_op_keys = sorted(temp_ops.keys(), key=lambda k: (k[0], k[1]))

        for job_id, op_id in sorted_op_keys:
            if job_id not in inst._job_map:
                job = Job(job_id)
                inst._jobs.append(job)
                inst._job_map[job_id] = job

            operation = temp_ops[(job_id, op_id)]
            inst._operations.append(operation)
            inst._operation_map[op_id] = operation  # On part de l'hypothèse que operation_id est unique
            inst._job_map[job_id].add_operation(operation)

        inst._jobs.sort(key=lambda j: j.job_id)
        inst._machines.sort(key=lambda m: m.machine_id)
        inst._operations.sort(key=lambda o: o.operation_id)

        return inst

    @property
    def name(self):
        return self._instance_name

    @property
    def machines(self) -> List[Machine]:
        return self._machines

    @property
    def jobs(self) -> List[Job]:
        return self._jobs

    @property
    def operations(self) -> List[Operation]:
        return self._operations

    @property
    def nb_jobs(self):
        return len(self._jobs)

    @property
    def nb_machines(self):
        return len(self._machines)

    @property
    def nb_operations(self):
        return len(self._operations)

    def __str__(self):
        return f"{self.name}_M{self.nb_machines}_J{self.nb_jobs}_O{self.nb_operations}"

    def get_machine(self, machine_id) -> Machine:
        return self._machine_map[machine_id]

    def get_job(self, job_id) -> Job:
        return self._job_map[job_id]

    def get_operation(self, operation_id) -> Operation:
        return self._operation_map[operation_id]

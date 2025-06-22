'''
Object containing the solution to the optimization problem.

@author: Vassilissa Lehoux
'''
import csv
import os
from typing import List, Optional
from matplotlib import pyplot as plt
from src.scheduling.instance.instance import Instance
from src.scheduling.instance.operation import Operation

from matplotlib import colormaps
from src.scheduling.instance.machine import Machine


class Solution(object):
    '''
    Solution class
    '''

    def __init__(self, instance: Instance):
        '''
        Constructor
        '''
        self._instance = instance
        self._objective_value: Optional[int] = None

        self._weights = {'energy': 1, 'cmax': 1, 'sum_ci': 0}


    @property
    def inst(self):
        '''
        Returns the associated instance
        '''
        return self._instance


    def reset(self):
        '''
        Resets the solution: everything needs to be replanned
        '''
        for job in self.inst.jobs:
            job.reset()

        for machine in self.inst.machines:
            machine.reset()

        self._objective_value = None

    @property
    def is_feasible(self) -> bool:
        '''
        Returns True if the solution respects the constraints.
        To call this function, all the operations must be planned.
        '''
        # Il faut s'assurer que toutes les opérations sont planifiées
        if any(not op.assigned for op in self.all_operations):
            return False

        # Il faut s'assurer que toutes les opérations ont un temps de début valide
        for op in self.all_operations:
            if op.start_time < op.min_start_time:
                return False

        # Il faut respecter les contraintes de précédence entre les opérations
        for machine in self.inst.machines:
            ops = sorted(machine.scheduled_operations, key=lambda o: o.start_time)
            for i in range(len(ops) - 1):
                if ops[i].end_time > ops[i + 1].start_time:
                    return False

        return True

    @property
    def evaluate(self) -> int:
        '''
        Computes the value of the solution
        '''

        # Si la solution n'est pas faisable, on retourne un score infini
        if not self.is_feasible:
            self._objective_value = float('inf')
            return self._objective_value

        # On s'assure que toutes les opérations sont planifiées
        for job in self.inst.jobs:
            if not job.planned:
                raise ValueError("All operations must be planned before evaluating the solution.")

        # On s'assure que toutes les machines sont arrêtées
        # pour éviter les erreurs de planification
        # (par exemple, si une machine est en marche mais n'a pas d'opérations planifiées)
        for machine in self.inst.machines:
            if machine.scheduled_operations and not machine.stop_times:
                last_op_time = machine.available_time
                machine.stop(last_op_time)

        # On calcule la valeur de l'objectif (C'est à nous de définir les pondérations?)
        w_energy = self._weights.get('energy', 1)
        w_cmax = self._weights.get('cmax', 1)
        w_sum_ci = self._weights.get('sum_ci', 0)

        value = (w_energy * self.total_energy_consumption +
                 w_cmax * self.cmax +
                 w_sum_ci * self.sum_ci)

        self._objective_value = int(value)
        return self._objective_value

    @property
    def objective(self) -> int:
        '''
        Returns the value of the objective function
        '''
        if self._objective_value is None:
            self.evaluate

        return self._objective_value

    @property
    def cmax(self) -> int:
        '''
        Returns the maximum completion time of a job
        '''
        completion_times = [j.completion_time for j in self.inst.jobs if j.completion_time != -1]
        return max(completion_times) if completion_times else 0

    @property
    def sum_ci(self) -> int:
        '''
        Returns the sum of completion times of all the jobs
        '''
        return sum(j.completion_time for j in self.inst.jobs if j.completion_time != -1)

    @property
    def total_energy_consumption(self) -> int:
        '''
        Returns the total energy consumption for processing
        all the jobs (including energy for machine switched on but doing nothing).
        '''
        return sum(m.total_energy_consumption for m in self.inst.machines)

    def __str__(self) -> str:
        '''
        String representation of the solution
        '''
        return ""

    def to_csv(self):
        '''
        Save the solution to a csv files with the following formats:
        Operation file:
          One line per operation
          operation id - machine to which it is assigned - start time
          header: "operation_id,machine_id,start_time"
        Machine file:
          One line per pair of (start time, stop time) for the machine
          header: "machine_id, start_time, stop_time"
        '''
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        op_filepath = os.path.join(output_dir, f"{self.inst.name}_solution_operations.csv")
        with open(op_filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["operation_id", "machine_id", "start_time"])
            sorted_ops = sorted(self.all_operations, key=lambda o: o.operation_id)
            for op in sorted_ops:
                if op.assigned:
                    writer.writerow([op.operation_id, op.assigned_to, op.start_time])

        mach_filepath = os.path.join(output_dir, f"{self.inst.name}_solution_machines.csv")
        with open(mach_filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["machine_id", "start_time", "stop_time"])
            for m in self.inst.machines:
                starts = m.start_times
                stops = m.stop_times
                for i in range(len(starts)):
                    writer.writerow([m.machine_id, starts[i], stops[i] if i < len(stops) else -1])

    def from_csv(self, inst_folder, operation_file, machine_file):
        '''
        Reads a solution from the instance folder
        '''
        self.reset()
        op_path = os.path.join(inst_folder, operation_file)

        ops_data = []
        with open(op_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ops_data.append({
                    "op_id": int(row['operation_id']),
                    "machine_id": int(row['machine_id']),
                    "start_time": int(row['start_time'])
                })

        ops_data.sort(key=lambda x: x['start_time'])

        for data in ops_data:
            op = self.inst.get_operation(data['op_id'])
            machine = self.inst.get_machine(data['machine_id'])

            self.schedule(op, machine)

    @property
    def available_operations(self)-> List[Operation]:
        '''
        Returns the available operations for scheduling:
        all constraints have been met for those operations to start
        '''
        return [op for op in self.all_operations if not op.assigned and op.is_ready(float('inf'))]

    @property
    def all_operations(self) -> List[Operation]:
        '''
        Returns all the operations in the instance
        '''
        return self.inst.operations


    def schedule(self, operation: Operation, machine: Machine):
        '''
        Schedules the operation at the end of the planning of the machine.
        Starts the machine if stopped.
        @param operation: an operation that is available for scheduling
        '''
        # On cherche à savoir quand l'opération peut commencer
        pred_ready_time = operation.min_start_time

        # On cherche à savoir quand la machine est prête en fonction de si elle a ou non une opération planifiée
        if not machine.scheduled_operations:
            # C'est la première opération sur cette machine.
            # Elle sera prête une fois son setup terminé.
            machine_ready_time = machine.set_up_time
        else:
            # La machine a déjà des opérations, elle est prête après la dernière.
            machine_ready_time = machine.available_time

        # L'opération peut démarrer au plus tard de ces deux moments.
        final_start_time = max(pred_ready_time, machine_ready_time)

        # Si la machine n'est pas démarrée, on la démarre.
        if not machine.scheduled_operations:
            # Pour que l'opération démarre à `final_start_time`, le setup a dû commencer avant.
            setup_start_time = final_start_time - machine.set_up_time
            machine.start(max(0, setup_start_time))

        # On planifie l'opération sur la machine
        operation.schedule(machine.machine_id, final_start_time, check_success=False)
        machine.add_operation(operation, final_start_time)

        # On met à jour les temps de début et de fin de l'opération
        job = self.inst.get_job(operation.job_id)
        if job.next_operation and job.next_operation.operation_id == operation.operation_id:
            job.schedule_operation()

    def gantt(self, colormapname):
        """
        Generate a plot of the planning.
        Standard colormaps can be found at https://matplotlib.org/stable/users/explain/colors/colormaps.html
        """
        fig, ax = plt.subplots()
        colormap = colormaps[colormapname]
        for machine in self.inst.machines:
            machine_operations = sorted(machine.scheduled_operations, key=lambda op: op.start_time)
            for operation in machine_operations:
                operation_start = operation.start_time
                operation_end = operation.end_time
                operation_duration = operation_end - operation_start
                operation_label = f"O{operation.operation_id}_J{operation.job_id}"
    
                # Set color based on job ID
                color_index = operation.job_id + 2
                if color_index >= colormap.N:
                    color_index = color_index % colormap.N
                color = colormap(color_index)
    
                ax.broken_barh(
                    [(operation_start, operation_duration)],
                    (machine.machine_id - 0.4, 0.8),
                    facecolors=color,
                    edgecolor='black'
                )

                middle_of_operation = operation_start + operation_duration / 2
                ax.text(
                    middle_of_operation,
                    machine.machine_id,
                    operation_label,
                    rotation=90,
                    ha='center',
                    va='center',
                    fontsize=8
                )
            set_up_time = machine.set_up_time
            tear_down_time = machine.tear_down_time
            for (start, stop) in zip(machine.start_times, machine.stop_times):
                start_label = "set up"
                stop_label = "tear down"
                ax.broken_barh(
                    [(start, set_up_time)],
                    (machine.machine_id - 0.4, 0.8),
                    facecolors=colormap(0),
                    edgecolor='black'
                )
                ax.broken_barh(
                    [(stop, tear_down_time)],
                    (machine.machine_id - 0.4, 0.8),
                    facecolors=colormap(1),
                    edgecolor='black'
                )
                ax.text(
                    start + set_up_time / 2.0,
                    machine.machine_id,
                    start_label,
                    rotation=90,
                    ha='center',
                    va='center',
                    fontsize=8
                )
                ax.text(
                    stop + tear_down_time / 2.0,
                    machine.machine_id,
                    stop_label,
                    rotation=90,
                    ha='center',
                    va='center',
                    fontsize=8
                )          

        fig = ax.figure
        fig.set_size_inches(12, 6)
    
        ax.set_yticks(range(self._instance.nb_machines))
        ax.set_yticklabels([f'M{machine_id+1}' for machine_id in range(self.inst.nb_machines)])
        ax.set_xlabel('Time')
        ax.set_ylabel('Machine')
        ax.set_title('Gantt Chart')
        ax.grid(True)
    
        return plt

'''
Test of the Solution class.

@author: Vassilissa Lehoux
'''
import unittest
import os

from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution
from src.scheduling.tests.test_utils import TEST_FOLDER_DATA, TEST_FOLDER


class TestSolution(unittest.TestCase):

    def setUp(self):
        """
        Charge une instance de test avant chaque test.
        """
        self.inst1 = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp1")
        self.sol = Solution(self.inst1)

    def tearDown(self):
        """
        Nettoyage après chaque test.
        """
        pass

    def test_init_sol(self):
        sol = Solution(self.inst1)
        self.assertEqual(len(sol.all_operations), len(self.inst1.operations),
                         'Nb of operations should be the same between instance and solution')
        self.assertEqual(len(sol.available_operations), len(self.inst1.jobs),
                         'One operation per job should be available for scheduling')

    def test_schedule_op(self):
        sol = Solution(self.inst1)
        operation = self.inst1.operations[0]
        machine = self.inst1.machines[1]
        sol.schedule(operation, machine)
        self.assertTrue(operation.assigned, 'operation should be assigned')
        self.assertEqual(operation.assigned_to, 1, 'wrong machine machine')
        self.assertEqual(operation.processing_time, 12, 'wrong operation duration')
        self.assertEqual(operation.energy, 12, 'wrong operation energy cost')
        self.assertEqual(operation.start_time, 20, 'wrong set up time for machine')
        self.assertEqual(operation.end_time, 32, 'wrong operation end time')
        self.assertEqual(machine.available_time, 32, 'wrong available time')
        self.assertEqual(machine.working_time, 120, 'wrong working time for machine')
        operation = self.inst1.operations[2]
        sol.schedule(operation, machine)
        self.assertTrue(operation.assigned, 'operation should be assigned')
        self.assertEqual(operation.assigned_to, 1, 'wrong machine machine')
        self.assertEqual(operation.processing_time, 9, 'wrong operation duration')
        self.assertEqual(operation.energy, 10, 'wrong operation energy cost')
        self.assertEqual(operation.start_time, 32, 'wrong start time for operation')
        self.assertEqual(operation.end_time, 41, 'wrong operation end time')
        self.assertEqual(machine.available_time, 41, 'wrong available time')
        self.assertEqual(machine.working_time, 120, 'wrong working time for machine')
        operation = self.inst1.operations[1]
        machine = self.inst1.machines[0]
        sol.schedule(operation, machine)
        self.assertTrue(operation.assigned, 'operation should be assigned')
        self.assertEqual(operation.assigned_to, 0, 'wrong machine machine')
        self.assertEqual(operation.processing_time, 5, 'wrong operation duration')
        self.assertEqual(operation.energy, 6, 'wrong operation energy cost')
        self.assertEqual(operation.start_time, 32, 'wrong start time for operation')
        self.assertEqual(operation.end_time, 37, 'wrong operation end time')
        self.assertEqual(machine.available_time, 37, 'wrong available time')
        self.assertEqual(machine.working_time, 83, 'wrong working time for machine')
        self.assertEqual(machine.start_times[0], 17)
        self.assertEqual(machine.stop_times[0], 100)
        operation = self.inst1.operations[3]
        sol.schedule(operation, machine)
        self.assertTrue(operation.assigned, 'operation should be assigned')
        self.assertEqual(operation.assigned_to, 0, 'wrong machine machine')
        self.assertEqual(operation.processing_time, 10, 'wrong operation duration')
        self.assertEqual(operation.energy, 9, 'wrong operation energy cost')
        self.assertEqual(operation.start_time, 41, 'wrong start time for operation')
        self.assertEqual(operation.end_time, 51, 'wrong operation end time')
        self.assertEqual(machine.available_time, 51, 'wrong available time')
        self.assertEqual(machine.working_time, 83, 'wrong working time for machine')
        self.assertEqual(machine.start_times[0], 17)
        self.assertEqual(machine.stop_times[0], 100)
        self.assertTrue(sol.is_feasible, 'Solution should be feasible')
        plt = sol.gantt('tab20')
        plt.savefig(TEST_FOLDER + os.path.sep +  'temp.png')

    def test_objective(self):
        '''
        Test your objective function
        '''
        # Vérifie que l'objectif n'est pas calculé au départ
        self.assertIsNone(self.sol._objective_value, "L'objectif ne doit pas être pré-calculé.")

        # Créer une solution complète
        while self.sol.available_operations:
            op = sorted(self.sol.available_operations, key=lambda o: o.operation_id)[0]
            machine_id = list(op.get_machine_options().keys())[0]
            machine = self.inst1.get_machine(machine_id)
            self.sol.schedule(op, machine)

        # Calculer la valeur attendue
        expected_value = self.sol.total_energy_consumption + self.sol.cmax

        # Vérifier que la propriété `objective` retourne la bonne valeur
        self.assertEqual(self.sol.objective, expected_value)

        # L'attribut interne doit maintenant contenir la valeur calculée
        self.assertEqual(self.sol._objective_value, expected_value,
                         "La valeur de l'objectif doit être mise en cache.")

        # Si on change une valeur manuellement, l'objectif doit rester le même
        self.sol._objective_value = -999
        self.assertEqual(self.sol.objective, -999)

    def test_evaluate(self):
        '''
        Test your evaluate function
        '''
        # Créer une solution complète de manière déterministe
        while self.sol.available_operations:
            op = sorted(self.sol.available_operations, key=lambda o: o.operation_id)[0]
            machine_id = list(op.get_machine_options().keys())[0]
            machine = self.inst1.get_machine(machine_id)
            self.sol.schedule(op, machine)

        # Vérifie que la solution est complète
        self.assertTrue(all(op.assigned for op in self.sol.all_operations))

        # Calculer les métriques et la valeur attendue
        cmax = self.sol.cmax
        total_energy = self.sol.total_energy_consumption
        # Poids par défaut : {'energy': 1, 'cmax': 1, 'sum_ci': 0}
        expected_value = total_energy + cmax

        self.assertGreater(cmax, 0)
        self.assertGreater(total_energy, 0)

        # Vérifier que `evaluate` retourne la bonne valeur
        self.assertEqual(self.sol.evaluate, expected_value)

    def test_is_feasible_property(self):
        """
        Vérifie la détection de solutions faisables et non faisables.
        """
        # Solution faisable
        while self.sol.available_operations:
            op = sorted(self.sol.available_operations, key=lambda o: o.operation_id)[0]
            machine_id = list(op.get_machine_options().keys())[0]
            machine = self.inst1.get_machine(machine_id)
            self.sol.schedule(op, machine)
        self.assertTrue(self.sol.is_feasible, "Une solution complète et sans conflit doit être faisable.")

        # Solution non faisable (opération manquante)
        self.sol.reset()
        op1 = self.inst1.get_operation(1)
        m1 = self.inst1.get_machine(1)
        self.sol.schedule(op1, m1)
        self.assertFalse(self.sol.is_feasible, "Une solution incomplète ne doit pas être faisable.")

        # Solution non faisable (violation de précédence)
        self.sol.reset()
        op1 = self.inst1.get_operation(1)
        op2 = self.inst1.get_operation(2)  # successeur de op1
        m1 = self.inst1.get_machine(1)
        # Planifie op2 à t=0 (impossible, op1 n'est pas faite)
        op2.schedule(m1.machine_id, 0, check_success=False)
        m1.add_operation(op2, 0)
        self.assertFalse(self.sol.is_feasible, "Une solution violant la précédence doit être non faisable.")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

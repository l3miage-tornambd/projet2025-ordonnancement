'''
Tests for the Machine class

@author: Vassilissa Lehoux
'''
import unittest
from src.scheduling.instance.machine import Machine
from src.scheduling.instance.operation import Operation


class TestMachine(unittest.TestCase):

    def setUp(self):
        """
        Méthode exécutée avant chaque test.
        Initialise une machine et des opérations standards pour les tests.
        """
        self.machine = Machine(
            machine_id=1,
            set_up_time=10,
            set_up_energy=100,
            tear_down_time=5,
            tear_down_energy=50,
            min_consumption=2,
            end_time=1000  # Horizon max de la machine
        )
        self.op1 = Operation(job_id=1, operation_id=1)
        self.op1.add_machine_option(machine_id=1, duration=20, energy=250)
        self.op2 = Operation(job_id=1, operation_id=2)
        self.op2.add_machine_option(machine_id=1, duration=30, energy=350)

    def tearDown(self):
        pass

    def test_initial_state(self):
        # Vérifie l'état initial de la machine que l'on crée dans setUp
        self.assertEqual(self.machine.machine_id, 1)
        self.assertEqual(self.machine.available_time, 0)
        self.assertFalse(self.machine.scheduled_operations)
        self.assertFalse(self.machine.start_times)
        self.assertFalse(self.machine.stop_times)

    def test_reset_clears_state(self):
        self.machine.start(0)
        self.op1.schedule(1, 10)
        self.machine.add_operation(self.op1, 10)
        self.assertTrue(self.machine.start_times)
        self.assertTrue(self.machine.stop_times)
        self.assertTrue(self.machine.scheduled_operations)

        self.machine.reset()

        self.test_initial_state()

    def testWorkingTime(self):
        # Au début, le temps de fonctionnement doit être 0
        self.assertEqual(self.machine.working_time, 0, "Le temps de fonctionnement initial doit être 0.")

        # On démarre la machine à t=50.
        self.machine.start(50)

        # Le working_time est la durée jusqu'à l'horizon car on ne l'a pas explicitement arrêtée
        self.assertEqual(self.machine.working_time, 950, "working_time doit être end_time(1000) - start_time(50).")

        # On ajoute une opération. Cela ne doit PAS changer le working_time
        self.op1.schedule(1, 60)  # setup de 10, op de 20
        self.machine.add_operation(self.op1, 60)
        self.assertEqual(self.machine.working_time, 950, "L'ajout d'une opération ne change pas le running time.")

        # On arrête explicitement la machine à t=200.
        self.machine.stop(200)
        # Le stop par défaut (1000) est remplacé par 200.
        # Le working_time est maintenant recalculé.
        self.assertEqual(self.machine.working_time, 150, "working_time doit être stop(200) - start(50).")

    def testTotalEnergyConsumption(self):
        # Au début, la consommation d'énergie totale doit être 0
        self.assertEqual(self.machine.total_energy_consumption, 0)

        # On démarre la machine à t=0
        self.machine.start(at_time=0)

        # On ajoute une opération qui consomme de l'énergie
        self.op1.schedule(machine_id=1, at_time=10)
        self.machine.add_operation(self.op1, 10)

        # La machine est occupée jusqu'à t=40 (10 + 20 de l'opération + 10 de setup)
        self.machine.stop(at_time=40)

        # Consommation d'énergie:
        # - Setup: 100 (set_up_energy)
        # - Opération: 250 (energy de op1)
        # - Teardown: 50 (tear_down_energy)
        # - Temps à vide: 2 * 30 (min_consumption * temps à vide de 30)
        self.assertEqual(self.machine.total_energy_consumption, 410)

    def test_add_operation_updates_state(self):
        self.op1.schedule(machine_id=1, at_time=50)
        self.machine.add_operation(self.op1, 50)

        self.assertIn(self.op1, self.machine.scheduled_operations)
        self.assertEqual(self.machine.available_time, 70)


    def test_stop_machine_while_busy_raises_error(self):
        self.machine.start(0)
        self.op1.schedule(machine_id=1, at_time=10)  # Opération finit à t=30
        self.machine.add_operation(self.op1, 10)

        # Essayer d'arrêter à t=25 doit toujours échouer
        with self.assertRaises(ValueError):
            self.machine.stop(at_time=25)

        # Arrêter à t=30 doit toujours fonctionner
        try:
            self.machine.stop(at_time=30)
        except ValueError:
            self.fail("stop() ne devrait pas lever d'exception si appelée au temps de disponibilité.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
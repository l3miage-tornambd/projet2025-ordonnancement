'''
Tests for the Job class

@author: Vassilissa Lehoux
'''
import unittest
from src.scheduling.instance.job import Job
from src.scheduling.instance.operation import Operation

class TestJob(unittest.TestCase):

    def setUp(self):
        """
        Méthode exécutée avant chaque test pour initialiser l'environnement.
        Crée un Job et deux Opérations pour être utilisés dans les tests.
        """
        self.job = Job(job_id=7)

        # Crée deux opérations appartenant à ce job
        self.op1 = Operation(job_id=7, operation_id=1)
        # Ajoute une option de machine pour pouvoir calculer une durée
        self.op1.add_machine_option(machine_id=1, duration=10, energy=100)

        self.op2 = Operation(job_id=7, operation_id=2)
        self.op2.add_machine_option(machine_id=1, duration=15, energy=150)

    def tearDown(self):
        """
        Méthode exécutée après chaque test.
        """
        pass

    def testCompletionTime(self):
        """
        Teste le calcul de la date de fin (completion time) du job.
        Le temps de complétion n'est valide que si toutes les opérations sont planifiées.
        """
        # Ajoute les opérations au job
        self.job.add_operation(self.op1)
        self.job.add_operation(self.op2)

        # Avant toute planification, le temps de complétion doit être -1
        self.assertEqual(self.job.completion_time, -1,
                         "Le temps de complétion doit être -1 si aucune opération n'est planifiée.")

        # Planifie la première opération
        self.op1.schedule(machine_id=1, at_time=0)  # op1 se termine à t=10

        # Le job n'est pas encore entièrement planifié, completion_time reste -1
        self.assertEqual(self.job.completion_time, -1,
                         "Le temps de complétion doit rester -1 si le job n'est pas fini.")

        # Planifie la seconde (et dernière) opération
        self.op2.schedule(machine_id=1, at_time=self.op1.end_time)  # op2 commence à t=10 et finit à t=25

        # Toutes les opérations sont planifiées, le temps de complétion est celui de la dernière opération
        self.assertEqual(self.job.completion_time, 25,
                         "Le temps de complétion doit être l'heure de fin de la dernière opération.")

    def test_initial_state(self):
        """
        Vérifie l'état d'un job juste après sa création.
        """
        self.assertEqual(self.job.job_id, 7)
        self.assertEqual(self.job.operation_nb, 0)
        self.assertTrue(self.job.planned, "Un nouveau job est considéré comme planifié.")
        self.assertIsNone(self.job.next_operation, "Un nouveau job ne doit pas avoir d'opération suivante.")

    def test_add_operation_and_precedence(self):
        """
        Vérifie que l'ajout d'opérations les lie correctement
        avec les contraintes de précédence.
        """
        # Ajout de la première opération
        self.job.add_operation(self.op1)
        self.assertEqual(self.job.operation_nb, 1)
        self.assertIn(self.op1, self.job.operations)
        # A ce stade, il n'y a pas de liens de précédence
        self.assertFalse(self.op1.predecessors)
        self.assertFalse(self.op1.successors)

        # Ajout de la seconde opération
        self.job.add_operation(self.op2)
        self.assertEqual(self.job.operation_nb, 2)

        # Vérification des liens de précédence
        self.assertIn(self.op2, self.op1.successors, "op2 doit être le successeur de op1.")
        self.assertIn(self.op1, self.op2.predecessors, "op1 doit être le prédécesseur de op2.")

    def test_scheduling_flow_and_state(self):
        """
        Vérifie le changement d'état du job (next_operation, planned)
        au fur et à mesure de la planification.
        """
        self.job.add_operation(self.op1)
        self.job.add_operation(self.op2)

        # État initial
        self.assertFalse(self.job.planned)
        self.assertEqual(self.job.next_operation, self.op1)

        # On signale que la première opération est planifiée
        self.job.schedule_operation()
        self.assertFalse(self.job.planned)
        self.assertEqual(self.job.next_operation, self.op2)

        # On signale que la seconde opération est planifiée
        self.job.schedule_operation()
        self.assertTrue(self.job.planned, "Le job doit être marqué comme planifié lorsque toutes les opérations le sont.")
        self.assertIsNone(self.job.next_operation,"Il ne doit plus y avoir d'opération suivante lorsque le job est fini.")

    def test_reset(self):
        """
        Vérifie que la méthode `reset` réinitialise correctement
        l'état du job et de ses opérations.
        """
        self.job.add_operation(self.op1)
        self.job.add_operation(self.op2)

        # Planifie le job
        self.op1.schedule(1, 0)
        self.job.schedule_operation()
        self.op2.schedule(1, 10)
        self.job.schedule_operation()

        # Vérifie que l'état a bien changé
        self.assertTrue(self.job.planned)
        self.assertTrue(self.op1.assigned)

        # Appelle reset
        self.job.reset()

        # Vérifie que l'état du job est réinitialisé
        self.assertFalse(self.job.planned)
        self.assertEqual(self.job.next_operation, self.op1)

        # Vérifie que l'état des opérations a aussi été réinitialisé
        self.assertFalse(self.op1.assigned, "L'opération doit aussi être réinitialisée.")
        self.assertEqual(self.op1.start_time, -1)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

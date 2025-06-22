import os
import time
import csv
from pathlib import Path

# On importe les classes dont on a besoin
from src.scheduling.instance.instance import Instance
from src.scheduling.optim.constructive import Greedy, NonDeterminist
from src.scheduling.optim.local_search import FirstNeighborLocalSearch
from src.scheduling.optim.neighborhoods import MyNeighborhood1, MyNeighborhood2

# --- Paramètres ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_ROOT_DIR = PROJECT_ROOT / 'data'
RESULTS_FILE = PROJECT_ROOT / 'results.csv'
NON_DETERMINISTIC_RUNS = 10


def main():
    print(f"Démarrage de la campagne de comparaison...")
    print(f"Dossier de données : {DATA_ROOT_DIR}")
    print(f"Fichier de résultats : {RESULTS_FILE}")

    with open(RESULTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['instance', 'algorithme', 'valeur_objectif', 'temps_execution_s'])

    if not DATA_ROOT_DIR.exists():
        print(f"[ERREUR] Le dossier de données '{DATA_ROOT_DIR}' est introuvable.")
        return

    instance_dirs = sorted([d for d in DATA_ROOT_DIR.iterdir() if d.is_dir() and d.name.startswith('jsp')])

    greedy_solver = Greedy()
    local_search_solver = FirstNeighborLocalSearch()

    for instance_dir in instance_dirs:
        instance_name = instance_dir.name
        print(f"--- Traitement de l'instance : {instance_name} ---")

        try:
            inst = Instance.from_file(instance_dir)
        except FileNotFoundError:
            print(f"  [Erreur] Fichiers non trouvés ou invalides dans {instance_dir}. Passage à la suivante.")
            continue

        # Partie algorithme glouton (inchangée)
        print(f"  [1/3] Exécution de l'algorithme glouton...")
        start_time = time.perf_counter()
        greedy_solution = greedy_solver.run(inst)
        end_time = time.perf_counter()

        greedy_objectif_value = greedy_solution.cmax
        greedy_time = end_time - start_time
        save_result(instance_name, 'glouton', greedy_objectif_value, greedy_time)
        print(f"    > Fait en {greedy_time:.4f}s, objectif valeur = {greedy_objectif_value}")

        # Partie recherche locale via échange d'opération ---
        print(f"  [2/3] Exécution de la recherche locale 1 ({NON_DETERMINISTIC_RUNS} runs)...")
        best_objectif_value_nd1 = float('inf')
        total_time_start_nd1 = time.perf_counter()

        for _ in range(NON_DETERMINISTIC_RUNS):
            solution_nd1 = local_search_solver.run(inst, NonDeterminist, MyNeighborhood1)
            current_objectif_value_nd1 = solution_nd1.cmax
            if current_objectif_value_nd1 < best_objectif_value_nd1:
                best_objectif_value_nd1 = current_objectif_value_nd1

        total_time_end_nd1 = time.perf_counter()
        total_time_nd1 = total_time_end_nd1 - total_time_start_nd1
        save_result(instance_name, 'local_search_voisinage1', best_objectif_value_nd1, total_time_nd1)
        print(f"    > Fait en {total_time_nd1:.4f}s, meilleur objectif valeur nd1 = {best_objectif_value_nd1}")

        # Partie recherche locale via changement de machine ---
        print(f"  [3/3] Exécution de la recherche locale 2 ({NON_DETERMINISTIC_RUNS} runs)...")
        best_objectif_value_nd2 = float('inf')
        total_time_start_nd2 = time.perf_counter()

        for _ in range(NON_DETERMINISTIC_RUNS):
            solution_nd2 = local_search_solver.run(inst, NonDeterminist, MyNeighborhood2)
            current_objectif_value_nd2 = solution_nd2.cmax
            if current_objectif_value_nd2 < best_objectif_value_nd2:
                best_objectif_value_nd2 = current_objectif_value_nd2

        total_time_end_nd2 = time.perf_counter()
        total_time_nd2 = total_time_end_nd2 - total_time_start_nd2
        save_result(instance_name, 'local_search_voisinage2', best_objectif_value_nd2, total_time_nd2)
        print(f"    > Fait en {total_time_nd2:.4f}s, meilleur objectif valeur nd2 = {best_objectif_value_nd2}")


def save_result(instance, algo, makespan, exec_time):
    with open(RESULTS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([instance, algo, makespan, exec_time])


if __name__ == '__main__':
    main()
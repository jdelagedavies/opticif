"""This script demonstrates how to use the ragraph and opticif packages to analyze and sequence plant models

1. Loads nodes and edges from CSV files.
2. Computes and prints initial metrics (feedback distance, feedback marks, and cycles).
3. Creates a design structure matrix (DSM) and saves it as an SVG image.
4. Performs a genetic algorithm-based sequencing to optimize the system.
5. Computes and prints metrics for the sequenced system.
6. Creates a sequenced DSM and saves it as an SVG image.
7. Writes the new sequence to a CSV file usable by opticif.

To customize the script for your own system, modify the file paths, directories, and adjust
the parameters as needed.
"""
import time
from pathlib import Path

from ragraph import plot
from ragraph.analysis.heuristics import johnson
from ragraph.analysis.sequence._genetic import genetic
from ragraph.analysis.sequence.metrics import feedback_distance, feedback_marks
from ragraph.io.csv import from_csv

from opticif import node_to_csv

# Define input files and directories
input_dir = "./models/simple_lock"
test_nodes = f"{input_dir}/simple_lock.nodes.csv"  # Requires at least a name column
test_edges = (
    f"{input_dir}/simple_lock.edges.csv"  # Requires at least a source and target column
)

# Define output files and directories
output_dir = "./models/simple_lock/generated"
output_csv_stem_path = "genetic"  # Stem path of the CSV list of sequenced node names

# Define parameters
n_chromosomes = 1000
n_generations = 10000
evaluator = "feedback_distance"
csv_delimiter = ";"

# Create graph object from nodes and edges
print("Initializing: Loading nodes and edges from CSV files...")
g = from_csv(test_nodes, test_edges)

# Compute penalty scores and contribution of each cell in the matrix to the penalty scores
score_dist, contrib_dist = feedback_distance(g.get_adjacency_matrix())
score_marks, contrib_marks = feedback_marks(g.get_adjacency_matrix())

# Detect cycles
cycles = list(johnson(g, names=True))
n_cycles = len(cycles)
print(
    f"Initialization complete.\n"
    f"Initial feedback distance: {score_dist}\n"
    f"Initial feedback marks: {score_marks}\n"
    f"Initial contribution to feedback distance:\n{contrib_dist}\n"
    f"Initial contribution to feedback marks:\n{contrib_marks}\n"
    f"Initial number of cycles: {n_cycles}\n"
    f"Initial cycles: {cycles}\n"
)

# Create the 'generated' directory if it doesn't exist
generated_dir = Path(output_dir)
generated_dir.mkdir(exist_ok=True)

# Plot DSM
fig = plot.dsm(
    leafs=g.leafs,
    edges=g.edges,
)
fig.write_image(f"{generated_dir}/dsm.svg")

# Sequence using genetic algorithm
print("Sequencing: Running genetic sequencing algorithm...")
start_time = time.time()
g, seq = genetic(g, n_chromosomes=1000, n_generations=10000, evaluator=evaluator)
end_time = time.time()

time_elapsed = end_time - start_time

# Compute penalty scores and contribution of each cell in the matrix to the penalty scores
score_dist_seq, contrib_dist_seq = feedback_distance(g.get_adjacency_matrix(nodes=seq))
score_marks_seq, contrib_marks_seq = feedback_marks(g.get_adjacency_matrix(nodes=seq))

# Detect cycles
cycles_seq = list(johnson(g, names=True, nodes=seq))
n_cycles_seq = len(cycles_seq)
print(
    f"Sequencing complete. Execution time: {time_elapsed:.2f} seconds.\n"
    f"Sequenced feedback distance: {score_dist_seq:.2f}\n"
    f"Sequenced feedback marks: {score_marks_seq}\n"
    f"Sequenced contribution to feedback distance:\n{contrib_dist_seq}\n"
    f"Sequenced contribution to feedback marks:\n{contrib_marks_seq}\n"
    f"Sequenced number of cycles: {n_cycles_seq}\n"
    f"Sequenced cycles: {cycles_seq}\n"
)

# Plot sequenced DSM
fig = plot.dsm(
    leafs=seq,
    edges=g.edges,
)
fig.write_image(f"{generated_dir}/dsm_sequenced.svg")

# Write new sequence to CSV
node_to_csv(seq, output_csv_stem_path, output_dir, csv_delimiter)
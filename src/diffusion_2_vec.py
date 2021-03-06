from subgraphcomponents import SubGraphComponents
from helper import parameter_parser, result_processing
from joblib import Parallel, delayed
from gensim.models import Word2Vec
from gensim.models.word2vec import logger, FAST_VERSION
from tqdm import tqdm
import logging
import numpy.distutils.system_info as sysinfo
import scipy; scipy.show_config()
import time

logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
sysinfo.get_info("atlas")

def create_features(seeding, edge_list_path, vertex_set_cardinality):
    """
    Creating a single feature for every node.
    :param seeding: Random seed.
    :param edge_list_path:  Path to edge list csv.
    :param vertex_set_cardinality: Number of diffusions per node.
    :return: Sequences and measurements.
    """
    sub_graphs = SubGraphComponents(edge_list_path, seeding, vertex_set_cardinality)
    return sub_graphs.paths, sub_graphs.read_time, sub_graphs.generation_time

def run_parallel_feature_creation(edge_list_path,  vertex_set_cardinality, number_of_replicates, num_of_workers):
    """
    Creating linear node sequences for every node multiple times in a parallel fashion
    :param edge_list_path: Path to edge list csv.
    :param vertex_set_cardinality: Number of diffusions per node.
    :param number_of_replicates: Number of unique nodes per diffusion.
    :param num_of_workers: Number of cores used.
    :return walk_results: List of 3-length tuples with sequences and performance measurements.
    """
    results = Parallel(n_jobs = num_of_workers)(delayed(create_features)(i, edge_list_path, vertex_set_cardinality) for i in tqdm(range(number_of_replicates)))
    walk_results = result_processing(results)
    return walk_results
    
def learn_embeddings(walks, args):
    """
    Method to learn an embedding given the sequences and arguments.
    :param walks: Linear vertex sequences.
    :param args: Arguments.
    """
    model = Word2Vec(walks, size = args.dimensions, window = args.window_size, min_count = 1, sg = 1, workers = args.workers, iter = args.iter, alpha = args.alpha)
    model.wv.save_word2vec_format(args.output)

def main(args):
    """
    Main method for creating sequences and learning the embedding.
    :param args: Arguments object.
    """
    print("\n---------------------------\nFeature extraction starts.\n---------------------------\n\n")
    walks = run_parallel_feature_creation(args.input,  args.vertex_set_cardinality, args.num_diffusions, args.workers)
    print("\n-----------------\nLearning starts.\n-----------------\n")
    learn_embeddings(walks, args)

if __name__ == "__main__":
    args = parameter_parser()
    main(args)

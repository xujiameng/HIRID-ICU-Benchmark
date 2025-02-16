import os
import random
import shutil
import torch
import gin
import numpy as np

from icu_benchmarks.data.loader import *
from icu_benchmarks.models.utils import save_config_file


def train_with_gin(model_dir=None,
                   overwrite=False,
                   gin_config_files=None,
                   gin_bindings=None,
                   seed=1234,
                   reproducible=True):
    """Trains a model based on the provided gin configuration.
    This function will set the provided gin bindings, call the train() function
    and clear the gin config. Please see train() for required gin bindings.
    Args:
        model_dir: String with path to directory where model output should be saved.
        overwrite: Boolean indicating whether to overwrite output directory.
        gin_config_files: List of gin config files to load.
        gin_bindings: List of gin bindings to use.
        seed: Integer corresponding to the common seed used for any random operation.
    """

    # Setting the seed before gin parsing
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if reproducible:
        os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
        torch.use_deterministic_algorithms(True)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    if gin_config_files is None:
        gin_config_files = []
    if gin_bindings is None:
        gin_bindings = []
    gin.parse_config_files_and_bindings(gin_config_files, gin_bindings)
    train_common(model_dir, overwrite)
    gin.clear_config()



@gin.configurable('train_common')
def train_common(log_dir, overwrite=False, model=gin.REQUIRED, dataset_fn=gin.REQUIRED,
                 data_path=gin.REQUIRED, weight=None, do_test=False):
    """

    :param log_dir:
    :param overwrite:
    :param model:
    :param dataset_fn:
    :param data_path:
    :param epochs:
    :param batch_size:
    :param weight:
    :param do_test:
    :return:
    """

    if os.path.isdir(log_dir):
        if overwrite:
            shutil.rmtree(log_dir)
        else:
            raise ValueError("Directory already exists and overwrite is False.")

    os.makedirs(log_dir)

    dataset = dataset_fn(data_path, split='train')
    val_dataset = dataset_fn(data_path, split='val')

    # We set the label scaler
    val_dataset.set_scaler(dataset.scaler)
    model.set_scaler(dataset.scaler)

    model.set_logdir(log_dir)
    save_config_file(log_dir)  # We save the operative config before and also after training

    model.train(dataset, val_dataset, weight)
    del dataset.h5_loader.lookup_table
    del val_dataset.h5_loader.lookup_table

    if do_test:
        test_dataset = dataset_fn(data_path, split='test')
        test_dataset.set_scaler(dataset.scaler)
        weight = dataset.get_balance()
        model.test(test_dataset, weight)

    save_config_file(log_dir)
    del test_dataset.h5_loader.lookup_table

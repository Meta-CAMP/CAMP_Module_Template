'''Utilities.'''


# --- Workflow setup --- #


import gzip
import os
from os import makedirs, symlink
from os.path import abspath, basename, exists, join
import pandas as pd
import shutil
import yaml

def get_conda_prefix(yaml_file):
    """Load conda_prefix from parameters.yaml."""
    with open(yaml_file, "r") as file:
        config = yaml.safe_load(file)
    return config.get("conda_prefix", "Not Found")  # Default value if key is missing


def extract_from_gzip(ap, out):
    if open(ap, 'rb').read(2) == b'\x1f\x8b': # If the input is gzipped
        with gzip.open(ap, 'rb') as f_in, open(out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    else: # Otherwise, symlink
        symlink(ap, out)


def ingest_samples(samples, tmp):
    df = pd.read_csv(samples, header = 0, index_col = 0) # name, ctgs, fwd, rev
    s = list(df.index)
    lst = df.values.tolist()
    for i,l in enumerate(lst):
        # Symlink your original data to the temporary directory
        # if not exists(join(tmp, s[i] + '.fasta')):
            # Example: symlink(abspath(l[0]), join(tmp, s[i] + '.fasta'))
            # Example: extract_from_gzip(abspath(l[1]), join(tmp, s[i] + '_1.fastq'))
            # Example: extract_from_gzip(abspath(l[2]), join(tmp, s[i] + '_2.fastq'))
    return s


def check_make(d):
    if not exists(d):
        makedirs(d)


class Workflow_Dirs:
    '''Management of the working directory tree.'''
    OUT = ''
    TMP = ''
    LOG = ''

    def __init__(self, work_dir, module):
        self.OUT = join(work_dir, '{{ cookiecutter.module_slug }}')
        self.TMP = join(work_dir, 'tmp') 
        self.LOG = join(work_dir, 'logs') 
        # Add custom subdirectories to organize intermediate files
        check_make(self.OUT)
        out_dirs = ['final_reports']
        for d in out_dirs: 
            check_make(join(self.OUT, d))
        # Add a subdirectory for symlinked-in input files
        check_make(self.TMP)
        # Add custom subdirectories to organize rule logs
        check_make(self.LOG)
        log_dirs = []
        for d in log_dirs: 
            check_make(join(self.LOG, d))


def cleanup_files(work_dir, df):
    pass
    smps = list(df.index)
    for d in []: # Add directories to clean up
        for s in smps:
            os.remove(join(work_dir, '{{ cookiecutter.module_slug }}', d, file_to_remove))
            os.remove(join(work_dir, '{{ cookiecutter.module_slug }}', d, file_to_remove))


def print_cmds(f):
    # fo = basename(log).split('.')[0] + '.cmds'
    # lines = open(log, 'r').read().split('\n')
    fi = [l for l in f.split('\n') if l != '']
    write = False
    with open('commands.sh', 'w') as f_out:
        for l in fi:
            if 'rule' in l:
                f_out.write('# ' + l.strip().replace('rule ', '').replace(':', '') + '\n')
            if 'wildcards' in l: 
                f_out.write('# ' + l.strip().replace('wildcards: ', '') + '\n')
            if 'resources' in l:
                write = True 
                l = ''
            if '[' in l: 
                write = False 
            if write:
                f_out.write(l.strip() + '\n')
            if 'rule make_config' in l:
                break


# --- Workflow functions --- #



'''
Doc string
'''

# Standard library imports
import os.path
from pathlib import Path
from os.path import abspath, dirname, join, exists
import sys
import subprocess
import tempfile
from subprocess import Popen
import time

# External library imports
import numpy as np
import pandas as pd
import yaml

def user_dtypes_from_file(dtypes):
    '''
    Return a dict with user dtypes
    Add commments to the file explaining
    that only three dtype options can be used:
    Categorical, Continuous and Timeseries
    ''' 
    with tempfile.TemporaryDirectory() as td:
        f_name = join(td, 'summarize.yml')
        with open(f_name, 'w') as f:
            
            f.write(yaml.safe_dump(dtypes))

        if sys.platform == "win32":
            proc = subprocess.Popen(["notepad.exe", f_name])
        else:
            proc = subprocess.Popen(["gedit", "-s", f_name])

        modified = time.ctime(os.path.getmtime(f_name))
        created = time.ctime(os.path.getctime(f_name))

        while modified == created:
            time.sleep(0.5)    
            modified = time.ctime(os.path.getmtime(f_name))
            
        proc.kill()

        with open(f_name, 'r') as f:

            output = yaml.safe_load(f)
            return output


def open_report_in_default_browser(file_path):
    '''
    Doc string
    '''
    if sys.platform == "win32":
        os.startfile(file_path) # pylint: disable=no-member
    else:
        subprocess.call(["xdg-open", file_path])


def path_checker(string):
    '''
    Improves error message for user if wrong path entered.
    Returns Path object.
    '''
    if not exists(string):
        msg = "Can't find specified file"
        raise FileNotFoundError(msg)
    return Path(string)


def package_dir(*args):
    '''
    Returns absolute path to package / package modules / files
    given names relative to the package root directory

    __file__ attribute  is the pathname of the file from
    which the module was loaded; each module using this
    function will take its own file path from the global
    namespace. Dot dot just moves it up one level which
    imposes certain constrains of the file structure of
    the project.
    '''
    return abspath(join(dirname(__file__), "..", *args))


def transform_frequencies(df1, df2, col_name):
    '''
    Adds zero frequency to a column that is present in one DF, but missing from another.
    '''

    freq_1 = df1[col_name].value_counts()
    freq_2 = df2[col_name].value_counts()

    all_cols = set([col for col in list(df1[col_name].unique()) + list(df2[col_name].unique())])

    new_freq_1 = []
    new_freq_2 = []

    for col in all_cols:
        if col in freq_1:
            new_freq_1.append([col, freq_1[col]])
        else:
            new_freq_1.append([col, 0])
        
        if col in freq_2:
            new_freq_2.append([col, freq_2[col]])
        else:
            new_freq_2.append([col, 0])

    bar_1 = np.array(new_freq_1, dtype=object).T
    bar_2 = np.array(new_freq_2, dtype=object).T

    return(bar_1, bar_2)

def read_data(data_path_1, data_path_2):
    '''
    Currently, only .csv and Excel files are supported.
    Possible to bring more, as long as they integrate into Pandas
    Filename is written into _metadata attribute of each dataframe.
    Watch out for version updates as work is underway to change
    how metadata is stored and propagated in dataframes
    '''

    #Read the first dataset
    if os.path.splitext(data_path_1)[1] == ".csv":

        df1 = pd.read_csv(data_path_1)
        df1._metadata = {"file_name":os.path.basename(data_path_1)}

    elif os.path.splitext(data_path_1)[1] in [".xlsx", ".xls"]:

        df1 = pd.read_excel(data_path_1)
        df1._metadata = {"file_name":os.path.basename(data_path_1)}

    #Read the second dataset
    if os.path.splitext(data_path_2)[1] == ".csv":

        df2 = pd.read_csv(data_path_2)
        df2._metadata = {"file_name":os.path.basename(data_path_2)}

    elif os.path.splitext(data_path_2)[1] in [".xlsx", ".xls"]:

        df2 = pd.read_excel(data_path_2)
        df2._metadata = {"file_name":os.path.basename(data_path_2)}

    return df1, df2

def map_dtype(input_key, reverse=False):
    '''
    Performs conversion between Pandas inferred data types and user-generated ones
    Returns mapped value given an input key; parse_dates is a magic value

    '''
    
    dtype_map = {"object":"Categorical", "int":"Continuous", "float":"Continuous", "datetime":"Timeseries"}
    dtype_map_reverse = {"Categorical":"object", "Continuous":"float64", "Timeseries":"parse_dates"}
    
    if reverse:
        return dtype_map_reverse[input_key]
            
    for mapping_key in dtype_map.keys():
        if mapping_key in str(input_key):
            return dtype_map[mapping_key]
        
    return 'unknown'
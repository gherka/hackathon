
# Standard library imports
import argparse
import textwrap
import sys
import subprocess
import os

# External library imports
import pandas as pd

from ..core.jinja_app import generate_report
from ..core.summary_stats import generate_common_columns, generate_summary
from ..core.helper_funcs import (
    read_data, map_dtype, path_checker, open_report_in_default_browser,
    launch_temp_file, convert_dtypes)
from ..core.mp_distributions import launch_controller

def main():
    '''
    Doc string
    '''

    #Set default verbosity
    sys.tracebacklimit = 0

    desc = textwrap.dedent('''\
        ------------------------------------------------------
        Summarize2: Comparing two datasets with a visual twist  \n
        Create an HTML report with metrics to show how similar
        or different two datasets are between each other.
        ------------------------------------------------------
        ''')

    parser = argparse.ArgumentParser(
            description=desc,
            formatter_class=argparse.RawTextHelpFormatter
            )

    parser.add_argument(
            'first_dataset',
            type=path_checker
            )

    parser.add_argument(
            'second_dataset',
            type=path_checker
            )

    parser.add_argument(
            '--ridge', '-r',
            default=False,
            action='store_true',
            help='not implemented yet',
            )

    parser.add_argument(
            '--xtab', '-xtab',
            action='store_true',
            help='add a crosstab section to the report',
            )

    parser.add_argument(
            '--verbose', '-v',
            default=False,
            action='store_true',
            help='control traceback length for debugging errors',
            )
    
    parser.add_argument(
            '--output', '-o',
            help='not implemented yet',
            )
 
    args = parser.parse_args(sys.argv[1:])

    #Default verbosity is set to 0
    if args.verbose:
        sys.tracebacklimit = 1000

    #Read in files as dataframes
    df1, df2 = read_data(args.first_dataset, args.second_dataset)
    common_columns = generate_common_columns(df1, df2)

    #Change to user-defined (via editable temp text file)
    dtypes = df1[common_columns].dtypes.apply(convert_dtypes).to_dict()
    user_dtypes = launch_temp_file(type="dtypes", dtypes=dtypes)

    ridge_spec = None
    xtab_spec = None

    if args.xtab:

        xtab_spec = launch_temp_file(type="xtab", common_cols=common_columns)

    #Generate report
    generate_report(df1, df2, user_dtypes, xtab=xtab_spec, ridge=ridge_spec)

    #launch the report HTML in the default browser
    file_path = os.path.join(os.getcwd(), "report.html")
    open_report_in_default_browser(file_path)

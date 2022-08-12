import argparse
import json
import re
from os import PathLike
from pathlib import Path
from typing import Union, List

import numpy
import scipy.io
from multiconds import main

if __name__ == "__main__":
    description = 'Create multi-condition files for SST task in DEV study'
    print(description)

    parser = argparse.ArgumentParser(description=description,
                                     add_help=True,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--input', metavar='Input directory', action='store',
                        type=str, required=True,
                        help='absolute path to directory containing behavioral output from the SST task.',
                        dest='input_dir'
                        )

    parser.add_argument('-o', '--output', metavar='directory for output', action='store',
                        type=str, required=False, default=None,
                        help='absolute or relative path for output',
                        dest='output_dir'
                        )

    args = parser.parse_args()

    print(args.input_dir)

    #we don't do BIDs here because BIDs, by convention, uses RT for duration.
    main(args.input_dir, bids_dir=None, use_rt_for_go_success_trials=False, output_folder= args.output_dir)

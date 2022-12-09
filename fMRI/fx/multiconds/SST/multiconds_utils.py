import argparse
from collections import OrderedDict
import json
import re
import warnings
from os import PathLike
from pathlib import Path
from typing import Union, List

import numpy as np
import pandas as pd
import scipy.io

def create_parametric_modulator_struct(modulator_var, masks, conditions,modulator_suffix='MOD',
modulators_to_include=None):
    condition_names = conditions['names']
    duration_array = None
    pmod_list = []
    #this code will assume that there are the same number of conditions as masks.
    #if there aren't, there's probably an error!
    assert len(condition_names)==len(masks)

    for condition_i, condition_name in enumerate(condition_names):
        condition_mask = masks[condition_i]
        # look up to see if we should include this regressor at all; it should
        if sum(condition_mask) > 0:

            #now perhaps the condition exists but we don't want to include it as a parametric modulator. In that case we have to add an empty array to the pmod_list
            if modulators_to_include is not None:
                if condition_name not in modulators_to_include:
                    raise Exception("this might work in theory but hasn't been tested. be aware of that.")
                    pmod_list = pmod_list + [(
                        np.empty((1, 0), dtype=np.float64), 
                        np.empty((1, 0), dtype=np.float64), 
                        np.empty((1, 0), dtype=np.float64)
                        )]
                    continue
            # print(str(condition_i) + ": " + posterror_names[condition_i])
            # print(len(condition_mask))
            # condition_column = condition_mask*reaction_time
            # I'm unsure we should be mean-centering by condition here rather than across all reaction times, but it seems probably the right thing to do?
            condition_column = modulator_var[condition_mask] - np.nanmean(modulator_var[condition_mask],)
            # print(condition_column)
            if condition_column is None:
                continue
            else:
                # print("duration_rray:")
                # print(duration_array.shape)
                # print(condition_column.shape)
                # TO DO; SEE: https://stackoverflow.com/questions/19797822/creating-matlab-cell-arrays-in-python
                # THINK THAT IS THE SOLUTION.
                condition_column_npt = np.empty(1, dtype='O')
                condition_column_npt[0] = condition_column
            
            # poly_val = np.empty(1, dtype='O')
            # poly_val[0] = [1.0]


            caps = re.findall("[A-Z]", condition_names[condition_i])
            abbreviation = "".join(caps).lower()
            abbreviation = abbreviation[0].upper() + abbreviation[1:]
            pmod_item = (
                abbreviation + modulator_suffix,
                condition_column_npt,
                [1.0]
            )


            pmod_list = pmod_list + [pmod_item]
        else:
            # raise Exception("need to verify the next level is prepped to deal with some subjects having a missing regressor.")
            warnings.warn(
                "need to verify the next level is prepped to deal with some subjects having a missing regressor for condition " + condition_name + ".")

    if len(pmod_list) == 0:
        return ({})  # return nothing because there doesn't appear to be any params to pass


    # pmod_array = np.array(
    #     pmod_list,
    #     dtype=([('name', 'object', (1,)), ('param', 'O', (1,)), ('poly', 'object', (1,))])
    # )
    
    pmod_array = np.array(
        pmod_list,
        dtype=([('name', 'O'), ('param', 'O'), ('poly', 'O')])
    )


    return ({
        'pmod': pmod_array,
        'orth': np.array([0] * len(pmod_list), dtype='O')
    })

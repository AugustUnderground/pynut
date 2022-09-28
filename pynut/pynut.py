""" Binary NutMeg Reader for Python """

import os
import re
import errno
import string
import random
from typing import NamedTuple
import numpy as np
import pandas as pd

def _read_next_line_pattern( raw: bytes, pattern: str, reverse: bool = False
                           ) -> str:
    pattern_enc = pattern.encode()
    pattern_idx = raw.rfind(pattern_enc) if reverse else raw.find(pattern_enc)
    return_idx  = raw.find(b'\n', pattern_idx)
    dec         = raw[pattern_idx:return_idx].decode()
    return dec.split(pattern + ':')[1].strip() if dec else ''

def _read_next_block_pattern( raw: bytes, pattern1: str, pattern2: str
                            , reverse: bool = True ) -> dict:
    enc1   = pattern1.encode()
    enc2   = pattern2.encode()
    p1_idx = raw.rfind(enc1) if reverse else raw.find(enc1)
    p2_idx = raw.find(enc2, p1_idx)
    dec    = raw[p1_idx:p2_idx].decode().removeprefix(pattern1).split('\n')
    return { j[1]: {'index': j[0], 'unit': j[2].split(' ')[0] }
             for j in [ i.split('\t') for i in [ d.strip() for d in dec ]
                      ] if j[0] }

def _get_analys_type(plot_name: str) -> str:
    analysis_pattern = "`(.*?)'"
    analysis_match   = re.search(analysis_pattern, plot_name)
    return analysis_match.group(1) if analysis_match\
            else 'dummy_' + ''.join(random.sample(string.ascii_letters, 5))

NutPlot = NamedTuple( 'NutPlot'
                    , [ ( 'plot_name', str )
                      , ( 'flags', str )
                      , ( 'n_points', int )
                      , ( 'variables', list[str] )
                      , ( 'data', np.array )
                      ] )

NutMeg = NamedTuple( 'NutMeg'
                   , [ ( 'title', str )
                     , ( 'date', str )
                     , ( 'plots', dict[str, NutPlot] )
                     ] )

def parse_plot(raw_plot: bytes, values_id: bytes = b'\nBinary:\n') -> NutPlot:
    """
    Parse plot segment of raw data into NutPlot object.
    """
    plot_name   = _read_next_line_pattern(raw_plot, 'Plotname')
    flags       = _read_next_line_pattern(raw_plot, 'Flags')
    n_variables = int(_read_next_line_pattern(raw_plot, 'No. Variables'))
    n_points    = int(_read_next_line_pattern(raw_plot, 'No. Points'))
    variables   = _read_next_block_pattern(raw_plot, 'Variables:', 'Binary:')
    dtypes      = np.dtype( { 'names': list(variables.keys())
                            , 'formats': ( n_variables
                                         * ( [np.complex128]
                                             if 'complex' in flags
                                             else [np.float64])) }
                          ).newbyteorder('>')
    data_start  = raw_plot.find(values_id) + len(values_id)
    raw_data    = raw_plot[data_start:]
    data        = np.frombuffer( raw_data, dtype = dtypes
                               , count = max(1, n_points))
    return NutPlot( plot_name = plot_name
                  , flags     = flags
                  , n_points  = n_points
                  , variables = variables
                  , data      = data )

def to_df(nut: NutPlot) -> pd.DataFrame:
    """ Turn NutPlot into pandas DataFrame. """
    return pd.DataFrame(nut.data.byteswap().newbyteorder())

def read_raw( file_name: str, plots_id: bytes = b'Plotname'
                ) -> NutMeg:
    """
    Parse NutMag raw/binary file.
    """
    if not os.path.isfile(file_name):
        raise( FileNotFoundError( errno.ENOENT
                                , os.strerror(errno.ENOENT)
                                , file_name ) )

    with open(file_name, 'rb') as raw_file:
        raw_data = raw_file.read()

    title     = _read_next_line_pattern(raw_data, 'Title')
    date      = _read_next_line_pattern(raw_data, 'Date')
    psx       = [ idx.start() for idx in re.compile(plots_id).finditer(raw_data) ]
    pex       = psx[1:] + [len(raw_data)]
    raw_plots = [ raw_data[sx:ex] for sx,ex in zip(psx,pex) ]
    plots     = { _get_analys_type( _read_next_line_pattern(plt, 'Plotname')
                              ): parse_plot(plt) for plt in raw_plots }
    return NutMeg( title = title
                 , date  = date
                 , plots = plots )

def plot_dict(nut: NutMeg) -> dict[str, pd.DataFrame]:
    """ Named Tuple as Dict with DataFrames. """
    return { n: to_df(p) for n,p in nut.plots.items() }

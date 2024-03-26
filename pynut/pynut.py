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
    try:
        dec     = raw[pattern_idx:return_idx].decode().split(pattern + ':')[1].strip()
    except:
        dec     = None
    return dec or ''

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

def _random_name(n: int = 5) -> str:
    return 'dummy_' + ''.join( random.sample( string.ascii_letters, n ))

def _get_analys_type(plot_name: str) -> str:
    analysis_pattern = "`(.*?)'"
    analysis_match   = re.search(analysis_pattern, plot_name)
    analysis_type    = ( plot_name if any([ plot_name.startswith(at)
                                            for at in ANALYSIS_TYPES ]) else
                            ( analysis_match.group(1) if analysis_match else
                                _random_name(5) ) )
    return analysis_type

ANALYSIS_TYPES: list[str] = [ 'ac', 'dc', 'dcmatch', 'dcop'
                            , 'noise', 'stb', 'tran', 'xf' ]

NutPlot = NamedTuple( 'NutPlot'
                    , [ ('plot_name', str)
                      , ('analysis',  str)
                      , ('flags',     str)
                      , ('n_points',  int)
                      , ('variables', list[str])
                      , ('data', np.array)
                      ] )

NutMeg = NamedTuple( 'NutMeg'
                   , [ ('title',  str)
                     , ('date',   str)
                     , ('plots',  dict[str, NutPlot])
                     , ('offset', int)
                     ] )

def parse_plot(raw_plot: bytes, values_id: bytes = b'\nBinary:\n') -> NutPlot:
    """
    Parse plot segment of raw data into NutPlot object.
    """
    plot_name   = _read_next_line_pattern(raw_plot, 'Plotname')
    analysis    = _get_analys_type(plot_name)
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
                  , analysis  = analysis
                  , flags     = flags
                  , n_points  = n_points
                  , variables = variables
                  , data      = data )

def to_df(nut: NutPlot) -> pd.DataFrame:
    """ Turn NutPlot into pandas DataFrame. """
    return pd.DataFrame(nut.data.byteswap().newbyteorder())

def read_raw( file_name: str, plots_id: bytes = b'Plotname', off_set: int = 0
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

    hdr_len   = raw_data.find(plots_id)
    hdr       = raw_data[:hdr_len]
    bdy       = raw_data[(hdr_len + off_set):]
    title     = _read_next_line_pattern(hdr, 'Title')
    date      = _read_next_line_pattern(hdr, 'Date')
    psx       = [idx.start() for idx in re.compile(plots_id).finditer(bdy)]
    pex       = psx[1:] + [len(bdy)]
    raw_plots = [ bdy[sx:ex] for sx,ex in zip(psx,pex) ]
    plots     = { _read_next_line_pattern(plt, 'Plotname'): parse_plot(plt)
                  for plt in raw_plots }
    offset    = len(raw_data) - hdr_len
    return NutMeg( title  = title
                 , date   = date
                 , plots  = plots
                 , offset = offset )

def plot_dict(nut: NutMeg) -> dict[str, pd.DataFrame]:
    """ Named Tuple as Dict with DataFrames. """
    return { n: to_df(p) for n,p in nut.plots.items()
           } | {"offset" : nut.offset}

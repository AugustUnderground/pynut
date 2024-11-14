import pandas as pd
import pynut as pn

raw = pn.read_raw('../char-gan/testbench.raw') 
dct = pn.plot_dict(raw)
dat = pd.concat(list(dct.values())[:-1], ignore_index = True)

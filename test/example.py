import pynut as pn
from matplotlib import pyplot as plt

## Example RC
RC1_RAW = './test/rc1.raw'

## Parsed Binary Data
raw = pn.read_raw(RC1_RAW)

## Transient Analysis Result
tran = raw.plots['tran']

## Plot Data
fig, axs = plt.subplots(1,1, figsize=(8,8))
axs.plot(tran.data['time'], tran.data['O'])
axs.set_title(tran.plot_name)
axs.set_xlabel('time (s)')
axs.set_ylabel('O (V)')
axs.grid('on')
plt.show()

# PyNut

You can pronounce it :peanuts: when you think no one's listening.

## Installation

With `pip`:

```sh
$ pip install git+https://github.com/augustunderground/pynut.git
```

From source:

```sh
$ git clone https://github.com/augustunderground/hace.git
$ pushd hace
$ pip install .
```

## Example

```python
import pynut as pn

file = './test/rc2.raw'

raw = pn.read_raw(file)
```

Or see `test/example.py`.

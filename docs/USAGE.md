# Usage

## Package

To use the very useless python classes of this example import the

```python
from my_package.asdf import ASDF

asdf = ASDF()
# ASDF init done

asdf.print_hello(who='Carl')
# Hello Carl
```

To get a list of random integers the
[**`my_package.qwertz.QWERTZ.get_list_of_int`**](my_package.qwertz.QWERTZ.get_list_of_int)
function can be used. The list will contain 5 integers between 0 and 100 by
default. The `how_long` argument can be used to change the number of elements
in the returned list.

## Create docs

### Installation

Python3 must be installed on your system. Check the current Python version
with the following command

```bash
python --version
python3 --version
```

Depending on which command `Python 3.x.y` (with x.y as some numbers) is
returned, use that command to proceed.

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r docs/requirements.txt
```

### Sphinx link checks

```bash
sphinx-build \
	docs/source docs/build/html \
	-d docs/build/docs_doctree \
	--color -blinkcheck -bhtml -W
```

### Sphinx build

```bash
sphinx-build \
	docs/source docs/build/linkcheck \
	-d docs/build/docs_doctree \
    --color -W
```

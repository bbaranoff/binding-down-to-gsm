# Template for the Read the Docs tutorial

[![Documentation Status](https://readthedocs.org/projects/brainelectronics-tutorial-template/badge/?version=latest)](https://brainelectronics-tutorial-template.readthedocs.io/en/latest/?badge=latest)
![Release](https://img.shields.io/github/v/release/brainelectronics/rtd-tutorial-template?include_prereleases&color=success)
![Python](https://img.shields.io/badge/python3-Ok-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Example RTD template project

---------------

This GitHub template includes fictional Python library
with some basic Sphinx docs.

The created documentation can be found at

https://brainelectronics-tutorial-template.readthedocs.io/en/latest/

<!-- MarkdownTOC -->

- [Getting started](#getting-started)
	- [Install required tools](#install-required-tools)
	- [Create documentation](#create-documentation)

<!-- /MarkdownTOC -->

## Getting started

### Install required tools

Python3 must be installed on your system. Check the current Python version
with the following command

```bash
python --version
python3 --version
```

Depending on which command `Python 3.x.y` (with x.y as some numbers) is
returned, use that command to proceed.

```bash
# create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install and upgrade required packages
pip install -U -r docs/requirements.txt
```

### Create documentation

```bash
# perform link checks
sphinx-build docs/ docs/build/linkcheck -d docs/build/docs_doctree/ --color -blinkcheck -j auto -W

# create documentation
sphinx-build docs/ docs/build/html/ -d docs/build/docs_doctree/ --color -bhtml -j auto -W
```

The created documentation can be found [here](docs/build/html).

Errors thrown due to invalid `autosectionlabels` or by invalid references to
files not being part of the [`docs/`](docs) folder are ignored, see
[`suppress_warnings` in docs config](docs/config.py)

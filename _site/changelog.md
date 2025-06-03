# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [x.y.z] - yyyy-mm-dd
### Added
### Changed
### Removed
### Fixed
-->
<!--
RegEx for release version from file
r"^\#\# \[\d{1,}[.]\d{1,}[.]\d{1,}\] \- \d{4}\-\d{2}-\d{2}$"
-->

## Released
## [0.5.0] - 2022-12-17
### Added
- Example for ReStructuredText evaluation directive to show a warning and a notes highlighted text

### Changed
- Removed outdated command to convert Markdown files to ReStructuredText files

### Fixed
- Call to generate sphinx documentation in USAGE

## [0.4.0] - 2022-12-06
### Added
- Usage guide for building docs locally in root README
- `changelog_link.rst` added to [docs](docs) to include this changelog from
  its real location without further relocation before building the docs

### Changed
- Relocate files of `docs/source` into `docs` directly
- Replace ReStructuredText references in Markdown files of [docs](docs)
- `docutils >=0.14,<0.18` is required to build the docs
- Sphinx extensions sorted aphabetically in [`config.py`](docs/config.py)

### Removed
- Documentation build process is no longer depending in `m2rr` package
- Unused batch file and Makefile

## [0.3.0] - 2022-10-29
### Added
- Add link to created documentation to root README

### Fixed
- Subtitle of root README does not reference MicroPython

## [0.2.0] - 2022-10-29
### Added
- Docs badge to root README, see [#2][ref-issue-2]

### Changed
- Converted root README from Markdown to ReStructuredText

## [0.1.0] - 2022-10-29
### Added
- This changelog file
- [.gitignore](.gitignore) file
- Docs [requirements.txt](docs/requirements.txt) file to setup tools for
  documentation generation
- [.readthedocs.yaml](.readthedocs.yaml) file to define custom actions after
  the default installation and before the actual docs build process
- [Dummy python package files](my_package/)
- [Script to convert](docs/convert_md2rst.py) Markdown to ReStructuredText
  files for Sphinx

<!-- Links -->
[Unreleased]: https://github.com/brainelectronics/rtd-tutorial-template/compare/0.5.0...main

[0.5.0]: https://github.com/brainelectronics/rtd-tutorial-template/tree/0.5.0
[0.4.0]: https://github.com/brainelectronics/rtd-tutorial-template/tree/0.4.0
[0.3.0]: https://github.com/brainelectronics/rtd-tutorial-template/tree/0.3.0
[0.2.0]: https://github.com/brainelectronics/rtd-tutorial-template/tree/0.2.0
[0.1.0]: https://github.com/brainelectronics/rtd-tutorial-template/tree/0.1.0

[ref-issue-2]: https://github.com/brainelectronics/rtd-tutorial-template/issues/2

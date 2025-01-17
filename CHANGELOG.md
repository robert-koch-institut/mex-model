# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changes

### Deprecated

### Removed

### Fixed

### Security

## [3.4.0] - 2024-12-18

### Changes

- type of Distribution.title is now a Text array field, instead of single string

## [3.3.2] - 2024-11-19

### Fixed

- fixed sidebar links in sphinx docs

## [3.3.1] - 2024-11-19

### Fixed

- fixed index.rst file name

## [3.3.0] - 2024-11-19

### Added

- add "$$target" property to model, to help with de-referencing

### Changes

- setup json-schema rendering for sphinx docs
- fix cruft diffs in README, pyproject and requirements

## [3.2.0] - 2024-11-18

## [3.1.0] - 2024-10-28

### Fixed

- fix typo in `BibliographicResource.repositoryURL`

## [3.0.0] - 2024-10-28

### Added

- release script, creating merged-models. Merged models are written to a zip file,
  together with the content of the following directories: i18n, fields, vocabularies.

## [2.5.0] - 2024-06-14

### Changes

- update versions and dependencies

## [2.4.0] - 2024-05-29

### Changes

- switch from poetry to pdm

## [2.3.0] - 2024-03-18

### Added

- pull request template
- cve scan workflow
- CHANGELOG file
- cruft template link
- sphinx configuration and documentation workflow
- open-code workflow
- new partial date type (for YYYY or YYYY-MM formats)
- translation files in PO format
- move vocabularies from mex-common to mex-model

### Changes

- harmonized boilerplate

## [2.2.0] - 2023-12-18

### Added

- first version with changelog

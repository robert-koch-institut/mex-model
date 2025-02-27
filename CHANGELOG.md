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

- removed character and digit tokens from string patterns

### Security

## [3.5.4] - 2025-02-25

### Fixed

- fixed repetition quantifier for doi string pattern

## [3.5.3] - 2025-02-25

### Changes

- BREAKING: update patterns for all URI-like field definitions and add more examples

### Fixed

- BREAKING: fixed patterns for `year_month`, concept/scheme `identifier` and link `url`

## [3.5.2] - 2025-02-12

### Fixed

- expand the pattern for DOI Urls as these can also contain lowercase letters.

## [3.5.1] - 2025-01-29

### Fixed

- make altLabel property for vocabularies always a list

## [3.5.0] - 2025-01-29

### Changes

- add new vocab items and altLabels to existing mimeTypes

### Fixed

- fix gnd-id pattern for organization models

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

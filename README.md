# MEx model

Conceptual and machine-readable versions of the MEx metadata model.

[![linting](https://github.com/robert-koch-institut/mex-model/actions/workflows/linting.yml/badge.svg)](https://github.com/robert-koch-institut/mex-model/actions/workflows/linting.yml)

## project

With the Metadata Exchange (MEx) project, the [RKI](https.//www.rki.de) is developing a
transparency platform for finding metadata on the institute's research activities and
data.

Via MEx, metadata will be made findable, accessible and shareable on a daily basis,
as well as available for further research. The goal is to get an overview of what
research data is available, understand its context, and know what needs to be considered
for subsequent use.

The platform is currently in internal trials but will also be made publicly available
and thus be available to external researchers as well as the interested (professional)
public.

For further details, please consult the
[project page](https://www.rki.de/DE/Content/Forsch/MEx/MEx_node.html).

## package

The `mex-model` repository contains two models:

- the conceptual model, which is mainly used to facilitate interoperability with other metadata schemas and models
- the json schema, which represents the conceptual model in a format that can be used for technical implementation in applications

## license

This package is licensed under the [MIT license](/LICENSE). Other components of the
MEx project will be released under the same license in the future.

## development

### installation

- install `python3.11` in your preferred way
- on unix run `make install`
- on windows run `.\mex.bat install`

### linting

- on unix run `make test`
- on windows run `.\mex.bat test`

### updating dependencies

- update global dependencies in `requirements.txt` manually
- update git hooks with `pre-commit autoupdate`

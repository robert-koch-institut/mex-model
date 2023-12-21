# MEx model

Conceptual and machine-readable versions of the MEx metadata model.

[![linting](https://github.com/robert-koch-institut/mex-model/actions/workflows/linting.yml/badge.svg)](https://github.com/robert-koch-institut/mex-model/actions/workflows/linting.yml)

## project

The Metadata Exchange (MEx) project is committed to improve the retrieval of RKI
research data and projects. How? By focusing on metadata: instead of providing the
actual research data directly, the MEx metadata catalog captures descriptive information
about research data and activities. On this basis, we want to make the data FAIR[^1] so
that it can be shared with others.

Via MEx, metadata will be made findable, accessible and shareable, as well as available
for further research. The goal is to get an overview of what research data is available,
understand its context, and know what needs to be considered for subsequent use.

For the pilot phase of the MEx project, the RKI cooperated with D4L data4life gGmbH, 
where we jointly explored the vision of a FAIR metadata catalog and developed concepts 
based on this. With the successful conclusion of the pilot phase, the partnership with D4L ended.

After an internal launch, the metadata will also be made publicly available and thus be
available to external researchers as well as the interested (professional) public to
find research data from the RKI.

For further details, please consult our
[project page](https://www.rki.de/DE/Content/Forsch/MEx/MEx_node.html).

[^1]: FAIR is referencing the so-called
[FAIR data principles](https://www.go-fair.org/fair-principles/) – guidelines to make
data Findable, Accessible, Interoperable and Reusable.

## package

The `mex-model` repository contains the MEx metadata model in two formats.

- `/docs` contains the conceptual model, which is mainly used to facilitate
  interoperability with other metadata schemas and models
- `mex/model` holds the JSON schema, which represents the conceptual model in a format
  that can be used for technical implementation in applications

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

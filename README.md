# MEx model

JSON schema files defining the MEx metadata model.

[![cookiecutter](https://github.com/robert-koch-institut/mex-model/actions/workflows/cookiecutter.yml/badge.svg)](https://github.com/robert-koch-institut/mex-template)
[![cve-scan](https://github.com/robert-koch-institut/mex-model/actions/workflows/cve-scan.yml/badge.svg)](https://github.com/robert-koch-institut/mex-model/actions/workflows/cve-scan.yml)
[![documentation](https://github.com/robert-koch-institut/mex-model/actions/workflows/documentation.yml/badge.svg)](https://robert-koch-institut.github.io/mex-model)
[![linting](https://github.com/robert-koch-institut/mex-model/actions/workflows/linting.yml/badge.svg)](https://github.com/robert-koch-institut/mex-model/actions/workflows/linting.yml)
[![open-code](https://github.com/robert-koch-institut/mex-model/actions/workflows/open-code.yml/badge.svg)](https://gitlab.opencode.de/robert-koch-institut/mex/mex-model)

## Project

The Metadata Exchange (MEx) project is committed to improve the retrieval of RKI
research data and projects. How? By focusing on metadata: instead of providing the
actual research data directly, the MEx metadata catalog captures descriptive information
about research data and activities. On this basis, we want to make the data FAIR[^1] so
that it can be shared with others.

Via MEx, metadata will be made findable, accessible and shareable, as well as available
for further research. The goal is to get an overview of what research data is available,
understand its context, and know what needs to be considered for subsequent use.

RKI cooperated with D4L data4life gGmbH for a pilot phase where the vision of a
FAIR metadata catalog was explored and concepts and prototypes were developed.
The partnership has ended with the successful conclusion of the pilot phase.

After an internal launch, the metadata will also be made publicly available and thus be
available to external researchers as well as the interested (professional) public to
find research data from the RKI.

For further details, please consult our
[project page](https://www.rki.de/DE/Aktuelles/Publikationen/Forschungsdaten/MEx/metadata-exchange-plattform-mex-node.html).

[^1]: FAIR is referencing the so-called
[FAIR data principles](https://www.go-fair.org/fair-principles/) – guidelines to make
data Findable, Accessible, Interoperable and Reusable.

**Contact** \
For more information, please feel free to email us at [mex@rki.de](mailto:mex@rki.de).

### Publisher

**Robert Koch-Institut** \
Nordufer 20 \
13353 Berlin \
Germany

## Package

Our metadata model is represented as JSON schema in `mex/model`. There, we defined 1.
`entities`, described by their properties, 2. `fields`, small objects, that are used as
`$ref` for certain properties, 3. an `extension`, which contains additional properties,
that are not in scope of the JSON schema definition, 4. `i18n` files, that hold
translations of the properties and are to be used in the context of user interfaces and
5. `vocabularies`, which are used in context of the `entities`. A more detailed
description of the model's context can be found in `/docs/index.rst`.

## License

This package is licensed under the [MIT license](/LICENSE). All other software
components of the MEx project are open-sourced under the same license as well.

## Development

### Installation

- install python3.11 on your system
- on unix, run `make install`
- on windows, run `.\mex.bat install`

### Linting

- run all linters with `make lint` or `.\mex.bat lint`

### Updating dependencies

- update boilerplate files with `cruft update`
- update global requirements in `requirements.txt` manually
- update git hooks with `pre-commit autoupdate`
- update package dependencies using `pdm update-all`
- update github actions in `.github/workflows/*.yml` manually

### Creating release

- run `pdm release RULE` to release a new version where RULE determines which part of
  the version to update and is one of `major`, `minor`, `patch`.

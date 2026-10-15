# Entity conventions

## Extracted and Merged Entities

Both the `Extracted[EntityType]` and `Merged[EntityType]` variants share the same set of descriptive properties. The Extracted variant additionally carries the four mandatory provenance properties `hadPrimarySource`, `identifierInPrimarySource`, `identifier`, and `stableTargetId`. The Merged variant only carries `identifier` alongside the descriptive properties. The property `supersededBy` is unique to the Merged variant and is not applicable for Extracted entities.

The Merged variant is the normalized, deduplicated record that consolidates descriptions from one or more primary sources. If a Merged item has been superseded by another, e.g. following deduplication, the `supersededBy` property will point to the preferred Merged item.

### When to use

`Extracted[EntityType]` is used when an item is extracted from a primary source system via an ETL pipeline. Each extracted record represents the item as described by that specific source, carrying the provenance properties that trace it back to its origin.

`Merged[EntityType]` is used referencing an item from another entity, or when consuming metadata in the catalogue or downstream systems. All properties that are relations to other entities use the identifier of a Merged entity in their `$ref` attribute, i.e. `ExtractedResource.contributor` referencing a `MergedPerson` using `"$ref": "/mex/model/entities/merged-person#/identifier"`.

The following sections lay out the entities without their Extracted or Merged variant, but their general characteristics, that are independent from the variants.

All sample JSON instances show examples of the Merged variant, which is considered sufficient within the scope of this specification.

## AccessPlatform

The `AccessPlatform` entity describes a technical system or service that provides access to distributions and/or resources. It corresponds to `dcat:DataService`.

### When to use

Use `AccessPlatform` to describe any technical system, API, or service through which a dataset or distribution can be accessed. For example, a REST API, a file server, a database interface, or a web portal. The entity captures both the technical characteristics of the access mechanism and the organizational responsibility for it.

`AccessPlatform` should not be confused with `Distribution`, which describes a specific representation or download of a dataset. An `AccessPlatform` is the system through which one or more distributions are made available. A `Distribution` is the artefact that is made available through it.

### Common pitfalls

* Confusing `AccessPlatform` with `Distribution`: a common mistake is creating an `AccessPlatform` record for each individual file or download rather than for the system that serves them. One `AccessPlatform` may serve multiple `Distribution` entities.
* Leaving `technicalAccessibility` inconsistent: marking a platform as externally accessible when it is in fact only reachable within the RKI network, or vice versa. This has downstream implications for access control and catalogue visibility.
* Omitting `unitInCharge`, when `technicalAccessibility` is "internal": while optional, this property is important for operational accountability.

### Schema detail

```{mex-entity} AccessPlatform
```

### Example JSON Instances

#### Merged AccessPlatform

```json
{
  "description": [{"value": "REST API providing access to infectious disease surveillance data.", "language": "en"}],
  "endpointURL": {"url": "https://survstat.rki.de/api/v2"},
  "identifier": "gglGQVGwZNJtqYDkW4N8jL",
  "technicalAccessibility": "https://mex.rki.de/item/technical-accessibility-1", # internal
  "title": [{"value": "SurvStat API", "language": "en"}],
  "unitInCharge": ["hJKL9mNoPqRsTuVwXyZ123"]
}
```

## Activity

The `Activity` entity describes any activity carried out by the RKI, whether it is a funded research project, a statutory surveillance task, or any other organised undertaking. It corresponds to `prov:Activity` and serves primarily to provide contextual information for `Resource` entities.

### When to use

Use `Activity` to describe a research project, a statutory task performed under federal law, or any other organised activity conducted at the RKI. Activities provide essential context for datasets. A `Resource` can reference the `Activity` that generated it via the wasGeneratedBy property.

`Activity` should not be confused with `Resource`, which describes the data itself. An `Activity` is the process or project that produced or is associated with data. A `Resource` is the dataset that resulted from or is used within that activity.

### Common pitfalls

* Confusing `contact` and `responsibleUnit`: `contact` is a point of enquiry (unit, or contact point), while `responsibleUnit` specifically denotes organisational accountability. Both are mandatory and should not be used interchangeably.
* Confusing `involvedPerson` and `contact`: persons involved in carrying out the activity belong in `involvedPerson`, while `contact` is for the unit a user should reach out to with questions.
* Omitting `start` and `end`: while optional, these are important for catalogue discoverability and for understanding whether an activity is ongoing or concluded.
* Using plain strings for `theme` or `activityType`: these require Concept URIs from their respective vocabularies, not free-text values.

### Schema detail

```{mex-entity} Activity
```

### Example JSON instances

#### Merged Activity

```json
{
  "activityType": ["https://mex.rki.de/item/activity-type-1"] # Third Party funded Project,
  "contact": ["cKMPkdHHTky6TF6hqMdbe7"],
  "end": ["2024-12-31"],
  "identifier": "gglGQVGwZNJtqYDkW4N8jL",
  "responsibleUnit": ["hJKL9mNoPqRsTuVwXyZ123"],
  "start": ["2020-03"],
  "title": [
    {"value": "COVID-19 Surveillance", "language": "en"},
    {"value": "COVID-19-Surveillance", "language": "de"}
  ]
}
```

## BibliographicResource

The `BibliographicResource` entity describes a publication, article, report or other bibliographic output. It corresponds to `dcterms:BibliographicResource`.

### When to use

Use `BibliographicResource` to describe any publication associated with RKI research. This includes journal articles, reports, preprints, book chapters, or similar outputs. It is typically linked from an `Activity` via the `publication` property.

`BibliographicResource` should not be confused with `Resource`, which describes a dataset or data collection. A `BibliographicResource` is a published document, a `Resource` is research data.

### Common pitfalls

* Duplicating publications across sources: the same `publication` may be present in multiple source systems. Ensure `stableTargetId` is consistent to allow proper merging.
* Confusing `BibliographicResource` with `Resource`: a PDF report describing a dataset is a `BibliographicResource`. The dataset itself is a `Resource`.

### Schema detail

```{mex-entity} BibliographicResource
```

### Example JSON instances

#### Merged BibliographicResource

```json
{
  "accessRestriction": "https://mex.rki.de/item/access-restriction-1", # open
  "bibliographicResourceType": ["https://mex.rki.de/item/bibliographic-resource-type-1"], # Book
  "creator": ["cKMPkdHHTky6TF6hqMdbe7"],
  "doi": "https://doi.org/10.2807/1560-7917.ES.2022.27.46.2200849",
  "identifier": "mNoPqRsTuVwXyZ1234AbCd",
  "issued": "2022-11-17",
  "journal": [{"value": "Eurosurveillance", "language": "en"}],
  "language": ["https://mex.rki.de/item/language-1"], # German
  "license": "https://mex.rki.de/item/license-1",  # CC-BY-4.0
  "publicationYear": "2022",
  "title": [{"value": "Epidemiological characterisation of SARS-CoV-2 variants in Germany", "language": "en"}]
}
```

## Concept Scheme

A `ConceptScheme` is a controlled list of concepts - a vocabulary. It corresponds to `skos:ConceptScheme`. All vocabularies in use within the MEx system are defined in `model/vocabularies/concept-schemes.json`.

### When to use

Both `ConceptScheme` and [Concept](#concept) are the only entity types that are excepted from the Extracted and Merged principle. Vocabularies used within the MEx system are not extracted from primary sources but manually curated within the mex-model repository. See chapter [Controlled vocabularies](controlled-vocabularies.md) for further details.

`ConceptScheme` gets confused it with `Concept`, which describes a term within the vocabulary, while `ConceptScheme`describes the vocabulary itself.

### Schema detail

```{mex-entity} ConceptScheme
```

### Example JSON instances

See `mex-model/vocabularies/concept-schemes.json` for details.

```json
{
   "description": [
    {"de": "Dieses Vokabular basiert auf dem Dublin Core Collection Description Frequency Vokabular, verfügbar unter https://www.dublincore.org/specifications/dublin-core/collection-description/frequency/.",
    "en": "This vocabulary is based on the Dublin Core Collection Description Frequency Vocabulary, available at https://www.dublincore.org/specifications/dublin-core/collection-description/frequency/."
    }
   ],
  "identifier": "https://mex.rki.de/item/frequency",
  "label": "Frequency vocabulary"
}

```

## Concept

A `Concept` is a term of a controlled list (vocabulary). It corresponds to `skos:Concept`. The vocabularies in use within the MEx system are stored in `model/vocabularies`.

### When to use

Both `Concept` and [ConceptScheme](#concept-scheme) are the only entity types that are excepted from the Extracted and Merged principle. Vocabularies used within the MEx system are not extracted from primary sources but manually curated within the mex-model repository. See chapter [Controlled vocabularies](controlled-vocabularies.md) for further details.

`Concept` gets confused it with `ConceptScheme`, which describes the vocabulary, while `Concept`describes a single term within the vocabulary.

### Schema detail

```{mex-entity} Concept
```

### Example JSON instances

See `mex-model/vocabularies/[vocabulary].json` for details.

```json
{
    "altLabel": [
            {
                "de": "PHDR",
                "en": "PHDR"
            }
    ],
    "definition": [
            {
                "de": "Bevölkerungsbezogene Gesundheitsdatenregisterdaten (Register der öffentlichen Gesundheit)",
                "en": "Data from population-based health data registries such as public health registries"
            }
    ],
    "exactMatch": [
            "https://hdeu-dcat.data.health.europa.eu/resource/authority/healthcategories/PHDR"
    ],
    "identifier": "https://mex.rki.de/item/health-category-16",
    "inScheme": "https://mex.rki.de/item/health-category",
    "prefLabel": {
            "de": "Bevölkerungsbezogene Gesundheitsregisterdaten",
            "en": "Data from population-based health data registries"
    }
}
```

## Consent

The `Consent` entity records a data subject's consent for the use of their personal data. It is aligned with the W3C Data Privacy Vocabulary `dpv:Consent`.

### When to use

Use `Consent` to document GDPR-relevant consent records associated with research data.

### Common pitfalls

* Conflating consent status with access restriction: consent is a GDPR-compliant declaration of a data subject's (an instance of `Person`) declaration. Access restriction on a `BibliographicResource`, `Resource` or `Distribution` indicates an access level of a resource or technical system. These are distinct and should not substitute for one another.
* Conflicting `Consent` items: For every person item, there is a corresponding consent item. When Person items are extracted from various primary source systems, duplicates of person items may occur. These may also have conflicting consent statuses. These items cannot be merged.

### Schema detail

```{mex-entity} Consent
```

### Example JSON instances

#### Merged Consent

```json
{
  "hasConsentStatus": "https://mex.rki.de/item/consent-status-1", # Invalid for Processing
  "hasDataSubject": "cKMPkdHHTky6TF6hqMdbe7",
  "identifier": "qRsTuVwXyZ1234AbCdEfGh",
  "isIndicatedAtTime": "2022-09-30T20:48:35Z"
}
```

## ContactPoint

The `ContactPoint` entity represents a shared email address or functional account used by a team or organizational unit. It corresponds to `vcard:Kind`.

### When to use

Use `ContactPoint` when a contact for an entity is a shared functional address, such as a team inbox, rather than an individual person. It provides a stable point of contact that does not depend on a specific individual remaining in post.

`ContactPoint` should not be confused with `Person`, which represents an individual. If a named individual is mentioned, use a reference to a `MergedPerson`.

### Common pitfalls

* Using a personal mail address as a `ContactPoint`: `ContactPoint` should always reference group or functional mail addresses.

### Schema detail

```{mex-entity} ContactPoint
```

### Example JSON instances

#### Merged ContactPoint

```json
{
  "email": ["mex@rki.de"],
  "identifier": "hJKL9mNoPqRsTuVwXyZ123"
}
```

## Distribution

The `Distribution` entity describes a specific representation or downloadable form of a dataset. It corresponds to `dcat:Distribution`.

### When to use

Use `Distribution` to describe a specific file, format, or access form of a Resource, for example a CSV file, an API response, or a ZIP archive. A single Resource may have multiple `Distribution` items, one per format or access method.

`Distribution` should not be confused with `AccessPlatform`. A `Distribution` is the artefact, the specific file or data representation. An `AccessPlatform` is the system through which it is served.

### Common pitfalls

* Creating one `Distribution` per dataset instead of per format: if a dataset is available in three formats, three `Distribution` records should exist.
* Confusing `accessURL` and `downloadURL`: `accessURL` points to a page where the distribution can be accessed. `downloadURL` points directly to the downloadable file. Both may be present simultaneously.

### Schema detail

```{mex-entity} Distribution
```

### Example JSON instances

#### Merged Distribution

```json
{
  "accessUrl": ["https://example.org/datasets/abc/distribution.csv"],
  "downloadUrl": ["https://example.org/datasets/abc/distribution.csv"],
  "identifier": "rStUvWxYzA1234AbCdEfGh",
  "mediaType": ["https://mex.rki.de/item/mime-type-7"] # text/csv
}
```

## Location

`Location` describes a geographical space on the earth such as a country, city or region. It corresponds to `dct:Location`.

### When to use

Use `Location` for geographical entities, i.e. when describing the geographical coverage of a dataset/data source.

### Common pitfalls

* Duplicating locations across sources: the same location may appear in multiple source systems under slightly different names. Further infos on de-duplication in chapter [How the model works](how-the-model-works.md). The MEx systems uses Wikidata as a authority to identify and ingest locations into the database.

### Schema detail

```{mex-entity} Location
```

### Example JSON instances

#### Merged Location

```JSON
{
  "geoNamesId": [
    "https://www.geonames.org/2950159",
    "https://www.geonames.org/2950157"
  ],
  "identifier": "",
  "name": [
    {"language": "de", "value": "Berlin"},
    {"language": "en", "value": "Berlin"}
  ],
  "wikidataId": [
    "http://www.wikidata.org/entity/Q64"
  ]
}
```

## Organization

The `Organization` entity describes an institution, a legal or administrative body. It corresponds to `foaf:Organization` and `org:Organization`.

### When to use

Use `Organization` to represent an external institution, for example a funding body, a cooperating university, or an international partner organization.

`Organization` should thus not be confused with `OrganizationalUnit`, which represents departments and units within the RKI.

### Common pitfalls

* Using `Organization` for RKI units: internal RKI departments and units must be modelled as `OrganizationalUnit`.
* Duplicating organizations across sources: the same external institution may appear in multiple source systems under slightly different names. Further infos on de-duplication in chapter [How the model works](how-the-model-works.md). The MEx systems uses Wikidata as a authority to identify and ingest organizations into the database.

### Schema detail

```{mex-entity} Organization
```

### Example JSON instances

#### Merged Organization

```json
{
  "identifier": "tUvWxYzA1234AbCdEfGhIj",
  "officialName": [
    {"language": "de", "value": "Robert Koch-Institut"}],
  "shortName": [
    {"language": "de", "value": "RKI"}],
  "website": [{"language": "de", "title": "Offizielle RKI-Website", "url": "https://www.rki.de/"}],
  "wikidataId": ["http://www.wikidata.org/entity/Q679041"]
}
```

## OrganizationalUnit

The `OrganizationalUnit` entity represents a department or unit within the RKI. It corresponds to `org:OrganizationalUnit`.

### When to use

Use `OrganizationalUnit` to represent any internal RKI unit: a department or unit. Organizational units can be arranged in a hierarchy using the `parentUnit` and `unitOf` properties.

`OrganizationalUnit` should not be confused with `Organization`, which represents an institution. If the unit is part of the RKI, use `OrganizationalUnit`.

### Common pitfalls

* Confusing `OrganizationalUnit` with `Organization`: While the laater is an institution, a unit is part of an institution. Within the MEx system `OrganizationalUnit` is only used to represent internal units of RKI.
* Not modelling the hierarchy: `parentUnit` and `unitOf` should be populated.

### Schema detail

```{mex-entity} OrganizationalUnit
```

### Example JSON instances

#### Merged OrganizationalUnit

```json
{
  "identifier": "cDeFgHiJkLmN1234OpQrSt",
  "officialName": [{"language": "en", "value": "Center for International Health Protection"}],
  "parentUnit": ["tUvWxYzA1234AbCdEfGhIj"],
  "shortName": ["ZIG"]
}
```

## Person

The `Person` entity represents an individual researcher, RKI staff member, or contributor associated with RKI activities or resources. It corresponds to `foaf:Person`.

### When to use

Use `Person` to represent a named individual, for example a person involved in an activity, a dataset contributor, or a publication author. Person records are mainly sourced from RKI's directory system, which functions as a authority for all RKI staff members. Other Person items are derived from primary sources such as authors of publications (Bibliographic Resource items). Person records and may be enriched with authority identifiers such as ORCID, which we use as an additional authority service for external persons, who can be as contributors to resources.

Person should not be confused with `ContactPoint`, which represents a shared functional address rather than an individual. If the contact is role-based or shared, use `ContactPoint`.

### Common pitfalls

* Referencing persons by `name` string instead of `identifier`: all references to persons in other entities must use the `MergedPerson` identifier, not a name string.
* Creating duplicate person records: the same individual may appear in multiple source systems. Take care identifying different persons carrying the same name.

### Schema detail

```{mex-entity} Person
```

### Example JSON instances

#### Merged Person

```json
{
  "affiliation": ["cDeFgHiJkLmN1234OpQrSt"],
  "email": ["ada.lovelace@example.org"],
  "familyName": ["Lovelace"],
  "fullName": ["Ada Lovelace"],
  "givenName": ["Ada"],
  "identifier": "fGhIjKlMnOpQ1234RsTuVw"
}
```

## PrimarySource

The `PrimarySource` entity represents a source system from which metadata is extracted and loaded into MEx. It corresponds to `prov:PrimarySource` and is a foundational provenance concept. Every Extracted entity references a `MergedPrimarySource` via `hadPrimarySource`.

### When to use

Use `PrimarySource` to describe a system, database, or API that feeds metadata into MEx via an extractor pipeline.

`PrimarySource` is established when a new extractor pipeline is set up and registered in the system.

### Common pitfalls

* Confusing `PrimarySource` with the extracted entities it produces: the `PrimarySource` describes the system, not the data it contains.
* Confusing `PrimarySource` with `AccessPlatform`: Whilst a `PrimarySource` can also be an `AccessPlatform`, an `AccessPlatform` is not necessarily the primary source for MEx metadata. A `PrimarySource` is a specific type of data service for MEx that serves as the sole source for metadata extraction. An `AccessPlatform` is used in conjunction with a user-side data service. It may be the case that the system used to access the data and the primary source for metadata extraction are one and the same, but even in this instance there would be two separate elements: a `PrimarySource` and an `AccessPlatform`.
* Leaving `hadPrimarySource` self-referential without documentation: the MEx system itself is its own primary source for `PrimarySource` records. This should be clearly documented in pipeline configurations.

### Schema detail

```{mex-entity} PrimarySource
```

### Example JSON Instances

#### Merged PrimarySource

```json
{
  "identifier": "iJkLmNoPqRsT1234UvWxYz",
  "locatedAt": ["www.example.org/server-address"],
  "title": ["Pathogen Database"]
}
```

## ResourceSeries

The `ResourceSeries` entity describes a collection of resources that are published separately but share characteristics that group them, such as a recurring surveillance report or a longitudinal study with annual data releases. It corresponds to `dcat:DatasetSeries`.

### When to use

Use `ResourceSeries` to represent a named series of related datasets that are released over time or in parts. For example, a weekly epidemiological bulletin where each edition is its own `Resource`, or a multi-wave survey where each wave produces a separate dataset.

`ResourceSeries` should not be confused with `Resource`, which describes a single dataset or data source. A `ResourceSeries` is a container that groups multiple `Resource` entities. It should also not be confused with `VariableGroup`, which groups variables within a single resource rather than grouping resources together.

### Common pitfalls

* Confusing `ResourceSeries` with `Resource`: a `ResourceSeries` never describes data directly, it groups `Resource` entities. If the thing you are describing has distributions, variables, or access restrictions of its own, it is a `Resource`.
* Not linking resources to their series: a `ResourceSeries` is only useful if individual `Resource` entities reference it. Ensure the relationship is established from the resource side.
* Omitting `start`/`end`: while optional, temporal coverage helps catalogue users understand whether the series is ongoing or concluded and what time span it covers.
* Using `ResourceSeries` for one-off collections: if a group of datasets was released once and will not grow, consider whether a single `Resource` with multiple `Distribution` records is more appropriate.

### Schema detail

```{mex-entity} ResourceSeries
```

### Example JSON Instances

#### Merged ResourceSeries

```json
{
  "accrualPeriodicity": "https://mex.rki.de/item/frequency-1", # triennial
  "contact": ["hJKL9mNoPqRsTuVwXyZ123"],
  "description": [
    {"value": "Wöchentliche Veröffentlichungsreihe des RKI zu aktuellen infektionsepidemiologischen Themen.", "language": "de"}
  ],
  "identifier": "mRsExAmPlE14chars01",
  "keyword": [
    {"value": "Infektionsepidemiologie", "language": "de"},
    {"value": "Infectious disease epidemiology", "language": "en"}
  ],
  "publisher": ["tUvWxYzA1234AbCdEfGhIj"],
  "title": [
    {"value": "Epidemiologisches Bulletin", "language": "de"},
    {"value": "Epidemiological Bulletin", "language": "en"}
  ],
  "start": ["2001-01"]
}
```

## Resource

The `Resource` entity is the central entity of the MEx model. It describes a dataset, data collection, or other research data asset. It corresponds to `dcat:Dataset`.

### When to use

Use `Resource` to describe any dataset or data collection produced or managed by RKI, e.g. surveillance data, study data, registry data, or any other structured data asset. Resources are the central objects of discovery in the Metadata Catalogue.

A `Resource` describes the dataset or data source. Its individual file representations are described as `Distribution` entities. The project or activity that produced the resource is described as an `Activity`. Individual variables within it may be described as `Variable` entities.

### Common pitfalls

* Confusing `Resource` with `Distribution`: the `Resource` is the dataset or data source. `Distribution` describes its representations.
* Confusing `Resource` with `BibliographicalResource`: a publication about a dataset is a `BibliographicResource`. The dataset itself is a `Resource`.

### Schema detail

```{mex-entity} Resource
```

### Example JSON instances

#### Merged Resource

```json
{
  "contact": ["hJKL9mNoPqRsTuVwXyZ123"],
  "description": [
    {"language": "de", "value": "Surveillance indicators collected and curated for demonstration purposes."}],
  "distribution": ["rStUvWxYzA1234AbCdEfGh"],
  "identifier": "mNoPqRsTuVwXyZ1234AbCd",
  "publisher": ["tUvWxYzA1234AbCdEfGhIj"],
  "title": ["Surveillance dataset: Example indicators (2021–2024)"]
}
```

## VariableGroup

The `VariableGroup` entity represents a logical grouping of `Variable` entities within a Resource, for example a section of a questionnaire or a thematic cluster of variables in a dataset. It is MEx-specific, but relates roughly to the concept of `csvw:Table`.

### When to use

Use `VariableGroup` when variables within a `Resource` can be meaningfully organized into named groups, e.g. by instrument section, dataset table, topic, or measurement domain. It is optional and should only be used where grouping genuinely aids understanding of the dataset structure.

`VariableGroup` should not be confused with `Variable`. A `VariableGroup` is the container.

### Common pitfalls

* Creating `VariableGroup`s without variable: a group with no member variables provides no value. Ensure that `Variable` entities reference their variable group.
* Over-grouping: not every dataset requires variable groups. Only introduce grouping where it reflects a genuine and meaningful structure in the source data.

### Schema detail

```{mex-entity} VariableGroup
```

### Example JSON instances

#### Merged VariableGroup

```json
{
  "identifier": "sTuVwXyZ1234AbCdEfGhIj",
  "title": ["Case definitions"],
  "usedIn": ["mNoPqRsTuVwXyZ1234AbCd"]
}
```

## Variable

The `Variable` entity describes a single data variable within a resource, for example a column in a dataset or a field in a data dictionary. It corresponds to how `csvw:column` is defined within HealthDCAT-AP.

### When to use

Use `Variable` to describe individual fields or variables within a `Resource`, particularly where variable-level documentation is meaningful for data reuse, for example coded variables, measurement units, or variables with complex value ranges.

`Variable` should not be confused with `VariableGroup`, which is a logical grouping of multiple variables. A `Variable` is the individual field. A `VariableGroup` is the container that organizes related variables.

### Common pitfalls

* Confusing `Variable` with `VariableGroup`: individual fields belong in `Variable`. Use `VariableGroup` only to group related variables logically.
* Not linking variables to their resource: a `Variable` must reference its parent `Resource` to be meaningful.

### Schema detail

```{mex-entity} Variable
```

### Example JSON instances

#### Merged Variable

```json
{
  "belongsTo": ["mPpRrTuVaWcYzB9145CdBw"],
  "datatypeInPrimarySource": "integer",
  "datatypeStandardized": "https://mex.rki.de/item/datatype-standardized-1", # URI
  "description": [
    {"langauge": "de", "value": "Number of reported cases per 100,000 inhabitants over the last 7 days."}],
  "identifier": "pQrStUvWxYzA1234BcDeFg",
  "technicalName": ["7-day_incidence"],
  "usedIn": ["mNoPqRsTuVwXyZ1234AbCd"]
}
```

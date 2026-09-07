# Common Usage Patterns

This section collects practical guidance for the most frequent modelling tasks. It is aimed at data stewards and extractor developers who need to produce valid, well-structured MEx records. Where the advice refers to schema rules, the entity reference pages are the authoritative source. The patterns here are meant as shortcuts.

## Describing a dataset (Resource)

Creating a Resource record is the most common starting point. A resource represents a single dataset, a data source (the entirety of the data collected for a specific purpose, e.g. surveillance of diseases), or data single and collections of samples in the MEx catalogue. Metadata consumers most likely will encounter the model through this entity first.

### Minimal Viable Record

A valid ExtractedResource requires the system-managed fields (`identifier`, `hadPrimarySource`, `identifierInPrimarySource`, `stableTargetId`) plus the following content fields:

| Field | What to provide |
| --- | --- |
| accessRestriction | A Concept URI from the Access Restriction vocabulary. |
| contact | At least one reference to a `MergedContactPoint` or `MergedOrganizationalUnit`. This is who a data consumer should reach out to. |
|description | Free-text summary of what the dataset contains, how it was collected, and what it covers.  |
| keyword | Free-text tags, that describe the character/subject of resource. |
| resourceCreationMethod | At least Concept URI from the Resource Creation Method vocabulary.  |
| title | At least one human-readable name. Use a Text object with a `language` tag (`de` or `en`). |
| unitInCharge | At least one reference to the `MergedOrganizationalUnit` responsible for the dataset. |

This is enough to pass schema validation, but it produces a sparse catalogue entry. A minimal record in this regard is sufficient for dataset discovery purposes, but lacks in-depth information, especially regarding the data's origin and its re-usabilty.

### Well-Described Record

A record that is genuinely useful to someone searching the catalogue to request access to the data should also include:

<STILL UNDER REVISION>

| Field | Why it matters |
| --- | --- |
| accessPlatform | Reference to a `MergedAccessPlatform` if the data is available through a service or API. This is given for open data, where the data can be accessed through open data access services, e.g. Zenodo. Access platform can also be RKI internal data services, where access is restricted. These access platforms have their `technicalAccessibility` set to `internal` and will not be published to the public MEx metadata catalogue. |
| distribution | References to one or more `MergedDistribution` records that describe the concrete files or endpoints. Without this, the catalogue entry has no actionable download or access link.  |
| hasLegalBasis | A free-text statement or a URL reference to the legal text/law that forms the basis for collecting the data. This is an important indicator for re-use options. |
| hasPurpose |  At least one Concept URI from the Purpose vocabulary. Another important indicator for re-use options. |
| provenance | A free-text statement describing the context of origin of the resource. This is mandatory in HealthDCAT-AP and therefore required for HealthDCAT-AP export. |
| rights | Free-text statement of the possible re-use options. |
| variables | This is not a property of `Resource`! (`Variable` is linked to `Resource` via `usedIn`) Nevertheless, MEx regards variables as necessary in-depth information of the dataset. Without variables, users may not have the information needed to make an informed decision for a data application request. In this regard, it is recommended to have Variables linked to their Resources via `usedIn`. |

The following optional properties can be used to enrich the metadata description and add more value for discoverability of the resource.

| Field | Use case |
| --- | --- |
| geopoliticalResolution |  A Concept URI from the Geopolitical Resolution vocabulary. |
| healthCategory | At least one Concept URI from the Health Category vocabulary. The vocabulary compiles the categories of health data as defined by EHDS Article 51. Required for HealthDCAT-AP export. |
| hasCodeValues | A list of free-text values can be given, which contain codes that derive from standardized coding systems like `ICD`, `SNOMED CT` and `LOINC`. |
| hasCodingSystem | A Concept URI from the Coding System vocabulary. If the dataset uses `ICD`, `SNOMED CT`, `LOINC`, or other standard terminologies, state them here. |
| minTypicalAge/maxTypicalAge | A numerical value indicating the minimum/maximun age of the individuals contained in the data. Especially used for population-based data. |
| numberOfRecords, numberOfUniqueIndividuals | Gives users a sense of scale before they request access. |
| populationCoverage | A free-text description of the population that is covered by the data. Especially used for population-based data. |
| spatial | A location indicating the geographical coverage of the data. |
| startDate/endDate | Dates that indicate the temporal coverage of the data. |
| wasGeneratedBy | An activity, in which the data originated, e.g. a research project. <STILL UNDER REVIEW> |

### Linking to Distributions, Activities and Responsible Units

A Resource rarely stands alone. The following links place it in context:

#### Distribution

Every concrete file format or download endpoint is a separate `Distribution`. The resource links to them via the distribution field, which holds an array of MergedDistribution identifiers. See Handling Multiple Distributions below for guidance on when to split.

#### Activity

If the dataset was produced by a research project or surveillance activity, link the two via the `Activity` entity. The activity's own fields (`responsibleUnit`, `involvedPerson`, `start`/`end`, `fundingProgram`) provide project-level context that does not belong on the resource itself. The connection is typically expressed from the resource side: a resource can reference an activity that generated it.

#### Responsible Unit

`unitInCharge` identifies the organisational unit accountable for the dataset. This is always a reference to a `MergedOrganizationalUnit`, not to a person.

### Examples

#### Minimal

```JSON
{
  "identifier": "aB1cDeFgHiJkLmNoPqRsTu",
  "hadPrimarySource": "bFQoRhcVH5DHU6naEb1wng",
  "identifierInPrimarySource": "DS-SURVEILLANCE-001",
  "stableTargetId": "xYzAbCdEfGhIjKlMnOpQrS",
  "title": [{"value": "Meldedaten Influenza", "language": "de"}],
  "contact": ["hJKL9mNoPqRsTuVwXyZ123"],
  "accessRestriction": "https://mex.rki.de/item/access-restriction-2",
  "theme": ["https://mex.rki.de/item/theme-17"],
  "unitInCharge": ["cDeFgHiJkLmN1234OpQrSt"]
}
```

#### Well-Described

```JSON
{
  "identifier": "aB1cDeFgHiJkLmNoPqRsTu",
  "hadPrimarySource": "bFQoRhcVH5DHU6naEb1wng",
  "identifierInPrimarySource": "DS-SURVEILLANCE-001",
  "stableTargetId": "xYzAbCdEfGhIjKlMnOpQrS",
  "title": [
    {"value": "Meldedaten Influenza", "language": "de"},
    {"value": "Notifiable disease data: Influenza", "language": "en"}
  ],
  "description": [
    {"value": "Wöchentliche Meldedaten zu Influenza-Fällen gemäß IfSG, aggregiert auf Kreisebene.", "language": "de"},
    {"value": "Weekly notifiable disease data on influenza cases per IfSG, aggregated at district level.", "language": "en"}
  ],
  "contact": ["hJKL9mNoPqRsTuVwXyZ123"],
  "accessRestriction": "https://mex.rki.de/item/access-restriction-2",
  "theme": ["https://mex.rki.de/item/theme-17"],
  "keyword": [
    {"value": "Influenza", "language": "de"},
    {"value": "Surveillance", "language": "en"}
  ],
  "language": ["https://mex.rki.de/item/language-1"],
  "unitInCharge": ["cDeFgHiJkLmN1234OpQrSt"],
  "publisher": ["tUvWxYzA1234AbCdEfGhIj"],
  "distribution": ["rStUvWxYzA1234AbCdEfGh"],
  "resourceTypeGeneral": "https://mex.rki.de/item/resource-type-general-1",
  "healthCategory": ["https://mex.rki.de/item/health-category-1"],
  "startDate": "2001-01-01",
  "numberOfRecords": 2500000
}
```

## Linking entities

MEx entities do not exist in isolation. A dataset has distributions, belongs to an activity, is maintained by an organisational unit, and has contact persons. Getting these cross-references right is essential for a coherent catalogue. This subsection covers the conventions.

### Golden Rule: Always refrence Merged IDs

Every cross-entity reference points to a Merged identifier (`stableTargetId`), never to an Extracted identifier. This applies regardless of whether the referencing entity is itself Extracted or Merged.
The reason is structural: multiple Extracted records from different source systems may describe the same real-world entity. They all share the same `stableTargetId`, which becomes the Merged record's identifier. By referencing the merged ID, the link survives deduplication. It does not matter which source system produced the target entity, or whether additional sources are added later.

#### Practical implication for extractor developers

When building a record for an Extracted Item, you must know the `stableTargetId` of the entity you want to reference. In most pipelines, this is resolved by looking up the target entity by its `identifierInPrimarySource` and `hadPrimarySource` combination, which deterministically maps to a `stableTargetId`.

#### How Activities provide context for Resources

The relationship between Resource and Activities is expressed by `relatedActivity`, which means any kind of relationship, e.g. the project in which the data originated or a project that used the data.

A typical pattern:

| Activity | | | Influenza Surveillance Programme 2020-2025 |
| --- | --- | --- | --- |
| | responsibleUnit | MergedOrganizationalUnit | FG 36 |
| | involvedPerson | MergedPerson | the project lead, e.g. leader of FG 36 |
| | start | | 2020-01-01 |
| | end | | 2025-12-31 |
| | funderOrCommissioner | | Horizon 2020 |
| Resource | | | Meldedaten Influenza |
| | (links to activity above) | | |
| | unitInCharge | MergedOrganizationalUnit | FG 36 |
| | contact | MergedContactPoint | team inbox |
| | distribution | MergedDistribution | CSV export |

This separation is deliberate: the activity carries project-level metadata (funding, timeline, participants) while the resource carries dataset-level metadata (format, access, content description). A single activity can produce multiple resources, and a resource can potentially relate to more than one activity.

### Linking Persons, Organisational Units, and Contact Points

MEx distinguishes three types of "who" entities. Using the right one is important:

| Entity | Represents | Use when\Idots |
| --- | --- | --- |
| Person | A named individual | You need to credit someone by name (e.g. `involvedPerson` on an `Activity`, `creator` on a `BibliographicResource`). |
| OrganizationalUnit | A team, department, or division within an organisation | You need to indicate organisational responsibility (e.g. `unitInCharge`, `responsibleUnit`). |
| ContactPoint | A reachable communication channel (typically an email address) | You need to tell a data consumer how to get in touch (e.g. `contact` on a `Resource`). |

These are not interchangeable, even though some properties accept more than one type. The key distinctions:

* `unitInCharge` and `responsibleUnit` accept only `MergedOrganizationalUnit`. They answer the question "Which team is responsible?" rather than "Who can I contact?".
* `contact` currently accepts `MergedOrganizationalUnit` and `MergedContactPoint`. The preferred target is a `ContactPoint` (a functional mailbox that survives staff changes).
* `involvedPerson` accepts only `MergedPerson`. This is for named individuals who contributed to an activity.

A common mistake is pointing contact at a person when a functional mailbox exists. Functional mailboxes are more stable and more appropriate for catalogue consumers who want to request access to a dataset.

#### Example: a fully linked Resource Set

The following shows how a minimal set of entities references each other. All identifier values shown are Merged identifiers.

| Source Entity | Source ID | Property | Target Entity | Target ID |
| --- | --- | --- | --- | --- |
| OrganizationalUnit (FG 36) | ou-fg36-001 | isPartOf | Organization (RKI) | org-rki-001 |
| Person (Dr. Example Person) | person-abc-001 | affiliation | OrganizationalUnit (FG 36) | ou-fg36-001 |
| Activity (Influenza-Surveillance) | act-influ-surv | responsibleUnit | OrganizationalUnit (FG 36) | ou-fg36-001 |
| Activity (Influenza-Surveillance) | act-influ-surv | contact | ContactPoint (example@rki.de) | cp-fg36-inbox |
| Activity (Influenza-Surveillance) | act-influ-surv | involvedPerson | Person (Dr. Example Person) | person-abc-001 |
| Resource (Meldedaten Influenza) | res-influ-001 | unitInCharge | OrganizationalUnit (FG 36) | ou-fg36-001 |
| Resource (Meldedaten Influenza) | res-influ-001 | publisher | Organization (RKI) | org-rki-001 |
| Resource (Meldedaten Influenza) | res-influ-001 | contact | ContactPoint (example@rki.de) | cp-fg36-inbox |
| Resource (Meldedaten Influenza) | res-influ-001 | distribution | Distribution (influenza.csv) | dist-csv-001 |

Reading the references:

* The resource links to a `Distribution` (what to access), a `ContactPoint` (who to contact), an `OrganizationalUnit` (who is responsible), and an `Organization` (who publishes)
* The `Activity` links to the same `ContactPoint` and `OrganizationalUnit`, plus a `Person` who is involved
* The `OrganizationalUnit` links upward to the `Organization` via `isPartOf`
* The `Person` links to the `OrganizationalUnit` via `affiliation`

No reference uses an Extracted identifier. Every link targets the Merged identifier of the target entity.

## Modelling organisational hierarchy

### Organization vs OrganizationalUnit

MEx uses two separate entity types to represent organisational structure:

| Entity | Represents | Examples |
| --- | --- | --- |
| Organization | A top-level legal entity | Robert Koch-Institut, Charité, WHO |
| OrganizationalUnit | A subdivision within an organisation | FG 36, Abteilung 3, ZIG |

The distinction matters because most MEx properties that express responsibility (`unitInCharge`, `responsibleUnit`, `involvedUnit`) reference an `OrganizationalUnit`, not an `Organization`. The `Organization` entity appears primarily as a publisher or external associate.

### Expressing Parent/Child relationships

Organisational hierarchy is modelled through the `parentUnit` property on `OrganizationalUnit`. It is a references to `MergedOrganizationalUnit` identifiers, expressing an upward link. 

An `OrganizationalUnit` is linked to its `Organization` with `unitOf`.

A typical RKI hierarchy:

| Entity | identifier | property | reference |
| --- | --- | --- | --- |
| Organization: Robert Koch-Institut | org-rki-001 | - | - |
| OrganizationalUnit: Abteilung 3 | ou-abt3-001 | unitOf | ["org-rki-001"] |
| OrganizationalUnit: FG 36 | ou-fg36-001 | parentUnit | ["ou-abt3-001"] |

Reading bottom-up: FG 36 is part of Abteilung 3, which is a unit of the Robert-Koch-Institut.
A few conventions to keep in mind:

* The top of the chain is always an `Organization`. An `OrganizationalUnit` can have one parent unit.
* Depth is not limited. The model does not impose a maximum nesting level. Whether you model two levels (institution - team) or five (institution - department - section - group - subgroup) depends on what the source system provides and what level of detail is useful for metadata consumers.

### What not to model

Not every box on an org chart needs a corresponding `OrganizationalUnit` in MEx. Create an organisational unit only if:

* it appears as `unitInCharge`, `responsibleUnit`, or `involvedUnit` on at least one resource or activity, or
* it is needed as an intermediate node to establish a correct hierarchy path.

Administrative units that never appear in metadata references (e.g. a facilities management team that does not produce or own any datasets) do not need to exist in the catalogue.

## Handling multiple distributions

A `Distribution` describes a single concrete form in which a dataset can be obtained, e.g. a downloadable file, an API endpoint, a database export. A `Resource` links to its distributions via the distribution field, which accepts an array of `MergedDistribution` identifiers.

### When to create multiple distribution records

Create a separate distribution when any of the following differ:

| Differentiator | Example |
| --- | --- |
| Multiple tables | The dataset consists of multiple tables, e.g. three csv files with a different data cross-section |
| File format | The same dataset is available as CSV and as Excel |
| Access method | One distribution is a downloadable file, another is a REST API endpoint |
| Granularity or scope | A full export and a filtered subset are offered separately |
| Update rhythm | A weekly snapshot and a daily incremental feed |
| Access restriction | A public aggregate file and a restricted record-level file (each with its own accessRestriction). |

Create a single distribution when the differences are trivial:

* The same CSV file is mirrored at two URLs: one distribution with the primary URL is sufficient.
* A file is available via HTTP and via the same endpoint over HTTPS.

Rule of thumb: If a data consumer would perceive two distinct things they could download or connect to, model them as two distributions. If they would perceive the same thing reached via a slightly different path, use one.

### Format and access URL conventions

Every distribution should populate at least accessURL, the URL at which the distribution can be reached. Beyond that:

| Field | When to use |
| --- | --- |
| accessURL | Always. The entry point for obtaining the data, whether that is a download link, a landing page, or an API base URL. |
| downloadURL | When the URL points directly to a downloadable file. If accessURL is a landing page that leads to a download, downloadURL should hold the direct file link. If they are the same, set both to the same value. |
| mediaType | Always, if known. Use a Concept URI from the MIME Type vocabulary (e.g. text/csv, application/json). |

## Multilingual text

Several MEx properties, such as title, description, keyword, and others, accept values as Text objects rather than plain strings. A Text object pairs a value with a language tag, allowing the same property to carry content in more than one language.

Structure of a text object:

```JSON
{
  "value": "Wöchentliche Meldedaten zu Influenza-Fällen",
  "language": "de"
}
```

Properties typed as Text are always arrays, so a bilingual title looks like this:

```JSON
"title": [
  {"value": "Meldedaten Influenza", "language": "de"},
  {"value": "Notifiable disease data: Influenza", "language": "en"}
]
```

Supported language codes

MEx uses two-letter ISO 639-1 codes. In practice, most commonly used values are `de` and `en` for German and English. The language field on a Text object describes the language of that specific text value, independent of the language property on a Resource, which describes the language of the data itself.

### Conventions

* Do not duplicate identical content: If a title is a proper noun, technical term, or abbreviation that reads the same in both languages (e.g. SARS-CoV-2 PCR"), a single entry without a language tag or with one language tag is sufficient. <STILL UNDER REVIEW>
* Language tag is optional but strongly recommended: The schema allows Text objects without a language field. Omitting it means "language unspecified", the value will still be stored and displayed, but language-aware search and filtering cannot use it. Always set the tag when the language is known.
* One value per language per property: Do not provide two German entries for the same property. If you need to express an alternative name, use alternativeTitle rather than a second title entry in the same language.
* Keyword language tags: Keywords are often short terms where the language boundary is blurry (e.g. "influenza" is used in both German and English). Pick the language that best reflects the term's origin. <STILL UNDER REVIEW>

## Governance & change requests

The MEx metadata model and its controlled vocabularies are maintained as Open Source JSON Schema files in the MEx-Model Github repository. Changes to the model follow a structured process to ensure that updates are deliberate, reviewed, and backward-compatible where possible.

### How to request a change

Changes fall into two categories:

| Category | Examples | Where to start |
| --- | --- | --- |
| Model changes | Adding a property, changing a cardinality, introducing a new entity type, removing a deprecated field | GitHub issue on mex-model or internal Jira ticket |
| Vocabulary changes | Adding a new concept to an existing vocabulary, aligning values with an EU code list, deprecating a concept | Same |

For vocabulary-specific governance (who can propose new values, how additions are reviewed), see the Controlled Vocabularies → Governance section above.

### What a change request should include

A useful change request, whether filed as a Github issue or a Jira ticket, should cover:

* What: the specific property, entity, or vocabulary affected.
* Why: the use case or requirement driving the change (e.g. HealthDCAT-AP compliance, extractor needs, data steward feedback).
* Impact: whether existing data would break or need migration. This is the single most important consideration for reviewers.
* Proposal: a concrete suggestion (new property name, cardinality, range, vocabulary values), not just the problem.

### Review and release process

<STILL NEEDS CONTENT>

### Who to contact

For questions about the model or to discuss a potential change before filing a formal request:

E-Mail: mex@rki.de

Github: open an issue
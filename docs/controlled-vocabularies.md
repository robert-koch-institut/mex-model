# Controlled Vocabularies

As described in the How the model works section, properties that draw from a fixed set of permissible values reference a controlled vocabulary via the useScheme keyword in the JSON Schema. The property value is always a Concept URI from that vocabulary. This section lists all vocabularies currently defined in the model, describes their alignment with EU-maintained code lists, and outlines how vocabularies are governed.

## Vocabulary list

The following vocabularies are defined as JSON files in `MEX/MODEL/VOCABULARIES`. The Used by column lists the entity types that reference each vocabulary.

| Vocabulary | File | Used by | Concepts |
| --- | --- | --- | --- |
| Access Restriction | access-restriction.json | Resource, Distribution, BibliographicResource | Access levels for datasets and distributions |
| Activity Type | activity-type.json | Activity | Classification of RKI activities, surveillance, research, etc. |
| Anonymization / Pseudonymization | anonymization-pseudonymization.json | Resource | Whether data is anonymized, pseudonymized, or neither (scheduled for removal, RKIMEX-134) |
| API Type | api-type.json | AccessPlatform | Protocol type of a service endpoint (scheduled for removal, RKIMEX-63) |
| Bibliographic Resource Type | bibliographic-resource-type.json | BibliographicResource | Publication format (article, report, etc.) |
| Consent Status | consent-status.json | Consent | GDPR consent status values |
| Consent Type | consent-type.json | Consent | Type of consent granted |
| Data Processing State | data-processing-state.json | Resource | Processing stage of the data (raw, cleaned, aggregated, etc.) (scheduled for removal, RKIMEX-135) |
| Frequency | frequency.json | Resource | Update frequency of a dataset |
| Health Category | health-category.json | Resource | Health-domain classification (added for HealthDCAT-AP alignment) |
| Language | language.json | Resource, BibliographicResource | Language of the dataset or publication |
| License | license.json | Distribution, BibliographicResource | License under which data is published |
| MIME Type | mime-type.json | Distribution | Media type of a distribution file |
| Personal Data | personal-data.json | Resource | Whether the dataset contains personal data (scheduled for removal, RKIMEX-91) |
| Resource Creation Method | resource-creation-method.json | Resource | How the dataset was generated (survey, register, model, etc.) |
| Resource Type General | resource-type-general.json | Resource | High-level dataset type classification |
| Technical Accessibility | technical-accessibility.json | AccessPlatform | Network reachability (internal, external, both) |
| Theme | theme.json | Resource, Activity | Topic classification of datasets and activities (scheduled for removal, RKIMEX-130) |

Additionally, `concept-scheme.json` serves as a registry of all vocabulary URIs (the `ConceptScheme` instances).

## EU alignment

Several MEx vocabularies correspond to code lists maintained by the EU Publications Office or by other standards bodies. Where a correspondence exists, MEx values should be mappable to the EU equivalent, though MEx may carry additional RKI-specific values that have no EU counterpart.

| MEx Vocabulary | EU/External Equivalent | Alignment Status |
| --- | --- | --- |
| Access Restriction | [EU Access Right](https://op.europa.eu/s/y9RF) | Partial — MEx uses finer-grained internal access levels; mapping flattens these |
| Frequency | [EU Frequency](https://op.europa.eu/s/y9RG) | Under review — MEx code list to be aligned (RKIMEX-43) |
| Language | [EU Languages](https://op.europa.eu/s/y9RH) | Aligned — vocabulary updated to match the EU authority table |
| License | [DCAT-AP.de Licenses](https://www.dcat-ap.de/def/licenses/) | under review |
| MIME Type | [IANA Media Types](https://www.iana.org/assignments/media-types/) | Aligned — values drawn from IANA registry |
| Resource Type General | [EU Dataset Type](https://op.europa.eu/s/y9RI) | Partial — MEx carries additional values |
| Consent Status | [DPV Consent Status](https://w3id.org/dpv#ConsentStatus) | Aligned — values modelled after the W3C Data Privacy Vocabulary |
| Health Category | HealthDCAT-AP Health Category | Added for HealthDCAT-AP alignment |
| Resource Creation Method | HealthDCAT-AP wasGeneratedBy | Aligned — vocabulary aligned to HealthDCAT-AP controlled vocabulary "Health Activities" |
| Personal Data | HealthDCAT-AP Personal Data | Partial — RKI-specific adaptations; vocabulary scheduled for removal from the model (will be mapped at export) |

Vocabularies not listed above (Activity Type, API Type, Anonymization/Pseudonymization, Bibliographic Resource Type, Consent Type, Data Processing State, Technical Accessibility) are MEx-specific with no EU equivalent.

## Governance

### Who can propose changes?

Changes can result from:

* The subject area
* User feedback
* External requirements
* Through technical assessment from a FAIR/metadata perspective (e.g. encountering a "new" standard)
* External rulings (such as EHDS)

### How are concept values added, deprecated, or retired?

* Identifiers are incremented
* When concepts are deleted, the identifier is not reassigned
* However, existing concepts can be assigned new pref- and altLabel values; the identifier remains the same
* Since MEx is not a reference vocabulary, there is no complex maintenance, and changes are tracked only via Git

### What is the relationship between vocabulary changes and schema versioning?

* A new vocabulary also requires a new property
* A new mandatory property requires a major version change
* A new optional property requires a minor version change
* A new vocabulary without a new property would also require a minor version change
* A change in an existing vocabulary would require a patch version
* A corrective adjustment (e.g. typos) would require a patch version

## Vocabulary Detail

The tables below are auto-generated from the vocabulary JSON files in the repository. Each table lists all concepts in the vocabulary with their label, identifier, and definition.
```{eval-rst}
.. mexvocabularies:: ../mex/model/vocabularies
```
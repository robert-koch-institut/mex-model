# Controlled Vocabularies

As described in the chapter [How the model works](how-the-model-works.md), properties that draw from a fixed set of permissible values reference a controlled vocabulary via the `useScheme` property in the JSON Schema. The value is always a Concept URI from that vocabulary. This section lists all vocabularies defined in the model, describes their alignment with EU-maintained code lists, and outlines how vocabularies are governed.

## Vocabulary list

The following vocabularies are defined as JSON files in `mex/model/vocabularies/`. The Used by column lists the entity types that reference each vocabulary.

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

The file `concept-schemes.json` serves as a registry of all vocabulary URIs (the `ConceptScheme` instances).

## Alignment with EU vocabularies and other standards

Several MEx vocabularies correspond to vocabularies and lists maintained by the EU Publications Office or by other standard bodies. Where a correspondence exists, MEx terms should be mappable to the standard equivalent, though MEx may carry additional RKI-specific values that have no counterpart in a standard.

| MEx Vocabulary | External Source | Alignment Status |
| --- | --- | --- |
| Access Restriction | [EU Access Right](https://publications.europa.eu/resource/authority/access-right) | Terms are matched with external source. MEx only uses terms that are relevant in the scope of RKI.  |
| Bibliographic Resource Type | [Bibliographic Ontology](http://purl.org/ontology/bibo/) and [Wikidata](http://www.wikidata.org) | All terms are matched with Bibo and/or Wikidata. MEx only uses types that are in the scope of RKI. |
| Coding System | [HealthDCAT-AP Coding Systems](https://hdeu-dcat.data.health.europa.eu/resource/authority/coding-system) and [Wikidata](http://www.wikidata.org) | All terms are derived and matched with the HealthDCAT-AP vocabulary and are additionally matched with Wikidata. |
| Consent Status | [DPV Consent Status](https://w3id.org/dpv#ConsentStatus) | All terms are derived and matched with external source. MEx only uses terms that are relevant in the scope of RKI. |
| Consent Type | [DPV Consent Type](https://w3id.org/dpv) | All terms derived are matched with external source. MEx only uses terms that are relevant in the scope of RKI. |
| Frequency | [EU Frequency](http://publications.europa.eu/resource/authority/frequency/) and [Dublin Core Collection Description Frequency Vocabulary](http://purl.org/cld/freq) | All terms are derived and matched with both external sources. MEx only includes terms which are relevant in the scope of RKI. |
| Geopolitical Resolution | [GND of German National Library](https://d-nb.info/gnd/) | Terms are matched with external source. |
| Health Category | [HealthDCAT-AP Health Category](https://hdeu-dcat.data.health.europa.eu/resource/authority/healthcategories) | All terms are derived and matched with the external source. MEx only uses terms that are relevant in the scope of RKI. |
| Health Standard | [HealthDCAT-AP Standard](https://hdeu-dcat.data.health.europa.eu/resource/authority/standard) | All terms are derived and matched with external source. |
| Language | [EU Languages](http://publications.europa.eu/resource/authority/language) | All terms are derived and matched with external source. MEx only uses terms that are relevant in the scope of RKI. |
| License | [SPDX Licenses](https://spdx.org/licenses) | All terms are derived and matched with the external source. |
| MIME Type | [IANA Media Types](https://www.iana.org/assignments/media-types/) | Most terms are matched with external source. MEx only uses terms that are relevant in the scope of RKI.|
| Resource Creation Method | [HealthDCAT-AP Health Activity](https://hdeu-dcat.data.health.europa.eu/resource/authority/health-activity) | Where applicable, terms are matched with the HealthDCAT-AP vocabulary. |

Vocabularies not listed above are MEx-specific with no alignment to external sources.

## Governance

### How the external sources are managed

Where MEx vocabularies correspond to established controlled vocabularies, MEx does not reference those external vocabularies directly. Instead, it maintains a local copy within the vocabulary/ directory of the repository, with its own Concept URIs.

This is a deliberate design decision, primarily motivated by versioning control. By maintaining its own copy, MEx can update a vocabulary on its own schedule and ensure that the version in use at any given time is explicitly known and documented. A live reference to an external vocabulary, by contrast, would mean that changes made upstream, such as additions, deprecations, or restructuring of concept hierarchies, would take effect immediately and without a corresponding entry in the MEx changelog. This would possibly break existing records silently as validation routines would fail.

However, this approach also introduces a maintenance burden. Local copies must be actively kept in sync with their upstream sources, and divergence can accumulate over time. This risk is particularly pronounced for large vocabularies, where upstream changes may be frequent and where outdated values in MEx could lead to incorrect or incomplete classifications. Crucially, this synchronization is only reliable if upstream changes are well-documented in the external vocabulary's own changelog, which cannot always be guaranteed.

Where a MEx vocabulary has an (established) equivalent, values should be mappable to that external vocabulary. The relevant mapping is maintained alongside the vocabulary definition.

### Change requests can result from

* The subject area
* User feedback
* External requirements
* Changes in the external sources used for vocabulary alignment
* Through technical assessment from a FAIR/metadata perspective (e.g. encountering a "new" standard)
* External rulings (such as EHDS)

### How are concept values added, deprecated, or retired?

* Identifiers are incremented
* When concepts are deleted, the identifier is not reassigned
* However, existing concepts can be assigned new pref- and altLabel values; the identifier remains the same
* Since MEx is not a reference vocabulary, there is no complex maintenance, and changes are tracked only via Git

## Vocabulary Detail

The tables below are auto-generated from the vocabulary JSON files in the repository. Each table lists all concepts in the vocabulary with their label, identifier, and definition.

```{eval-rst}
.. mexvocabularies:: ../mex/model/vocabularies
```

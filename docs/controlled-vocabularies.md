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
| Resource Creation Method | [HealthDCAT-AP Health Actvity](https://hdeu-dcat.data.health.europa.eu/resource/authority/health-activity) | Where applicable, terms are matched with the HealthDCAT-AP vocabulary. |

Vocabularies not listed above are MEx-specific with no alignment to external sources.

## Governance

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

## Vocabulary Detail

The tables below are auto-generated from the vocabulary JSON files in the repository. Each table lists all concepts in the vocabulary with their label, identifier, and definition.

```{eval-rst}
.. mexvocabularies:: ../mex/model/vocabularies
```

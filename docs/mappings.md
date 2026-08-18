# Mappings

## DCAT property mapping

The MEx metadata model did not grow in isolation. Its entity types, property names, and cardinality rules were designed with an established vocabulary landscape in mind, primarily W3C DCAT 2.0 for dataset and distribution metadata, and W3C PROV-O for provenance tracking. This section documents the relationship between MEx and those standards: Where does MEx adopt a concept as-is? Where does it extend one? Where does it introduce something new?

### MEx as a DCAT-inspired application profile

MEx draws on two W3C Recommendations as its conceptual foundation:
* DCAT 2.0: the Data Catalog Vocabulary, which provides the core classes Dataset, Distribution and DataService together with a rich set of metadata properties.
* PROV-O: the Provenance Ontology, from which MEx inherits the notions of Activity and hadPrimarySource.

MEx is not a strict DCAT serialisation. It does not produce RDF, it does not mint namespace URIs for its own terms, and its JSON documents are validated with JSON Schema rather than SHACL. What it does instead is use DCAT and PROV-O as a conceptual vocabulary: The entity types and properties in MEx are designed so that a mapping back to DCAT is always possible, even where MEx has renamed a property for JSON convention or added constraints that go beyond the original specification.

To make that relationship precise, every MEx entity class and every property is assigned one of three interoperability levels:

| Level | Label | Meaning |
| --- | --- | --- |
| A | Adopted | Semantically identical to the corresponding DCAT or PROV-O term or a term from another standard. The only difference is the property name (JSON camelCase instead of a prefixed RDF URI). A round-trip conversion to DCAT is lossless. |
| E | Extended | Based on a DCAT or PROV-O concept, but MEx adds constraints, narrows the range, or broadens the semantics beyond what the original standard defines. A conversion to DCAT is possible but may lose MEx-specific detail. |
| P | Profile-specific | Defined by MEx with no direct counterpart in DCAT or PROV-O. These properties serve RKI-internal requirements — data-privacy tracking, variable-level descriptions, organisational hierarchy — that fall outside the scope of a general-purpose data-catalogue vocabulary. |

These levels are recorded in the JSON Schema files themselves via exactMatch (for A and E properties that correspond to an existing RDF predicate) and closeMatch (where a MEx property specialises a broader standard property). The properties exactMatch and closeMatch derive from the standard SKOS and are commonly used for mappings between schemas (see Simple Standard for Sharing Ontological Mappings - SSSOM). The entity reference pages in this specification include the level for every property, making it straightforward to assess how much a given entity can be exported to a standards-compliant DCAT catalogue and what will require profile-specific handling.

### Renamed properties

The following table lists every MEx property that corresponds to a DCAT 2.0 or PROV-O property but uses a different name. The JSON Schema files record these correspondences via the sameAs keyword, the table below consolidates them across all entity types.

Where a property appears on more than one entity type, the entity column lists all of them. The Level column indicates whether the mapping is a straight adoption (A) or an extension with additional MEx-specific constraints (E).

| MEx Property | MEx Entity | DCAT/PROV-O Property | Level |
| --- | --- | --- | --- |
| title | Resource, Activity, AccessPlatform, BibliographicResource | dcterms:title | A |
| alternativeTitle | AccessPlatform, Resource, BibliographicResource | dcterms:alternative | A |
| description | Resource, AccessPlatform, Activity | dcterms:description | A |
| keyword | Resource | dcat:keyword | A |
| theme | Resource, Activity | dcat:theme | A |
| contact | Resource, Activity, AccessPlatform | dcat:contactPoint | A |
| language | Resource, BibliographicResource | dcterms:language | A |
| issued | Distribution, BibliographicResource | dcterms:issued | A |
| modified | Distribution | dcterms:modified | A |
| license | Distribution, BibliographicResource | dcterms:license | A |
| accessURL | Distribution | dcat:accessURL | A |
| downloadURL | Distribution | dcat:downloadURL | A |
| mediaType | Distribution | dcat:mediaType | A |
| distribution | Resource, BibliographicResource | dcat:distribution | A |
| publisher | BibliographicResource | dcterms:publisher | A |
| creator | BibliographicResource | dcterms:creator | A |
| endpointURL | AccessPlatform | dcat:endpointURL | A |
| endpointDescription | AccessPlatform | dcat:endpointDescription | A |
| landingPage | AccessPlatform | dcat:landingPage | A |
| start | Activity | prov:startedAtTime | A |
| end | Activity | prov:endedAtTime | A |
| hadPrimarySource | All Extracted entities | prov:hadPrimarySource | A |
| accessRestriction | Resource, Distribution, BibliographicResource | dcterms:accessRights | E |
| unitInCharge | Resource, Activity, AccessPlatform | prov:wasAssociatedWith | E |
| responsibleUnit | Activity | prov:wasAssociatedWith | E |

Reading the table:

* Level A rows are direct renames. The MEx property carries the same semantics, the same expected value space, and the same cardinality intent as the DCAT/PROV-O original. Converting these to RDF is a one-to-one predicate substitution.
* Level E rows have a DCAT/PROV-O starting point but diverge in practice. accessRestriction, for example, maps to dcterms:accessRights, but draws its values from a MEx-specific controlled vocabulary rather than an open string. unitInCharge resembles dcterms:publisher but always references an internal OrganizationalUnit, not an arbitrary agent.

Properties that are entirely MEx-specific (level P) are omitted here and covered in the MEx-specific extensions beyond DCAT subsection below.

### DCAT properties not used in MEx (and why)

Not every DCAT 2.0 property has a counterpart in the MEx model. Some were omitted because they address concerns outside RKI's current scope, others are handled through a different mechanism. The table below lists the most notable omissions together with the rationale.

| DCAT/PROV-O Property | DCAT Class | Reason for Omission |
| --- | --- | --- |
| dcterms:spatial | Dataset | Part of Resource |
| dcterms:temporal | Dataset | Resource with start and end |
| dcat:spatialResolutionInMeters | Dataset | geopoliticalResolution is used instead |
| dcterms:accrualPeriodicity | Dataset | Part of Resource |
| dcat:temporalResolution | Dataset | Not applicable; variable-level granularity is described through Variable entities instead. |
| dcat:version | Dataset, Distribution | Not yet implemented, planned for model v5.1. Versioning is currently handled outside the metadata model (e.g. at the repository or file-system level). |
| dcat:versionNotes | Dataset | Omitted together with dcat:version. |
| dcterms:conformsTo | Dataset, Distribution | planned for model v5 |
| dcat:qualifiedRelation | Dataset | Not modelled. Inter-dataset relationships are expressed implicitly through shared Activity or PrimarySource references. |
| dcat:servesDataset | DataService | Not modelled. The link between an AccessPlatform and the resources it exposes is captured from the resource side (accessPlatform on Resource) rather than from the service side. |
| dcat:catalog | Catalog | MEx does not model a Catalog entity; the MEx system itself acts as the catalogue. |
| dcat:record | CatalogRecord | No CatalogRecord entity exists. Record-level audit metadata (timestamps, provenance) is managed by the MEx backend, not exposed in the schema. |
| foaf:homepage | Organization | Covered by the website property on Organization and PrimarySource, which serves the same purpose under a different name. |

### MEx-specific extensions beyond DCAT

The properties below have no counterpart in DCAT 2.0 or PROV-O. They exist because the RKI metadata landscape includes concerns such as data-privacy consent, variable-level documentation, internal organisational hierarchy, and source-system traceability, that a general-purpose data-catalogue vocabulary was never designed to address.

| MEx Property | MEx Entity | Description | Why DCAT Does Not Cover This |
| --- | --- | --- | --- |
| identifierInPrimarySource | All Extracted | The identifier of the item as it appears in the source system. | DCAT assumes a single catalogue-issued identifier. MEx must track the original ID from each feeder system to support deduplication and provenance across dozens of independent sources. |
| stableTargetId | All Extracted | Reference from an Extracted item to its Merged counterpart. | DCAT has no concept of an extract-then-merge pipeline. This property is the structural glue between the two lifecycle stages. |
| technicalAccessibility | AccessPlatform | Whether the platform is reachable from inside the RKI network, externally, or both. | DCAT's DataService describes what an endpoint offers, not who can reach it on the network level. RKI needs this to distinguish intranet-only services from public APIs. |
| activityType | Activity | Classification of the activity (e.g. surveillance, research project, administrative process). | PROV-O's Activity is deliberately type-agnostic. RKI requires a controlled vocabulary to categorise its projects for reporting and discovery. |
| fundingProgram | Activity | Name of the funding programme that finances the activity. | DCAT does not model funding. Research-metadata standards like CERIF or DataCite do, but MEx addresses this with a lightweight text property rather than importing an entire funding ontology. |
| funderOrCommissioner | Activity | The organisation that funds or commissions the activity. | Same rationale as fundingProgram: outside DCAT's scope, handled here with a simple reference rather than a dedicated funding entity. |
| involvedPerson | Activity | Persons who participate in the activity beyond the responsible unit. | PROV-O offers prov:wasAssociatedWith, but MEx separates responsible unit (organisational accountability) from involved persons (individual contributors). DCAT has no equivalent distinction. |
| involvedUnit | Activity | Organisational units that participate alongside the responsible unit. | Same distinction as above, at the unit level. |
| hasConsentStatus | Consent | The GDPR consent status granted by a data subject. | DCAT does not address data-privacy consent. The Consent entity is modelled after the W3C Data Privacy Vocabulary (DPV) but formalised as a first-class MEx entity so that consent metadata travels with the dataset it governs. |
| hasDataSubject | Consent | The person who granted or withdrew consent. | Part of the same privacy-tracking requirement. DCAT's access-rights vocabulary stops at "restricted / public" and does not track individual consent records. |
| isIndicatedAtTime | Consent | Timestamp at which consent was recorded. | No DCAT property captures the moment a privacy decision was made. |
| variable | Resource | References to Variable entities that describe the columns or fields in the dataset. | Maps to CSVW in HealthDCAT-AP |
| variableGroup | Resource | References to VariableGroup entities that organise variables into logical clusters. |  Maps to CSVW Table in HealthDCAT-AP |
| label | VariableGroup | The name of a variable group. | VariableGroup itself has no DCAT equivalent, so its properties are inherently profile-specific. |
| containedBy | VariableGroup | Back-reference to the Resource the group belongs to. | Inverse navigation link within the MEx-specific variable hierarchy. |
| isPartOf | OrganizationalUnit | Reference to the parent organisation or unit. | While org:subOrganizationOf exists in the W3C Organization Ontology, MEx uses its own reference mechanism (MEx identifiers rather than RDF URIs) and sameAs / subPropertyOf annotations to record the correspondence. The property is classified E at the entity-class level but P in terms of serialisation, because a standards-compliant consumer would need MEx-specific logic to resolve the reference. |
| doi | BibliographicResource | Digital Object Identifier. | DCAT uses dcterms:identifier as a generic bucket. MEx separates DOI into its own property so that extractors and validators can enforce the DOI syntax without ambiguity. |
| isbnIssn | BibliographicResource | ISBN or ISSN of the publication. | Same rationale as doi: a typed identifier field that would be lost in DCAT's generic dcterms:identifier. |

The MEx team adds a profile-specific property only when the requirement cannot be met by adopting or contraining an existing DCAT/PROV-O term. Each addition is recorded with a Level: P annotation in the entity reference pages, making it easy to identify which parts of a MEx record will need special handling when exporting to a standards-compliant DCAT-catalogue.

## HealthDCAT-AP Mapping

### background

HealthDCAT-AP is a domain-specific extension of DCAT-AP, the European application profile of DCAT, designed for health data catalogues. It was developed in the context of the European Health Data Space (EHDS), where it serves as the metadata standard that national health data catalogues are expected to conform to. For RKI, aligning with HealthDCAT-AP is not purely a matter of best practice. It is a regulatory trajectory that affects how German public-health datasets will need to be described and published at the European level.

HealthDCAT-AP builds on DCAT-AP's foundation and adds elements specific to the health domain.

* Sensitivity classification: properties for marking datasets according to their data-protection sensitivity, beyond the generic dcterms:accessRights that DCAT provides.
* Legal basis: structured fields for recording the legal grounds under which health data may be accessed or reused (e.g. GDPR Article 6 / Article 9 bases, national legislation).
* Health terminologies: support for referencing domain-standard code systems such as ICD-10/11, SNOMED CT, ATC, LOINC, and others, so that datasets can be described in terms that clinical and epidemiological users recognise.
* Quality annotations: mechanisms for attaching data-quality indicators (completeness, timeliness, methodological documentation) to datasets and distributions.
* Access procedures: metadata describing how a researcher or institution can request access to a dataset, including the expected turnaround, required approvals, and applicable fees.

MEx's approach to HealthDCAT-AP is selective adoption. Where a HealthDCAT-AP concept adds genuine value to MEx's own users, for instance: structured legal-basis metadata or terminology references, it is incorporated into the MEx model directly through model updates. Where full adoption would require structural changes that do not benefit MEx internally (e.g. properties that duplicate information already captured differently, or EU-specific classification schemes that do not map to RKI workflows), the property is handled through an export-time mapping rather than a model change. This keeps the MEx model lean for its primary consumers while still enabling compliant HealthDCAT-AP output where required.

> Work in progress
> The HealthDCAT-AP alignment is under active development, as is HealthDCAT-AP itself. The mapping table, gap analysis, and workaround documentation in the following subsections will be populated once the model updates are stabilised. The canonical status of each property is tracked via the branches ingested into MEx.

### Mapping Table

#### Entity-Class Mapping

| HealthDCAT-AP Class | MEX Entity | Coverage | Notes |
| --- | --- | --- | --- |

#### Properties required by HealthDCAT-AP already present in MEx

The table below lists HealthDCAT-AP mandatory or recommended properties that MEx already covers, grouped by the HealthDCAT-AP property name. The status column reflects whether the alignment work is complete.

| HealthDCAT-AP Property | MEx Property | MEx Entity | Status |
| --- | --- | --- | --- |

### GAP Analysis

The tables below list HealthDCAT-AP properties and concepts that are not yet fully present in MEx. Each gap is classified into one of three resolution strategies:

* planned for implementation: the property will be added to the MEx model directly
* will be mapped: the MEx model will not change, the property will be produced at export time from existing MEx data
* out of scope: the property is not applicable to RKI's current use cases and has no implementation or mapping planned

#### High priority: HealthDCAT-AP mandatory or key recommended properties

| HealthDCAT-AP Property | Class | Gap Description | Resolution | Tickets | Status |
| --- | --- | --- | --- | --- | --- |

#### Medium priority: recommended properties and structural alignment

| HealthDCAT-AP Property | Class | Gap Description | Resolution | Tickets | Status |
| --- | --- | --- | --- | --- | --- |

#### Low priority: optional properties, clean-up and out-of-scope items

| HealthDCAT-AP Property | Class | Gap Description | Resolution | Tickets | Status |
| --- | --- | --- | --- | --- | --- |

#### Summary

The majority of gaps fall into the "planned for implementation" category, which reflect MEx's stated philosophy: adopt into the model whatever benefits MEx directly, map everything else. The "out of scope" items are predominantly clean-up to remove legacy properties that have been superseded by HealthDCAT-AP-aligned replacements.

### Implementation Notes


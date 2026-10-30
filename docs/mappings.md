# Mappings

## Foundations of the MEx model

The MEx metadata model did not grow in isolation. Its entity types, property names, and cardinality rules were designed with an established vocabulary landscape in mind, primarily W3C DCAT 2.0 for dataset and distribution metadata, W3C PROV-O for provenance tracking and SKOS for modelling vocabularies. This chapter documents the relationship between MEx and those standards and how they are expressed in the model.

### MEx as a DCAT-inspired metadata model

MEx draws on different W3C Recommendations as well as other standards as its conceptual foundation:

* **DCAT 2.0**: the Data Catalog Vocabulary, which provides the core classes Dataset, DatasetSeries, Distribution and DataService together with a rich set of metadata properties.
* **PROV-O**: the Provenance Ontology, from which MEx inherits the notions of hadPrimarySource and methods of provenance tracking.
* **SKOS**: Simple Knowledge Organization System, from which MEx uses the entity and property definitions to model vocabularies.
* Others:
  * **HealthDCAT-AP**: As part of the efforts to build the European Health Data Space (EHDS), the HealthDCAT application profile was created, which is based on DCAT-AP, the European application profile of DCAT. The EHDS has a direct impact on RKI as a health data holding organization, which is required to deliver metadata to the EU Dataset Catalogue.
  * **Organization Ontology**: MEx uses concepts for representing RKI's organizational structure.
  * **DPV**: Data Privacy Vocabulary: MEx uses concepts to track data privacy.

MEx is not a strict DCAT serialization. It does not produce RDF, it does not mint namespace URIs for its own terms, and its JSON documents are validated with JSON Schema rather than SHACL. What it does instead is use DCAT and PROV-O as a conceptual vocabulary: The entity types and properties in MEx are designed so that a mapping back to DCAT is always possible, even where MEx has renamed a property for JSON convention or added constraints that go beyond the original specification.

## Conceptual mapping

To make the conceptual relationships between MEx and the standards transparent, the mapping types can be categorized in three interoperability levels:

| Level | Label | Meaning |
| --- | --- | --- |
| A | Adopted | Conceptually identical to the corresponding DCAT or a term from another standard. The only difference is the property name (JSON camelCase instead of a prefixed RDF URI). A round-trip conversion to DCAT is lossless. |
| E | Extended | Based on a DCAT or other standard concept, but MEx adds constraints, narrows the range, or broadens the semantics beyond what the original standard defines. A conversion is possible but may lose MEx-specific detail. |
| P | Profile-specific | Defined by MEx with no direct counterpart in DCAT or another standard. These properties serve RKI-internal requirements that fall outside the scope of a general-purpose data-catalogue vocabulary. |

### Annotation properties

These levels are recorded in the JSON Schema entity models via the following annotation are defined in `mex/model/extension/definition.json`:

| Level | Annotation property | Description |
| --- | --- | --- |
| A | exactMatch | For entities/properties that correspond to an existing RDF predicate |
| E | broadMatch | The MEx entity/property is a broader/more general concept than the standard. |
| E | narrowMatch | The MEx entity/property is a narrower/more specific concept than the standard. |
| E | closeMatch | The two are similar enough to be interchangeable in some contexts, but not all. |
| E | relatedMatch | The two are associated in some way, but not interchangeable. |
| P | n/a | No annotation property is used for the MEx entity/property, because there is no matching concept available in the standard. |

The annotation properties derive from the standard SKOS and are used for mappings between ontologies (see Simple Standard for Sharing Ontological Mappings - [SSSOM](https://mapping-commons.github.io/sssom)).

Note that MEx uses the annotation properties for a **conceptual mapping** to the entities/properties of the standards mentioned. The mapping is not an attempt on doing a ontology mapping (as intended by SSSOM)! MEx uses the annotation properties as a guidance indicator for conceptual alignment with standards to create a solid basis for mappings to external sources and to make the alignment with standards transparent in the model. For metadata managers this can serve as an indicator of the level of metadata standardization of the MEx model.

### MEx-specific extensions beyond DCAT

The entities below have no counterpart in DCAT. They exist because MEx needs to address RKI-specific requirements, that go beyond the scope of a general-purpose data-catalogue vocabulary.

| MEx Entity | Usage in MEx |
| --- | --- |
| Activity | While DCAT does not define details of the Activity entity, MEx's scope also covers the detailed description of RKI's research activities and institutional public health responsibilities. |
| Bibliographic Resource | The MEx metadata catalog includes RKI's institutional bibliography, which is out of scope of DCAT. |
| Consent | With regard to data protection, MEx manages consents for the publication of metadata relating to RKI staff. |
| ContactPoint | Pragmatic modelling of a contact that is neither a Organization nor a Person but a functional email account. |
| OrganizationalUnit | Used to identify organizational units of RKI responsible for activities, datasets, primary sources, access platforms etc. |
| Variable | While HealthDCAT-AP also addresses variable-level metadata via CSVW, DCAT only describes datasets. |
| VariableGroup | While HealthDCAT-AP also addresses variable-level metadata via CSVW, DCAT only describes datasets. |

## HealthDCAT-AP Mapping

### Background

HealthDCAT-AP is a domain-specific extension of DCAT-AP, the European application profile of DCAT, designed for health data catalogues. It was developed in the context of the European Health Data Space (EHDS), where it serves as the metadata standard that national health data catalogues are expected to conform to. Therefore, MEx model should be well aligned to HealthDCAT-AP to minimize metadata creation efforts and complex transformation logics.

HealthDCAT-AP builds on DCAT-AP's foundation and adds elements specific to the health domain.

* Sensitivity classification: properties for marking datasets according to their data-protection sensitivity, beyond the generic dcterms:accessRights that DCAT provides.
* Legal basis: structured fields for recording the legal grounds under which health data may be accessed or reused (e.g. GDPR Article 6 / Article 9 bases, national legislation).
* Health terminologies: support for referencing domain-standard code systems such as ICD-10/11, SNOMED CT, ATC, LOINC, and others, so that datasets can be described in terms that clinical and epidemiological users recognise.
* Quality annotations: mechanisms for attaching data-quality indicators (completeness, timelines, methodological documentation) to datasets and distributions.
* Access procedures: metadata describing how a researcher or institution can request access to a dataset, including the expected turnaround, required approvals, and applicable fees.

MEx's approach to HealthDCAT-AP is by selective adoption of concepts. When a HealthDCAT-AP concept adds genuine value to MEx, it gets incorporated into the MEx model. These major changes were done in the scope of updating the model to v5.

HealthDCAT-AP concepts were directly adopted, when they are required in HealthDCAT-AP and cannot be served through existing metadata fields, for instance `healthdcatap:healthCategory`.

To keep the MEx model lean for its primary consumers, compliance to HealthDCAT-AP is achieved by mapping and transformation to fit the expected value types. For instance instead of adding `dcatap:applicableLegislation` to the MEx model, the expected value (the ELI of the EHDS regulation) will be added when transforming the metadata to the expected export format.

Note that The HealthDCAT-AP alignment is under active development, as is HealthDCAT-AP itself. See [HealthData@EU Central Platform](https://acceptance.data.health.europa.eu/healthdata-central-platform) for further information and timelines.

#### Entity Mapping

| HealthDCAT-AP Class | MEx Entity | Level | Usage Note |
| --- | --- | --- | --- |
| Agent | Organization, OrganizationalUnit, Person | P | Sub-classes of Agent as defined in HealthDCAT-AP are not applicable in MEx. Required properties can still be served and optional information can be enriched through transformation logics. |
| Catalogue | n/a | n/a | Used to represent separate catalogs in the EU Dataset Catalogue. Up to this point, RKI datasets will not be in scope for a separate catalog. Therefore the information is not needed. If this change in the future, the required information can be enriched via mapping and transformation logics, as default values would be applied. |
| CatalogueRecord | n/a | n/a | The required information can be enriched via mapping and transformation logics, as default values would be applied. |
| CataloguedResource | n/a | n/a | As per usage note of HealthDCAT-AP "this class Catalogued Resource is an abstract class for DCAT-AP. Therefore only subclasses should be used in a data exchange". |
| Checksum | n/a | n/a | The required information can be enriched via mapping and transformation logics. |
| DatasetService | AccessPlatform | P | MEx's notion of AccessPlatform is broader and includes also internal platforms such as databases and file systems. MEx uses the entity for internal purposes, it will not be used for a mapping to HealthDCAT-AP. |
| Dataset | Resource | E | While many of the properties were adopted by MEx, the Resource entity includes also physical material such as laboratory samples, which was also the main reason for naming the entity 'Resource' and not 'Dataset'. Nevertheless, the entities can be regarded as conceptually matching. |
| DatasetSeries | ResourceSeries | E | The naming of the entity is aligned to the naming of the 'Resource' entity in MEx, but is conceptually aligned with DatasetSeries, although MEx defines additional properties which are needed for RKI. |
| Distribution | Distribution | A | Conceptually fully aligned, MEx does not include all properties, which are defined in HealthDCAT-AP. Nevertheless, all required elements are present in MEx model. |
| Kind | n/a | n/a | MEx stores all contact information directly with the Agent entities (Organization, OrganizationalUnit, Person). |
| LicenseDocument | n/a | n/a | MEx models licenses as controlled vocabulary. |
| Location | Location | E | Conceptually the entities are fully aligned. HealthDCAT-AP usage not says, that "It can be represented using a controlled vocabulary or with geographic coordinates". MEx uses Wikidata as authority for identifying locations. All locations items are also matched to GeoNames as second authority for geographical entities. |
| Relationship | n/a | n/a | MEx can make use of the class to send additional information, which are directly represented by the MEx entity's properties but not in HealthDCAT-AP. |
| csvw:TableGroup | n/a | n/a | MEx model has no need to represent this. All variable groups belonging to one Resource item can be regarded as an instance of a TableGroup. |
| csvw:Table | VariableGroup | E | The MEx entity is broader than CSVW in the sense as a variable group could also be represented as a table but also in other formats or the grouping of the variables could follow another ordering mechanism that is not structural but thematic. |
| csvw:Column | Variable | E | MEx describes the variable in its own right - independent from a (tabular) structure. The modelling of Variable is strongly inspired by [Datapackage](https://datapackage.org), which is a schema for representing data structures (not just tables). |
| ContactPoint | ContactPoint | P | While the name of the entities are identical, MEx notion of contact point is narrower for it is used for representing a functional email account. |

### Implementation Notes

The actual mapping to HealthDCAT-AP is outside of the scope of the MEx model repository. It will be realized following the same procedure as for other mappings to external sources that are carried out by MEx.

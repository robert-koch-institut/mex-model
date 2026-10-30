# Introduction

The MEx model improves the **F**indability, **A**ccessibility, **I**nteroperability and **R**eusability of research data at the Robert Koch Institute in accordance to the **FAIR** data principles. Rather than providing access to research data directly, MEx captures metadata: structured descriptions of datasets, their origins, responsible teams, access conditions, and relationships to other resources.

## Purpose of the specification

The purpose of this document is threefold:
New team members (i.e. developer, metadata specialists, project manager) need a single place to understand what the MEx model looks like, why it is structured the way it is, and how to produce valid metadata records. [How the Model Works](how-the-model-works.md) ist the recommended starting point.

Experienced users need quick access to entity definitions, mandatory fields, vocabulary values, and mapping tables without reading prose. The sections [Entity Conventions](entity-conventions.md), [Controlled Vocabularies](controlled-vocabularies.md), and [Validation Rules](validation-rules.md) are designed for lookup rather than sequential reading.

The model exists within a broader landscape of standards such as DCAT, PROV-O, and HealthDCAT-AP, and makes deliberate choices about what to adopt, extend and leave out. The [Mappings](mappings.md) section document these choices so that anyone producing DCAT or HealthDCAT-AP mappings understands where MEx aligns and where it diverges.

## Structure of the specification

The specification is organized into the following chapters:

| Section | What it covers | Audience |
| --- | --- | --- |
| [How the Model Works](how-the-model-works.md) | The concept model, JSON Schema conventions, layout of the repository, identifier system, MEx metadata lifecycle. | Everyone. **Read this first!** |
| [Entity Conventions](entity-conventions.md) | Extracted/Merged entity variants, per-entity guidance: when to use each entity type, mandatory fields, common pitfalls, and example JSON instances. | Developers, Metadata specialists |
| [Deduplication Mechanism](deduplication-mechanism.md) | Description of the mechanism used to deduplicate items deriving from different source systems. | Developers, Metadata specialists, Project managers |
| [Controlled Vocabularies](controlled-vocabularies.md) | Complete list of vocabularies, alignment status with standards, and governance. | Metadata specialists, Project leads |
| [Validation Rules](validation-rules.md) | Schema validation, vocabulary validation, cardinality rules, cross-entity validation, and obligation levels (MUST / MAY). | Developers, Metadata specialists |
| [Mappings](mappings.md) | How standardization and alignments to external standards and sources is represented in MEx model, interoperability levels (A/E/P) and usage of annotation properties, relationship between MEx and DCAT, Mapping to HealthDCAT-AP incl. background and EHDS compliance | Standards and Metadata specialists, Project leads |
| Maintaining the Specification | How the specification is maintained. | Metadata specialists |

Chapters are designed to be read independently. Cross-references point to related material where context would help, but no chapter assumes you have read the others. [How the Model Works](how-the-model-works.md) is the exception. This section introduces concepts used throughout the model and should therefore be read first.

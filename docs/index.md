# MEx Conceptual Metadata Model – Specification

**Table of Contents**
- [MEx Conceptual Metadata Model – Specification](#mex-conceptual-metadata-model--specification)
    - [MEx - Metadata Exchange Platform](#mex---metadata-exchange-platform)
    - [Publisher of this document](#publisher-of-this-document)
  - [Abstract](#abstract)
  - [Namespaces](#namespaces)
  - [Classes and their properties](#classes-and-their-properties)
    - [Class: Base](#class-base)
    - [Properties of mex:Base](#properties-of-mexbase)
      - [identifier](#identifier)
      - [had primary source](#had-primary-source)
    - [Class: Variable](#class-variable)
    - [Properties of mex:Variable](#properties-of-mexvariable)
      - [belongs to](#belongs-to)
      - [coding system](#coding-system)
      - [data type](#data-type)
      - [used in](#used-in)
      - [value set](#value-set)
      - [variable description](#variable-description)
      - [variable label](#variable-label)
    - [Class: Variable Group](#class-variable-group)
    - [Properties of mex:VariableGroup](#properties-of-mexvariablegroup)
      - [contained by](#contained-by)
      - [variable group label](#variable-group-label)
    - [Class: Distribution](#class-distribution)
    - [Properties of dcat:Distribution](#properties-of-dcatdistribution)
      - [access service](#access-service)
      - [access restriction](#access-restriction)
      - [access URL](#access-url)
      - [author](#author)
      - [contactPerson](#contactperson)
      - [dataCurator](#datacurator)
      - [dataManager](#datamanager)
      - [distributionTitle](#distributiontitle)
      - [downloadURL](#downloadurl)
      - [issued](#issued)
      - [license](#license)
      - [media type](#media-type)
      - [modified](#modified)
      - [other contributor](#other-contributor)
      - [project leader](#project-leader)
      - [project manager](#project-manager)
      - [publisher](#publisher)
      - [researcher](#researcher)
    - [Class: Activity](#class-activity)
    - [Properties of mex:Activity](#properties-of-mexactivity)
      - [abstract](#abstract-1)
      - [activity contact](#activity-contact)
      - [activity documentation](#activity-documentation)
      - [activity publication](#activity-publication)
      - [activity short name](#activity-short-name)
      - [activity theme](#activity-theme)
      - [activity title](#activity-title)
      - [activity type](#activity-type)
      - [alternative activity title](#alternative-activity-title)
      - [end](#end)
      - [external associate](#external-associate)
      - [funder or commissioner](#funder-or-commissioner)
      - [funding program](#funding-program)
      - [involved person](#involved-person)
      - [involved unit](#involved-unit)
      - [is part of activity](#is-part-of-activity)
      - [responsible unit](#responsible-unit)
      - [start](#start)
      - [succeeds](#succeeds)
      - [website](#website)
    - [Class: ManagedResource](#class-managedresource)
    - [Properties of mex:ManagedResource](#properties-of-mexmanagedresource)
      - [alternative](#alternative)
      - [contact](#contact)
      - [description](#description)
      - [documentation](#documentation)
      - [unit in charge](#unit-in-charge)
      - [title](#title)
    - [Class: Primary Source](#class-primary-source)
    - [Properties of mex:PrimarySource](#properties-of-mexprimarysource)
      - [located at](#located-at)
      - [version](#version)
    - [Class: Access Platform](#class-access-platform)
    - [Properties of mex:AccessPlatform](#properties-of-mexaccessplatform)
      - [endpoint description](#endpoint-description)
      - [endpoint type](#endpoint-type)
      - [endpoint URL](#endpoint-url)
      - [landing page](#landing-page)
      - [technical accessibility](#technical-accessibility)
    - [Class: Resource](#class-resource)
    - [Properties of mex:Resource](#properties-of-mexresource)
      - [access platform](#access-platform)
      - [accrual periodicity](#accrual-periodicity)
      - [anonymization pseudonymization](#anonymization-pseudonymization)
      - [contributing unit](#contributing-unit)
      - [contributor](#contributor)
      - [created](#created)
      - [creator](#creator)
      - [distribution](#distribution)
      - [external identifier](#external-identifier)
      - [external partner](#external-partner)
      - [icd 10 code](#icd-10-code)
      - [instrument, tool or apparatus](#instrument-tool-or-apparatus)
      - [is part of resource](#is-part-of-resource)
      - [keyword](#keyword)
      - [language](#language)
      - [license](#license-1)
      - [loincId](#loincid)
      - [meshId](#meshid)
      - [method](#method)
      - [method description](#method-description)
      - [modified](#modified-1)
      - [publication](#publication)
      - [publisher](#publisher-1)
      - [quality information](#quality-information)
      - [related resource](#related-resource)
      - [resource type general](#resource-type-general)
      - [resource type specific](#resource-type-specific)
      - [rights](#rights)
      - [size of data basis](#size-of-data-basis)
      - [spatial](#spatial)
      - [state of data processing](#state-of-data-processing)
      - [temporal](#temporal)
      - [theme](#theme)
      - [was generated by](#was-generated-by)
    - [Class: Actor](#class-actor)
    - [Properties of mex:Actor](#properties-of-mexactor)
      - [alternative name](#alternative-name)
      - [email](#email)
      - [GND identifier](#gnd-identifier)
      - [has address](#has-address)
      - [has URL](#has-url)
      - [ISNI identifier](#isni-identifier)
      - [short name](#short-name)
      - [VIAF identifier](#viaf-identifier)
      - [wikidata identifier](#wikidata-identifier)
    - [Class: Organization](#class-organization)
    - [Properties org:Organization](#properties-orgorganization)
      - [GEPRIS identifier](#gepris-identifier)
      - [official name](#official-name)
      - [ROR identifier](#ror-identifier)
    - [Class: Organizational Unit](#class-organizational-unit)
    - [Properties org:OrganizationalUnit](#properties-orgorganizationalunit)
      - [parent unit](#parent-unit)
      - [unit name](#unit-name)
      - [unit of](#unit-of)
    - [Class: Person](#class-person)
    - [Properties foaf:Person](#properties-foafperson)
      - [affiliation](#affiliation)
      - [family name](#family-name)
      - [full name](#full-name)
      - [given name](#given-name)
      - [member of](#member-of)
      - [ORCID identifier](#orcid-identifier)


### MEx - Metadata Exchange Platform

With the Metadata Exchange (MEx) project, the [Robert Koch Institute](https://www.rki.de) (RKI) is developing a transparency platform for finding metadata about the institute's research activities and data.

Via MEx, metadata will be made findable, accessible and available for further research. The goal is to get an overview of RKI's research data, understand its context, and to know what to consider when reusing the data. The project is also one of the many iniatives to implement the German government's open data strategy.

For further details, please consult the [project page](https://www.rki.de/DE/Content/Forsch/MEx/MEx_node.html).

**Contact** \
For more information, please feel free to email us at [mex@rki.de](mailto:mex@rki.de).

### Publisher of this document
**Robert Koch-Institut** \
Nordufer 20 \
13353 Berlin \
Germany

## Abstract

The MEx metadata model is an RDF-based vocabulary used to catalog Public Health data, resources and activities of the [Robert Koch Institute (RKI)](https://www.rki.de) - the federal Public Health institute of Germany - with the goal of making them findable and accessible via a web application.
This document contains the specification of the conceptual model and can be used to facilitate interoperability with other metadata models and schemas.

The MEx metadata model enables the description of data and resources derived from the (research) activities of RKI.
In most cases, the RKI's public health data are protected by data protection laws. Instead of publishing the data itself, MEx provides descriptions about the data. The MEx metadata model is designed to provide comprehensive descriptions for RKI's public health data. MEx users can both find and assess whether the data matches their interests and needs.
To achieve this, we provide detailed information about the data in the form of variables. Variables describe how the actual data is specified and form the basis for a data-based evaluation of studies, for example.

To collect information, MEx uses a mixed approach: In addition to manually compiling, we also automatically extract information from various primary sources managed by the RKI departments.
To model this, we rely on the W3C recommendations [DCAT](https://www.w3.org/TR/vocab-dcat-2/) and [PROV-O](http://www.w3.org/TR/prov-o/).


## Namespaces

| Prefix | Namespace |
|--------|---------|
|crm | http://www.cidoc-crm.org/cidoc-crm/ |
|datacite | http://schema.datacite.org/namespace/ |
|dc | http://purl.org/dc/elements/1.1/ |
|dcat | http://www.w3.org/ns/dcat# |
|dcatde | http://dcat-ap.de/def/dcatde/ |
|dct | http://purl.org/dc/terms/ |
|dctype | http://purl.org/dc/dcmitype/ |
|foaf | http://xmlns.com/foaf/0.1/ |
|mex | https://mex.rki.de/metadata-model# |
|org | http://www.w3.org/ns/org# |
|prov | http://www.w3.org/ns/prov# |
|rdf | http://www.w3.org/1999/02/22-rdf-syntax-ns# |
|rdfs | http://www.w3.org/2000/01/rdf-schema# |
|schema | https://schema.org/ |
|skos | http://www.w3.org/2004/02/skos/core# |
|vcard | http://www.w3.org/2006/vcard/ns# |
|wd | http://www.wikidata.org/entity/ |

## Classes and their properties

### Class: Base

| RDF Class | mex:Base |
|--------|---------|
| Definition | Root class. Every other class defined in the mex-namespace is a subclass of this class. |
| Usage note | This class has no direct instances. |

### Properties of mex:Base

#### identifier

| RDF Property | `dct:identifier` |
|--------|---------|
| Definition | An unambiguous reference to the resource within a given context. Persistent identifiers should be provided as HTTP URIs ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `rdfs:Literal` |
| owl:sameAs | `datacite:Identifier` |

#### had primary source
| RDF Property | prov:hadPrimarySource |
|--------|---------|
| Definition | A primary source for a topic refers to something produced by some agent with direct experience and knowledge about the topic, at the time of the topic's study, without benefit from hindsight. Because of the directness of primary sources, they 'speak for themselves' in ways that cannot be captured through the filter of secondary sources. As such, it is important for secondary sources to reference those primary sources from which they were derived, so that their reliability can be investigated. A primary source relation is a particular case of derivation of secondary materials from their primary sources. It is recognized that the determination of primary sources can be up to interpretation, and should be done according to conventions accepted within the application's domain ([PROV-O, 2013-04-30 ](http://www.w3.org/TR/2013/REC-prov-o-20130430/)). |
| Range | [mex:PrimarySource](#class-primary-source) |

### Class: Variable

| RDF Class | mex:Variable |
|--------|---------|
| Definition | Variables are defined for the data-based evaluation of investigations (e.g. studies). A variable is characterized by its data type (e.g. integer, string, date) and value range. The variable can be either quantitative or qualitative, i.e. the value range can take numerical or categorical values. |
| rdfs:subClassOf | [mex:Base](#class-base) |

### Properties of mex:Variable

#### belongs to
| RDF Property | mex:belongsTo |
|--------|---------|
| Definition | The group, the variable is part of. |
| Range | [mex:VariableGroup](#class-variable-group) |
| owl:sameAs | `dct:isPartOf` |
| rdfs:subPropertyOf | n/a |

#### coding system
| RDF Property | mex:codingSystem |
|--------|---------|
| Definition | An established standard to which the described resource conforms ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `dct:Standard` |
| owl:sameAs | `dct:conformsTo` |
| rdfs:subPropertyOf | n/a |

#### data type
| RDF Property | mex:dataType |
|--------|---------|
| Definition | The defined data type. |
| Range | `skos:Concept` |
| owl:sameAs | n/a |
| rdfs:subPropertyOf | n/a |

#### used in
| RDF Property | mex:usedIn |
|--------|---------|
| Definition | The resource, the variable is used in. |
| Range | [mex:Resource](#class-resource) |
| owl:sameAs | `dct:isPartOf` |
| rdfs:subPropertyOf | n/a |

#### value set
| RDF Property | mex:valueSet |
|--------|---------|
| Definition | A set of predefined values. |
| Range | `rdfs:Literal` |
| owl:sameAs | n/a |
| rdfs:subPropertyOf | n/a |

#### variable description
| RDF Property | mex:variableDescription |
|--------|---------|
| Definition | A description of the variable. How the variable is defined. |
| Range | `rdfs:Literal` |
| owl:sameAs | `dct:description` |
| rdfs:subPropertyOf | n/a |

#### variable label
| RDF Property | mex:variableLabel |
|--------|---------|
| Definition | A name for the variable. |
| Range | `rdfs:Literal` |
| owl:sameAs | `dct:title`, `rdfs:label` |
| rdfs:subPropertyOf | n/a |

### Class: Variable Group

| RDF Class | mex:VariableGroup |
|--------|---------|
| Definition | The grouping of variables according to a certain aspect, e.g. how the information is modelled in the primary source. |
| rdfs:subClassOf | [mex:Base](#class-base) |

### Properties of mex:VariableGroup

#### contained by
| RDF Property | mex:containedBy |
|--------|---------|
| Definition | The resource, the variable group is contained by. |
| Range | [mex:Resource](#class-resource) |
| owl:sameAs | `dct:isPartOf` |
| rdfs:subPropertyOf | n/a |

#### variable group label
| RDF Property | mex:variableGroupLabel |
|--------|---------|
| Definition | The name of the variable group. |
| Range | `rdfs:Literal` |
| owl:sameAs | `dct:title`, `rdfs:label` |
| rdfs:subPropertyOf | n/a |

### Class: Distribution

| RDF Class | `dcat:Distribution` |
|--------|---------|
| Definition | A specific representation of a dataset. A dataset might be available in multiple serializations that may differ in various ways, including natural language, media-type or format, schematic organization, temporal and spatial resolution, level of detail or profiles (which might specify any or all of the above) ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |
| rdfs:subClassOf | [mex:Base](#class-base) |

### Properties of dcat:Distribution

#### access service
| RDF Property | `dcat:accessService` |
|--------|---------|
| Definition | A data service that gives access to the distribution of the dataset ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |
| Range | [mex:AccessPlatform](#class-access-platform) |

#### access restriction
| RDF Property | mex:accessRestriction |
|--------|---------|
| Definition | Indicates how access to the distribution is restricted. |
| Range | `skos:Concept` |
| owl:sameAs | `dct:accessRights` |

#### access URL
| RDF Property | `dcat:accessURL` |
|--------|---------|
| Definition | A URL of the resource that gives access to a distribution of the dataset. E.g. landing page, feed, SPARQL endpoint ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |
| Range | `rdfs:Resource` |
| Usage note | Can only be used if the distribution is available via an according service (`mex:AccessPlatform`). If the distribution is stored on an RKI internal network drive, use property `dcat:downloadURL`. |

#### author
| RDF Property | mex:author |
|--------|---------|
| Definition | The author of the distribution. |
| Range | [mex:Actor](#class-actor) |
| owl:sameAs | `dct:creator` |

#### contactPerson
| RDF Property | mex:contactPerson |
|--------|---------|
| Definition | The person serving as a contact for the distribution. |
| Range | `foaf:Person` |
| owl:sameAs | `dcat:contactPoint` |

#### dataCurator
| RDF Property | mex:dataCurator |
|--------|---------|
| Definition | The person responsible for data curation in the activity that eventually led to the creation of this distribution. |
| Range | `foaf:Person` |
| rdfs:subPropertyOf | `dct:contributor` |

#### dataManager
| RDF Property | mex:dataManager |
|--------|---------|
| Definition | The person responsible for managing the data in the activity that eventually led to the creation of this distribution. |
| Range | `foaf:Person` |
| rdfs:subPropertyOf | `dct:contributor` |

#### distributionTitle
| RDF Property | mex:distributionTitle |
|--------|---------|
| Definition | The name of the distribution. |
| Range | `rdfs:Literal` |
| owl:sameAs | `dct:title`, `rdfs:label` |

#### downloadURL
| RDF Property | `dcat:downloadURL` |
|--------|---------|
| Definition | The URL of the downloadable file in a given format. E.g. CSV file or RDF file. The format is indicated by the distribution's `dcat:mediaType` ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |
| Range | `rdfs:Resource` |
| Usage note | Should be used, if the distribution is stored on an internal RKI network drive. |


#### issued
| RDF Property | `dct:issued` |
|--------|---------|
| Definition | Date of formal issuance of the resource ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `rdfs:Literal` |
| Usage note | Recommended practice is to describe the date, date/time, or period of time as recommended for `dct:date`, of which this is a sub-property. |

#### license
| RDF Property | `dct:license` |
|--------|---------|
| Definition | A legal document giving official permission to do something with the resource ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `dct:LicenseDocument` |
| Usage note | Information about licenses and rights SHOULD be provided on the level of `dcat:Distribution`. Information about licenses and rights MAY be provided for a `dcat:Dataset` [in the scope of this model: `mex:Resource`] in addition to but not instead of the information provided for the distributions of that dataset ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |

#### media type
| RDF Property | `dcat:mediaType` |
|--------|---------|
| Definition | The media type of the distribution as defined by [IANA media types](https://www.iana.org/assignments/media-types/) ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |
| Range | `skos:Concept` |

#### modified
| RDF Property | `dct:modified` |
|--------|---------|
| Definition | Date on which the resource was changed  ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `rdfs:Literal` |
| Usage note | Recommended practice is to describe the date, date/time, or period of time as recommended for `dct:date`, of which this is a sub-property. |

#### other contributor
| RDF Property | mex:otherContributor |
|--------|---------|
| Definition | Other contributors involved in the activity that eventually led to the creation of this distribution. |
| Range | [mex:Actor](#class-actor) |
| owl:sameAs | `dct:contributor` |

#### project leader
| RDF Property | mex:projectLeader |
|--------|---------|
| Definition | The head of the activity that eventually led to the creation of this distribution. |
| Range | `foaf:Person` |
| rdfs:subPropertyOf | `dct:contributor` |

#### project manager
| RDF Property | mex:projectManager |
|--------|---------|
| Definition | The manager of the activity that eventually led to the creation of this distribution. |
| Range | `foaf:Person` |
| rdfs:subPropertyOf | `dct:contributor` |

#### publisher
| RDF Property | `dct:publisher` |
|--------|---------|
| Definition | An entity responsible for making the resource available ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | [mex:Actor](#class-actor) |
| owl:sameAs | `datacite:Publisher` |
| Usage note | Default value should be the `org:Organization`-item that represents the Robert Koch Institute. |

#### researcher
| RDF Property | mex:researcher |
|--------|---------|
| Definition | Researcher involved in the activity that led eventually to the creation of this distribution. |
| Range | `foaf:Person` |
| rdfs:subPropertyOf | `dct:contributor` |

### Class: Activity

| RDF Class | mex:Activity |
|--------|---------|
| Definition | An activity carried out by RKI. This may be a research activity, such as a funded project, or a task that RKI performs under federal law.  Activities provide useful context information for resources. |
| owl:sameAs | `prov:Activity`, `crm:E7_Activity` |
| rdfs:subClassOf | [mex:Base](#class-base) |

### Properties of mex:Activity

#### abstract
| RDF Property | mex:abstract |
|--------|---------|
| Definition | A short abstract describing the activity. |
| Range | `rdfs:Literal` |
| owl:sameAs | `dct:description` |

#### activity contact
| RDF Property | mex:activityContact |
|--------|---------|
| Definition | An agent serving as a contact for the activity. |
| Range | [mex:Actor](#class-actor) |
| owl:sameAs | `dcat:contactPoint` |

#### activity documentation
| RDF Property | mex:activityDocumentation |
|--------|---------|
| Definition | A documentation of the activity. |
| Range | `foaf:Document` |
| rdfs:subPropertyOf | `dct:isReferencedBy` |

#### activity publication
| RDF Property | mex:activityPublication |
|--------|---------|
| Definition | A publication related to the activity. |
| Range | `foaf:Document` |
| rdfs:subPropertyOf | `dct:isReferencedBy` |

#### activity short name
| RDF Property | mex:activityShortName |
|--------|---------|
| Definition | A short name for or an abbreviated title of the activity. |
| Range | `rdfs:Literal` |
| owl:sameAs | `wd:P1813` |

#### activity theme
| RDF Property | mex:activityTheme |
|--------|---------|
| Definition | The main theme or subject of the activity. |
| Range | `skos:Concept` |
| rdfs:subPropertyOf | `dcat:theme` |

#### activity title
| RDF Property | mex:activityTitle |
|--------|---------|
| Definition | The official title of the activity. |
| Range | `rdfs:Literal` |
| owl:sameAs | `dct:title` |

#### activity type
| RDF Property | mex:activityType |
|--------|---------|
| Definition | The type of activity. |
| Range | `skos:Concept` |
| rdfs:subPropertyOf | `dct:type` |

#### alternative activity title
| RDF Property | mex:alternativeActivityTitle |
|--------|---------|
| Definition | Another name for the activity. |
| Range | `rdfs:Literal` |
| owl:sameAs | `dct:alternative` |

#### end
| RDF Property | mex:end |
|--------|---------|
| Definition | (Planned) end of the activity. |
| Range | `rdfs:Literal` |
| owl:sameAs | `wd:P582` |
| Usage note | Recommended practice is to describe the date or date/time, or period of time as recommended for `dct:date`. |

#### external associate
| RDF Property | mex:externalAssociate |
|--------|---------|
| Definition | An external institution or person, that is associated with the activity. |
| Range | [mex:Actor](#class-actor) |
| rdfs:subPropertyOf | `dct:contributor` |

#### funder or commissioner
| RDF Property | mex:funderOrCommissioner |
|--------|---------|
| Definition | An agent, that has either funded or commissioned the activity. |
| Range | [mex:Actor](#class-actor) |
| owl:sameAs | `wd:P8324` |

#### funding program
| RDF Property | mex:fundingProgram |
|--------|---------|
| Definition | The program in which the activity is funded, e.g. "Horizon2020". |
| Range | `rdfs:Literal` |

#### involved person
| RDF Property | mex:involvedPerson |
|--------|---------|
| Definition | A person involved in the activity. |
| Range | `foaf:Person` |
| rdfs:subPropertyOf | `dct:contributor` |

#### involved unit
| RDF Property | mex:involvedUnit |
|--------|---------|
| Definition | An organizational unit that is involved in the activity. |
| Range | `org:OrganizationalUnit` |
| rdfs:subPropertyOf | `dct:contributor` |

#### is part of activity
| RDF Property | mex:isPartOfActivity |
|--------|---------|
| Definition | Another activity, this activity is part of. |
| Range | [mex:Activity](#class-activity) |
| owl:sameAs | `dct:isPartOf`, `crm:P9i_forms_part_of` |


#### responsible unit
| RDF Property | mex:responsibleUnit |
|--------|---------|
| Definition | A unit, that is responsible for the activity. |
| Range | `org:OrganizationalUnit` |
| owl:sameAs | `dcatde:maintainer` |

#### start
| RDF Property | mex:start |
|--------|---------|
| Definition | The start of the activity. |
| Range | `rdfs:Literal` |
| owl:sameAs | `wd:P580` |
| Usage note | Recommended practice is to describe the date or date/time, or period of time as recommended for `dct:date`. |

#### succeeds
| RDF Property | mex:succeeds |
|--------|---------|
| Definition | Another activity, that ended with the start of the described activity. A follow-up activity. |
| Range | [mex:Activity](#class-activity) |
| owl:sameAs | `crm:P173_start_before_or_with_the_end_of` |

#### website
| RDF Property | mex:website |
|--------|---------|
| Definition | A web presentation of the activity, e.g. on the RKI homepage. |
| Range | `foaf:Document` |
| owl:sameAs | `wd:P856` |

### Class: ManagedResource

| RDF Class | mex:ManagedResource |
|--------|---------|
| Definition | A resource, that is managed, curated and/or maintained by RKI. |
| Usage note | This class has no direct instances. |
| rdfs:subClassOf | [mex:Base](#class-base) |

### Properties of mex:ManagedResource

#### alternative
| RDF Property | `dct:alternative` |
|--------|---------|
| Definition | An alternative name for the resource ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `rdfs:Literal` |


#### contact
| RDF Property | mex:contact |
|--------|---------|
| Definition | An agent that serves as a contact for the resource. |
| Range | [mex:Actor](#class-actor) |
| owl:sameAs | `dcat:contactPoint` |

#### description
| RDF Property | `dct:description` |
|--------|---------|
| Definition | An account of the resource ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `rdfs:Literal` |

#### documentation
| RDF Property | mex:documentation |
|--------|---------|
| Definition | A documentation of the resource. |
| Range | `foaf:Document` |
| rdfs:subPropertyOf | `dct:isReferencedBy` |

#### unit in charge
| RDF Property | mex:unitInCharge |
|--------|---------|
| Definition | This property refers to agents who assume responsibility and accountability for the resource and its appropriate maintenance ([DCAT-AP.de, 2022-02-28](http://dcat-ap.de/def/dcatde/2.0/spec/)) |
| Range | `org:OrganizationalUnit` |
| owl:sameAs | `dcatde:maintainer` |

#### title
| RDF Property | `dct:title` |
|--------|---------|
| Definition | A name given to the resource ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `rdfs:Literal` |

### Class: Primary Source

| RDF Class | mex:PrimarySource |
|--------|---------|
| Definition | An collection of information, that is managed and curated by an RKI unit ans lists activities and/or resources. |
| owl:sameAs | `dcat:Catalog`, `prov:PrimarySource` |
| Usage note | This class is needed of the internal data management of MEx-RKI team and will not be used for the MEx web app. |
| rdfs:subClassOf | [mex:ManagedResource](#class-managedresource) |

### Properties of mex:PrimarySource

#### located at
| RDF Property | mex:locatedAt |
|--------|---------|
| Definition | A URL that leads to the primary source or a filepath, where the primary source is stored. |
| Range | `rdfs:Literal` |

#### version
| RDF Property | mex:version |
|--------|---------|
| Definition | The version of the primary source, e.g. the date of the last modification. |
| Range | `rdfs:Literal` |

### Class: Access Platform

| RDF Class | mex:AccessPlatform |
|--------|---------|
| Definition | A technical system or service that provides access to distributions or resources. |
| owl:sameAs | `dcat:DataService` |
| rdfs:subClassOf | [mex:ManagedResource](#class-managedresource) |

### Properties of mex:AccessPlatform

#### endpoint description
| RDF Property | `dcat:endpointDescription` |
|--------|---------|
| Definition | A description of the services available via the end-points, including their operations, parameters etc. ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |
| Range | `rdfs:Resource` |

#### endpoint type
| RDF Property | mex:endpointType |
|--------|---------|
| Definition | The type of endpoint, e.g. REST. |
| Range | `skos:Concept` |
| rdfs:subPropertyOf | `dct:type` |

#### endpoint URL
| RDF Property | `dcat:endpointURL` |
|--------|---------|
| Definition | The root location or primary endpoint of the service (a Web-resolvable IRI) ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |
| Range | `rdfs:Resource` |


#### landing page
| RDF Property | `dcat:landingPage` |
|--------|---------|
| Definition | A Web page that can be navigated to in a Web browser to gain access to the catalog, a dataset, its distributions and/or additional information ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |
| Range | `foaf:Document` |

#### technical accessibility
| RDF Property | mex:technicalAccessibility |
|--------|---------|
| Definition | Indicates form if the platform can be accessed only within RKI network (internally) or if the platform is accessible publicly (externally). |
| Range | `skos:Concept` |

### Class: Resource

| RDF Class | mex:Resource |
|--------|---------|
| Definition | A defined piece of information or a collection of information on Public Health, that has been generated in an activity at RKI or to comply with a (federal) law or regulation that applies to RKI. |
| owl:sameAs | `dcat:Dataset`, `datacite:Resource` |
| rdfs:subClassOf | [mex:ManagedResource](#class-managedresource) |

### Properties of mex:Resource

#### access platform
| RDF Property | mex:accessPlatform |
|--------|---------|
| Definition | A platform from which the resource can be accessed. |
| Range | [mex:AccessPlatform](#class-access-platform) |

#### access restriction
| RDF Property | mex:accessRestriction |
|--------|---------|
| Definition | Indicates how access to the resource is restricted. |
| Range | `skos:Concept` |
| owl:sameAs | `dct:accessRights` |

#### accrual periodicity
| RDF Property | `dct:accrualPeriodicity` |
|--------|---------|
| Definition | The frequency with which items are added to a collection ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `dct:Frequency` |
| owl:sameAs | `datacite:Accrualperiodicity` |

#### anonymization pseudonymization
| RDF Property | mex:anonymizationPseudonymization |
|--------|---------|
| Definition | Indicates whether the data has been anonymized and/or pseudonymized. |
| Range | `skos:Concept` |
| rdfs:subPropertyOf | `dct:type` |

#### contributing unit
| RDF Property | mex:contributingUnit |
|--------|---------|
| Definition | An organizational unit of RKI, that is contributing to the resource. |
| Range | [org:OrganizationalUnit](#class-organizational-unit) |
| rdfs:subPropertyOf | `dct:contributor` |

#### contributor
| RDF Property | mex:contributor |
|--------|---------|
| Definition | A person involved in the creation of the resource. |
| Range | [foaf:Person](#class-person) |
| owl:sameAs | `datacite:Contributor` |
| rdfs:subPropertyOf | `dct:contributor` |

#### created
| RDF Property | `dct:created` |
|--------|---------|
| Definition | Date of creation of the resource ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `rdfs:Literal` |

#### creator
| RDF Property | `dct:creator` |
|--------|---------|
| Definition | An entity responsible for making the resource ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | [foaf:Person](#class-person) |
| owl:sameAs | `datacite:Creator` |

#### distribution
| RDF Property | `dcat:distribution` |
|--------|---------|
| Definition | An available distribution of the resource ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |
| Range | [dcat:Distribution](#class-distribution) |

#### external identifier
| RDF Property | mex:externalIdentifier |
|--------|---------|
| Definition | An identifier from an external source (that is not MEx), e.g. a DOI assigned by some authority. |
| Range | `rdfs:Resource` |
| rdfs:subPropertyOf | `dc:identifier` |

#### external partner
| RDF Property | mex:externalPartner |
|--------|---------|
| Definition | An external organization that is somehow involved in the creation of the resource. |
| Range | [org:Organization](#class-organization) |
| rdfs:subPropertyOf | `dct:contributor` |

#### icd 10 code
| RDF Property | mex:icd10Code |
|--------|---------|
| Definition | A concept from ICD-10. |
| Range | `rdfs:Resource` |

#### instrument, tool or apparatus
| RDF Property | mex:instrumentToolOrApparatus |
|--------|---------|
| Definition | Instrument, tool, or apparatus used in the research, analysis, observation, or processing of the object that is the subject of this resource. |
| Range | `rdfs:Literal` |

#### is part of resource
| RDF Property | mex:isPartOfResource |
|--------|---------|
| Definition | A related resource, in which the described resource is physically or logically included  ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | [mex:Resource](#class-resource) |
| owl:sameAs | `dct:isPartOf`, `datacite:IsPartOf` |

#### keyword
| RDF Property | `dcat:keyword` |
|--------|---------|
| Definition | A keyword or tag describing the resource ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |
| Range | `rdfs:Literal` |

#### language
| RDF Property | `dct:language` |
|--------|---------|
| Definition | A language of the resource ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `dct:LinguisticSystem` |
| owl:sameAs | `datacite:Language` |

#### license
| RDF Property | `dct:license` |
|--------|---------|
| Definition | A legal document giving official permission to do something with the resource ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `dct:LicenseDocument` |
| Usage note | Information about licenses SHOULD be provided on the level of `dcat:Distribution`. Information about licenses MAY be provided for a `mex:Resource` in addition, but not instead, of the information provided for the distributions of that resource ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |

#### loincId
| RDF Property | mex:loincId |
|--------|---------|
| Definition | A concept from LOINC. |
| Range | `rdfs:Resource` |

#### meshId
| RDF Property | mex:meshId |
|--------|---------|
| Definition | A concept from MeSH. |
| Range | `rdfs:Resource` |

#### method
| RDF Property | mex:method |
|--------|---------|
| Definition | Method used in the research, analysis, observation or processing of the object that is subject to the resource. |
| Range | `rdfs:literal` |

#### method description
| RDF Property | mex:methodDescription |
|--------|---------|
| Definition | The description of the method, that was used to research, analysis, observation or processing of the object that was subject to the resource. |
| Range | `rdfs:Literal` |

#### modified
| RDF Property | `dct:modified` |
|--------|---------|
| Definition | Date on which the resource was changed  ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `rdfs:Literal` |

#### publication
| RDF Property | mex:publication |
|--------|---------|
| Definition | A publication that deals with the research, analysis, observation or processing of the object that was subject to the resource, e.g. a research paper. |
| Range | `foaf:Document` |
| rdfs:subPropertyOf | `dct:isReferencedBy` |

#### publisher
| RDF Property | `dct:publisher` |
|--------|---------|
| Definition | The entity responsible for making the item available ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | [mex:Actor](#class-actor) |

#### quality information
| RDF Property | mex:qualityInformation |
|--------|---------|
| Definition | Some information about the quality of the resource. |
| Range | `rdfs:Literal` |

#### related resource
| RDF Property | mex:relatedResource |
|--------|---------|
| Definition | Unspecified relation to another resource. |
| Range | [mex:Resource](#class-resource) |
| owl:sameAs | `dct:relation`, `datacite:Relation` |

#### resource type general
| RDF Property | mex:resourceTypeGeneral |
|--------|---------|
| Definition | General type of the resource. |
| Range | `skos:Concept` |
| owl:sameAs | `datacite:ResourceTypeGeneral` |
| rdfs:subPropertyOf | `dct:type` |

#### resource type specific
| RDF Property | mex:resourceTypeSpecific |
|--------|---------|
| Definition | A term describing the specific nature of the resource. A more precise term than given by `mex:resourceTypeGeneral`. |
| Range | `rdfs:Literal` |
| owl:sameAs | `datacite:ResourceType` |
| rdfs:subPropertyOf | `dct:type` |

#### rights
| RDF Property | `dct:rights` |
|--------|---------|
| Definition | information about rights held in and over the resource ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `dct:rightsStatement` |
| owl:sameAs | `datacite:Rights` |
| Usage note | Use `dct:rights` PREFERABLY over `dct:license` in the context of `mex:Resource`. Either `dct:license`or `dct:rights` MUST be provided. Typically, resources have a license only if a reuse of the resource is intended or foreseeable, e.g., if the resource is published. If the resource has a `dcat:Distribution`, a license SHOULD be granted for this distribution. Whether or not the resource is published, a rights statement can and SHOULD be given. The statement should include information about the rights that apply to the resource, for example, if it contains personal data or data covered by a data protection law. |

#### size of data basis
| RDF Property | mex:sizeOfDataBasis |
|--------|---------|
| Definition | The size of the underlying data basis, e.g. for studies: the size of the sample. |
| Range | `rdfs:Literal` |

#### spatial
| RDF Property | `dct:spatial` |
|--------|---------|
| Definition | Spatial coverage of the resource ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `dct:Location` |
| owl:sameAs | `datacite:GeoLocation` |

#### state of data processing
| RDF Property | mex:stateOfDataProcessing |
|--------|---------|
| Definition | The processing state of the data, e.g. raw or aggregated. |
| Range | `skos:Concept` |
| rdfs:subPropertyOf | `dct:type` |

#### temporal
| RDF Property | `dct:temporal` |
|--------|---------|
| Definition | Temporal coverage of the resource ([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/)). |
| Range | `dct:PeriodOfTime` |

#### theme
| RDF Property | `dcat:theme` |
|--------|---------|
| Definition | A main category of the resource. A resource can have multiple themes ([DCAT, 2020-02-04](https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/)). |
| Range | `skos:Concept` |
| owl:sameAs | `datacite:Subject` |

#### was generated by
| RDF Property | `prov:wasGeneratedBy` |
|--------|---------|
| Definition | Generation is the completion of production of a new entity by an activity. This entity did not exist before generation and becomes available for usage after this generation ([PROV-O, 2013-04-30](http://www.w3.org/TR/2013/REC-prov-o-20130430/)). |
| Range | [mex:Activity](#class-activity) |

### Class: Actor

| RDF Class | mex:Actor |
|--------|---------|
| Definition | This class comprises people, either individually or in groups, who have the potential to perform intentional actions of kinds for which someone may be held responsible ([CIDOC CRM, version 7.1.1](https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html)). |
| owl:sameAs | `foaf:Agent`, `dct:Agent`, `crm:E39_Actor` |
| Usage note | This class has no direct instances |
| rdfs:subClassOf | [mex:Base](#class-base) |

### Properties of mex:Actor

#### alternative name
| RDF Property | mex:alternativeName |
|--------|---------|
| Definition | An alternative name for the actor. |
| Range | `rdfs:Literal` |
| owl:sameAs | `dct:alternative` |

#### email
| RDF Property | `schema:email` |
|--------|---------|
| Definition | The email address through which the actor can be contacted. |
| Range | `rdfs:Literal` |
| owl:sameAs | `vcard:hasEmail` |

#### GND identifier
| RDF Property | mex:gndId |
|--------|---------|
| Definition | Identifier from the GND (Gemeinsame Normdatei) authority file of the German National Library (DNB). |
| Range | `rdfs:Resource` |
| owl:sameAs | `wd:P227` |

#### has address
| RDF Property | vcard:hasAddress |
|--------|---------|
| Definition | A postal address. |
| Range | `vcard:Address` |
| owl:sameAs | `schema:address` |

#### has URL
| RDF Property | `vcard:hasURL` |
|--------|---------|
| Definition | A URL serving as the official web presentation of an actor. |
| Range | `foaf:Document` |
| owl:sameAs | `wd:P856`, `foaf:homepage` |

#### ISNI identifier
| RDF Property | mex:isniId |
|--------|---------|
| Definition | The ISNI (International Standard Name Identifier) of an actor. |
| Range | `rdfs:Resource` |
| owl:sameAs | `wd:P213` |

#### short name
| RDF Property | mex:shortName |
|--------|---------|
| Definition | A short name or abbreviation of the actor. |
| Range | `rdfs:Literal` |
| owl:sameAs | `wd:P1813` |

#### VIAF identifier
| RDF Property | mex:viafId |
|--------|---------|
| Definition | Identifier from VIAF (Virtual Authority File). |
| Range | `rdfs:Resource` |
| owl:sameAs | `wd:P214` |

#### wikidata identifier
| RDF Property | mex:wikidataId |
|--------|---------|
| Definition | Identifier from Wikidata. |
| Range | `rdfs:Resource` |

### Class: Organization

| RDF Class | org:Organization |
|--------|---------|
| Definition | Represents a collection of people organized together into a community or other social, commercial or political structure. The group has some common purpose or reason for existence which goes beyond the set of people belonging to it and can act as an Agent. Organizations are often decomposable into hierarchical structures ([The Organization Ontology, 2014-01-16](http://www.w3.org/TR/2014/REC-vocab-org-20140116/)). |
| owl:sameAs | `foaf:Organization`, `vcard:Organization`, `wd:Q43229` |
| rdfs:subClassOf | [mex:Actor](#class-actor) |

### Properties org:Organization

#### GEPRIS identifier
| RDF Property | mex:geprisId |
|--------|---------|
| Definition | Identifier from GEPRIS authority file. |
| Range | `rdfs:Resource` |
| owl:sameAs | `wd:P4871` |

#### official name
| RDF Property | mex:officialName |
|--------|---------|
| Definition | The official name of the organization. |
| Range | `rdfs:Literal` |
| owl:sameAs | `wd:P1448` |

#### ROR identifier
| RDF Property | mex:rorId |
|--------|---------|
| Definition | An identifier of the Research Organization Registry (ROR). |
| Range | `rdfs:Resource` |
| owl:sameAs | `wd:6782` |

### Class: Organizational Unit

| RDF Class | org:OrganizationalUnit |
|--------|---------|
| Definition | An Organization such as a department or support unit which is part of some larger Organization and only has full recognition within the context of that Organization. In particular the unit would not be regarded as a legal entity in its own right ([The Organization Ontology, 2014-01-16](http://www.w3.org/TR/2014/REC-vocab-org-20140116/)). |
| owl:sameAs | `vcard:Group`, `crm:E_74_Group` |
| rdfs:subClassOf | [mex:Actor](#class-actor) |

### Properties org:OrganizationalUnit

#### parent unit
| RDF Property | mex:parentUnit |
|--------|---------|
| Definition | The described unit is a subunit of another organizational unit. |
| Range | [org:OrganizationalUnit](#class-organizational-unit) |

#### unit name
| RDF Property | mex:unitName |
|--------|---------|
| Definition | The full name of the unit. |
| Range | `rdfs:Literal` |
| owl:sameAs | `foaf:name` |

#### unit of
| RDF Property | `org:unitOf` |
|--------|---------|
| Definition | Indicates an Organization of which this Unit is a part, e.g. a Department within a larger Organization  ([The Organization Ontology, 2014-01-16](http://www.w3.org/TR/2014/REC-vocab-org-20140116/)). |
| Range | [org:Organization](#class-organization) |

### Class: Person

| RDF Class | `foaf:Person` |
|--------|---------|
| Definition | A person ([FOAF, 2004-05-01](http://xmlns.com/foaf/0.1/)). This class comprises real persons who live or are assumed to have lived ([CIDOC CRM, version 7.1.1](https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html)). |
| owl:sameAs | `crm:E21_Person`, `vcard:Individual`, `wd:Q5` |
| Usage note | n/a |

### Properties foaf:Person

#### affiliation
| RDF Property | `schema:affiliation` |
|--------|---------|
| Definition | An organization that the described person is affiliated with. |
| Range | [org:Organization](#class-organization) |
| owl:sameAs | `wd:P1416` |

#### family name
| RDF Property | `schema:familyName` |
|--------|---------|
| Definition | The name inherited from the family. |
| Range | `rdfs:Literal` |
| owl:sameAs | `vcard:hasFamilyName` |

#### full name
| RDF Property | mex:fullName |
|--------|---------|
| Definition | The full name of a person. also used if the naming schema (given name and family name) does not apply to the name. |
| Range | `rdfs:Literal` |
| rdfs:subPropertyOf | `foaf:name` |

#### given name
| RDF Property | `schema:givenName` |
|--------|---------|
| Definition | The name given to the person e.g. by their parents. |
| Range | `rdfs:Literal` |
| owl:sameAs | `vcard:hasGivenName` |

#### member of
| RDF Property | mex:memberOf |
|--------|---------|
| Definition | Organizational unit at RKI the person is associated with. |
| Range | [org:OrganizationalUnit](#class-organizational-unit) |
| owl:sameAs | `crm:P107i_is_current_or_former_member_of` |

#### ORCID identifier
| RDF Property | mex:orcidId |
|--------|---------|
| Definition | Identifier of a person from the ORCID authority file. |
| Range | `rdfs:Resource` |
| owl:sameAs | `wd:P496` |

MEx Metadata Schema
===================

The MEx metadata schema is used to catalog Public Health data, resources and activities
of the `Robert Koch Institute (RKI) <https://www.rki.de>`_ - the federal Public Health
institute of Germany - with the goal of making them findable and accessible via a web
application.

The MEx metadata schema enables the description of data and resources derived from the
research and other activities of the RKI. In most cases, the RKI's public health data
are protected by data protection laws. Instead of publishing the data itself, MEx
provides descriptions about the data. The MEx metadata model is designed to provide
comprehensive descriptions for RKI's public health data. MEx users can both find and
assess whether the data matches their interests and needs. To achieve this, we provide
detailed information about the data in the form of variables. Variables describe how the
actual data is specified and form the basis for a data-based evaluation of studies, for
example.

To collect information, MEx uses a mixed approach: In addition to manually compiling, we
also automatically extract information from various primary sources managed by the RKI
departments. To model this, we rely on the W3C recommendations
`DCAT <https://www.w3.org/TR/vocab-dcat-2/>`_ and
`PROV-O <http://www.w3.org/TR/prov-o/>`_.

Fields
------

.. jsonschema:: ../mex/model/fields/identifier.json
.. jsonschema:: ../mex/model/fields/link.json
.. jsonschema:: ../mex/model/fields/text.json

Entities
--------

.. jsonschema:: ../mex/model/entities/access-platform.json
.. jsonschema:: ../mex/model/entities/activity.json
.. jsonschema:: ../mex/model/entities/bibliographic-resource.json
.. jsonschema:: ../mex/model/entities/consent.json
.. jsonschema:: ../mex/model/entities/contact-point.json
.. jsonschema:: ../mex/model/entities/distribution.json
.. jsonschema:: ../mex/model/entities/organization.json
.. jsonschema:: ../mex/model/entities/organizational-unit.json
.. jsonschema:: ../mex/model/entities/person.json
    :encoding: utf8
.. jsonschema:: ../mex/model/entities/primary-source.json
.. jsonschema:: ../mex/model/entities/resource.json
.. jsonschema:: ../mex/model/entities/variable-group.json
.. jsonschema:: ../mex/model/entities/variable.json

Concepts
--------

.. jsonschema:: ../mex/model/entities/concept-scheme.json
.. jsonschema:: ../mex/model/entities/concept.json

Available concepts (aka vocabularies) soon. In the meantime, see
https://github.com/robert-koch-institut/mex-model/tree/main/mex/model/vocabularies

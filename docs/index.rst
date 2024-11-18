MEx Metadata Schema
===================

The MEx metadata schema is used to catalog Public Health data, resources and activities of the [Robert Koch Institute (RKI)](https://www.rki.de) - the federal Public Health institute of Germany - with the goal of making them findable and accessible via a web application.

The MEx metadata schema enables the description of data and resources derived from the (research) activities of RKI.
In most cases, the RKI's public health data are protected by data protection laws. Instead of publishing the data itself, MEx provides descriptions about the data. The MEx metadata model is designed to provide comprehensive descriptions for RKI's public health data. MEx users can both find and assess whether the data matches their interests and needs.
To achieve this, we provide detailed information about the data in the form of variables. Variables describe how the actual data is specified and form the basis for a data-based evaluation of studies, for example.

To collect information, MEx uses a mixed approach: In addition to manually compiling, we also automatically extract information from various primary sources managed by the RKI departments.
To model this, we rely on the W3C recommendations [DCAT](https://www.w3.org/TR/vocab-dcat-2/) and [PROV-O](http://www.w3.org/TR/prov-o/).

.. openapi:: swagger.yml

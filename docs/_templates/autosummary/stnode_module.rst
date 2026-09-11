{%- macro table(items, toctree) %}
.. autosummary::
{%- if toctree %}
   :toctree:
   :template: autosummary/class.rst
{%- endif %}
{% for item in items %}
   {{ item }}
{%- endfor %}
{% endmacro -%}

{%- set general_classes = [] -%}
{%- set science_nodes = [] -%}
{%- set reference_nodes = [] -%}
{%- set converters = [] -%}
{%- set serialization_nodes = [] -%}
{%- set legacy_objects = [] -%}
{%- set legacy_scalars = [] -%}
{%- set legacy_lists = [] -%}
{%- set legacy_mixins = [] -%}
{%- set groups = {
   "general": general_classes,
   "science-node": science_nodes,
   "reference-node": reference_nodes,
   "converter": converters,
   "serialization": serialization_nodes,
   "legacy-object": legacy_objects,
   "legacy-scalar": legacy_scalars,
   "legacy-list": legacy_lists,
   "legacy-mixin": legacy_mixins,
} -%}
{%- for item in all_classes -%}
{{- groups[stnode_category(fullname, item)].append(item) or "" -}}
{%- endfor -%}

{{ fullname | escape | underline }}

.. automodule:: {{ fullname }}

.. currentmodule:: {{ fullname }}

{% if general_classes %}
General Classes
---------------
{{ table(general_classes, true) }}
{% endif %}

{% if science_nodes or reference_nodes %}
DataModel Node Classes
----------------------

These node classes are documented in the *Node Class* section of the
:class:`~roman_datamodels.datamodels.DataModel` that wraps them.

{% if science_nodes %}
Science Product Node Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{{ table(science_nodes, false) }}
{% endif %}

{% if reference_nodes %}
Reference File Node Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~
{{ table(reference_nodes, false) }}
{% endif %}
{% endif %}

{% if converters or serialization_nodes %}
Serialization Classes
---------------------

{% if converters %}
ASDF Converter Classes
~~~~~~~~~~~~~~~~~~~~~~
{{ table(converters, true) }}
{% endif %}

{% if serialization_nodes %}
Serialization Node Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~
{{ table(serialization_nodes, true) }}
{% endif %}
{% endif %}

{% if all_functions %}
Functions
---------

.. autosummary::
   :toctree:
{% for item in all_functions %}
   {{ item }}
{%- endfor %}
{% endif %}

{% if legacy_objects or legacy_scalars or legacy_lists or legacy_mixins %}
Legacy Node Classes
-------------------

{% if legacy_objects %}
Legacy Object Node Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~
{{ table(legacy_objects, true) }}
{% endif %}

{% if legacy_scalars %}
Legacy Scalar Node Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~
{{ table(legacy_scalars, true) }}
{% endif %}

{% if legacy_lists %}
Legacy List Node Classes
~~~~~~~~~~~~~~~~~~~~~~~~
{{ table(legacy_lists, true) }}
{% endif %}

{% if legacy_mixins %}
Legacy Node Mixin Classes
~~~~~~~~~~~~~~~~~~~~~~~~~
{{ table(legacy_mixins, true) }}
{% endif %}
{% endif %}

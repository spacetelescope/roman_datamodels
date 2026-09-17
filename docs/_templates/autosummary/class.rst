{%- macro class_body(modname, objname, all_attributes, all_methods, uline) -%}
{% set attributes = documented_members(modname, objname, all_attributes) %}
{% set methods = documented_members(modname, objname, all_methods) | reject("equalto", "__init__") | list %}
{% set flags = enum_flags(modname, objname) %}
{% if flags %}
Flags
{{ uline * 5 }}

.. list-table::
   :header-rows: 1

   * - Bit
     - Value
     - Name
     - Description
{% for flag in flags %}
   * - {{ flag.bit_number }}
     - {{ flag.value }}
   {{ "  " }}- :attr:`~{{ objname }}.{{ flag.name }}`
     - {{ flag.description }}
{%- endfor %}

{% for flag in flags %}
.. autoattribute:: {{ objname }}.{{ flag.name }}
{%- endfor %}
{% endif %}

{% if attributes %}
Attributes
{{ uline * 10 }}

.. autosummary::
{% for item in attributes %}
   ~{{ objname }}.{{ item }}
{%- endfor %}

{% for item in attributes %}
{% if is_property(modname, objname, item) %}
.. autoproperty:: {{ objname }}.{{ item }}
{% else %}
.. autoattribute:: {{ objname }}.{{ item }}
{% endif %}
{%- endfor %}
{% endif %}

{% if methods %}
Methods
{{ uline * 7 }}

.. autosummary::
{% for item in methods %}
   ~{{ objname }}.{{ item }}
{%- endfor %}

{% for item in methods %}
.. automethod:: {{ objname }}.{{ item }}
{%- endfor %}
{% endif %}
{%- endmacro -%}

{{ fullname | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :show-inheritance:

{{ class_body(module, objname, attributes, methods, "-") }}

{% set node = node_class(module, objname) %}
{% if node %}
Node Class
----------

.. currentmodule:: {{ node.module }}

.. autoclass:: {{ node.name }}
   :show-inheritance:

{{ class_body(node.module, node.name, node.attributes, node.methods, "~") }}
{% endif %}

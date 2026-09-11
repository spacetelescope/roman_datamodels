{%- macro class_body(modname, objname, attributes, methods, uline) -%}
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
{% if item != "__init__" %}
   ~{{ objname }}.{{ item }}
{% endif %}
{%- endfor %}

{% for item in methods %}
{% if item != "__init__" %}
.. automethod:: {{ objname }}.{{ item }}
{% endif %}
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

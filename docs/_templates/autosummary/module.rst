{{ fullname | escape | underline }}

.. automodule:: {{ fullname }}

   {% block classes %}
   {% if all_classes %}
   {%- set general_classes = [] -%}
   {%- set science_models = [] -%}
   {%- set reference_models = [] -%}
   {%- for item in all_classes -%}
   {%- set category = datamodel_category(fullname, item) -%}
   {%- if category == "reference" -%}
   {{- reference_models.append(item) or "" -}}
   {%- elif category == "science" -%}
   {{- science_models.append(item) or "" -}}
   {%- else -%}
   {{- general_classes.append(item) or "" -}}
   {%- endif -%}
   {%- endfor %}

   {% if general_classes %}
   .. rubric:: {% if science_models or reference_models %}General Classes{% else %}Classes{% endif %}

   .. autosummary::
      :toctree:
      :template: autosummary/class.rst
   {% for item in general_classes %}
      {{ item }}
   {%- endfor %}
   {% endif %}

   {% if science_models %}
   .. rubric:: Science Product DataModel Classes

   .. autosummary::
      :toctree:
      :template: autosummary/class.rst
   {% for item in science_models %}
      {{ item }}
   {%- endfor %}
   {% endif %}

   {% if reference_models %}
   .. rubric:: Reference File DataModel Classes

   .. autosummary::
      :toctree:
      :template: autosummary/class.rst
   {% for item in reference_models %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endif %}
   {% endblock %}

   {% block exceptions %}
   {% if all_exceptions %}
   .. rubric:: Exceptions

   .. autosummary::
      :toctree:
      :template: autosummary/class.rst
   {% for item in all_exceptions %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block functions %}
   {% if all_functions %}
   .. rubric:: Functions

   .. autosummary::
      :toctree:
   {% for item in all_functions %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

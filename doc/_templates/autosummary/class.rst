.. raw:: html

    </div>
    <div class=col-md-9 content>

{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

   {% block methods %}
   .. automethod:: __init__

   {% block attributes %}
   {% if attributes %}
   .. rubric:: Attributes

   .. autosummary::
      :toctree:
   {% for item in attributes %}
   {%- if not item.startswith('_') %}
      ~{{ name }}.{{ item }}
   {%- endif -%}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% if methods %}
   .. rubric:: Methods

   .. autosummary::
      :toctree:
   {% for item in methods %}
   {%- if not item.startswith('_') or item in ['__call__'] %}
      ~{{ name }}.{{ item }}
   {%- endif -%}
   {%- endfor %}
   {% endif %}
   {% endblock %}

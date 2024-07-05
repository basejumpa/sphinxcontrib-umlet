sphinxcontrib-umlet
###################

Sphinx Extension for effordlessly embedding `UMLet <http://umlet.com>`_ diagrams in your Sphinx document.

.. code-block:: RST

    .. umlet-figure:: some_folder/some_diagram.uxf


It adds the **umlet-image** and **umlet-figure** directives.
These are equivalent to the standard **image** and **figure** directives, but
accept the path to a `.uxf` file and additional options to control
exporting of the diagram to a suitable image format.

.. attention::
    This extension does not work on readthedocs as RTD does not allow
    packages (e.g. UMLet) to be installed. If you only require diagrams in a single
    format, you can consider using editable SVGs or PNGs, accessible through
    UMLet's GUI via **File / Export**.

This extension is highly influenced by `sphinxcontrib-drawio <https://pypi.org/project/sphinxcontrib-drawio/>`_. Many thanks to the creator `@modelmat <https://github.com/modelmat>`_ !

Installation
************

1. Make sure that UMLet works on your machine. Java runtime in the path is a prerequisite.

2. Add the UMLet binary to `$PATH`. See below for more details and alternative solutions.

3. **pip install sphinxcontrib-umlet**
4. In your sphinx **conf.py**, register it to the extensions to use, such as:

.. code-block:: python

    extensions = []
    # ...
    extensions.append("sphinxcontrib.umlet")
    # ...


Usage
*****

The extension can be used through the **umlet-image** directive. For example:

.. code-block:: RST

    .. umlet-image:: some_diagram.uxf


There's also a **umlet-figure** directive that mimics the **figure** directive:

.. code-block:: RST

    .. umlet-figure:: some_diagram.uxf

        Some caption


The directives can be configured with option **format** to control the export of the specific
UMLet diagram to a bitmap or vector image. This option controls the output file format of **this specific** directive, so it overrides the export format commonly used or commonly configured in the **conf.py** file.

- **Name:** `:format:`
- **Default value:** :code:`"png"`
- **Possible Values:** :code:`"png"`, :code:`"jpg"`, :code:`"svg"` or :code:`"pdf"`

Additionally, **umlet-image** accepts all of the options supported by the
`image directive <https://docutils.sourceforge.io/docs/ref/rst/directives.html#image>`_.
These options apply to the image as exported by UMLet. Similarly,
**umlet-figure** accepts all options supported by the `figure directive <https://docutils.sourceforge.io/docs/ref/rst/directives.html#figure>`_.


Configuration Options
*********************

These values are placed in the **conf.py** of your Sphinx project.

.. _sec_binary_path:

Binary Path
===========

- **Name:** :code:`umlet_binary_path`
- **Default value:** :code:`None`

It is the path including the program's name.

This config option allows for a specific override for the binary location. By default, this
chooses the **umlet.sh** (resp. **Umlet.exe**) binary accessible in `$PATH`.


Default Output Format
=====================

- **Name:** :code:`umlet_builder_export_format`
- **Default value:** :code:`{}`

This config option controls the default export file format for each Sphinx builder.

It accepts a dictionary mapping builder names to image formats. The
builder name should match the name of a `Sphinx builder <https://www.sphinx-doc.org/en/master/usage/builders/index.html>`_
(e.g., :code:`"html"`, :code:`"latex"`). Accepted values for the export format are :code:`"png"`,
:code:`"jpg"`, :code:`"svg"` and :code:`"pdf"`. If no format is set for a given builder, its
preferred image format is used, that is, the first format listed in a builder's
supported image types that UMLet is capable of exporting to (eg. SVG for HTML, PDF for LaTeX).

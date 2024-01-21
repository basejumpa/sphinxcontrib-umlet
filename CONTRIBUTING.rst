Contributing to sphinxcontrib-umlet
###################################

If you have an bug or issue, please `create an issue <https://github.com/basejumpa/sphinxcontrib-umlet/issues>`_ using the relevant template.


Adding new functionality
************************

* Please ensure that all relevant changes are documented in the README
* Ensure that your code meets the black formatter standards (run the formatter)


Releasing new versions
**********************

To release a new version, create a new commit which increases :code:`__version__`
inside **sphinxcontrib/umlet/__init__.py**. Do this according `Semantic Versioning 2.0.0 <https://semver.org/>`_.

Then use GitHub relases to
"Draft a new release" by creating a new tag named with the version.
This will trigger the `CI <https://github.com/basejumpa/sphinxcontrib-umlet/actions>`_ to push to `PyPI <https://pypi.org/project/sphinxcontrib-umlet/>`_.

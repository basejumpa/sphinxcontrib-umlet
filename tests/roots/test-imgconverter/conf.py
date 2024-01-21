extensions = ["sphinxcontrib.umlet", "sphinx.ext.imgconverter"]

master_doc = "index"
exclude_patterns = ["_build"]

# removes most of the HTML
html_theme = "basic"

umlet_builder_export_format = {"html": "svg", "latex": "pdf"}

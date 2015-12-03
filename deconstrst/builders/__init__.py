from sphinx.config import Config

# Tell Sphinx about the deconst_default_layout and deconst_default_unsearchable keys.
Config.config_values["deconst_default_layout"] = ("default", "html")
Config.config_values["deconst_default_unsearchable"] = (None, "html")

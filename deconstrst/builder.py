# -*- coding: utf-8 -*-

from sphinx.builders.html import JSONHTMLBuilder
from sphinx.util import jsonimpl


class DeconstJSONImpl:
    """
    Enhance the default JSON encoder by adding additional keys.
    """

    def dump(self, obj, fp, *args, **kwargs):
        self._enhance(obj)
        return jsonimpl.dump(obj, fp, *args, **kwargs)

    def dumps(self, obj, *args, **kwargs):
        self._enhance(obj)
        return jsonimpl.dumps(obj, *args, **kwargs)

    def load(self, *args, **kwargs):
        return jsonimpl.load(*args, **kwargs)

    def loads(self, *args, **kwargs):
        return jsonimpl.loads(*args, **kwargs)

    def _enhance(self, obj):
        """
        Add additional properties to "obj" to get them into the JSON.
        """

        obj["hello"] = "Sup"


class DeconstJSONBuilder(JSONHTMLBuilder):
    """
    Custom Sphinx builder that generates Deconst-compatible JSON documents.
    """

    implementation = DeconstJSONImpl()
    name = 'deconst'
    out_suffix = '.json'

    def init(self):
        JSONHTMLBuilder.init(self)

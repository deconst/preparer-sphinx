# Deconst RST preparer

.rst :point_right: .json :point_right: :wrench: :point_right: content service

*deconstrst* builds [Sphinx documentation](http://sphinx-doc.org/contents.html) into a custom JSON metadata envelope and broadcasts it to a *Content Storage* service that performs storage and indexing for presentation and search.

It's intended to be used within a CI system to present content to the rest of build pipeline.

## reStructuredText integration

Sphinx doesn't natively have the concept of a per-page layout. To tell Deconst what layout to use for a specific page, add the following field to a field list that's the *first thing* within a page, along with any other [per-page metadata](http://sphinx-doc.org/markup/misc.html#file-wide-metadata) that's present:

```rst
:deconstlayout: this-page-layout-key
```

If this field isn't specified, a setting in your `conf.py` will be used:

```python
deconst_default_layout = "default-layout-key"
```

Finally, the preparer will fall back to `"default"` if no other key is specified.

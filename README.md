# Deconst Sphinx preparer

.rst :point_right: :wrench: :point_right: .json

[![Build Status](https://travis-ci.org/deconst/preparer-sphinx.svg?branch=master)](https://travis-ci.org/deconst/preparer-sphinx) [![Docker Repository on Quay.io](https://quay.io/repository/deconst/preparer-sphinx/status "Docker Repository on Quay.io")](https://quay.io/repository/deconst/preparer-sphinx)

The *deconst Sphinx preparer* builds [Sphinx documentation](http://sphinx-doc.org/contents.html) into custom JSON metadata envelopes. It's intended to be used within a CI system to present content to the rest of build pipeline.

## Running locally

To run the Sphinx preparer locally, you'll need to install [Docker](https://docs.docker.com/installation/#installation) for your platform.

Once you have Docker set up, export any desired configuration variables and run `deconst-preparer-sphinx.sh` with the absolute path to any Sphinx-based content repository.

```bash
./deconst-preparer-sphinx.sh /absolute/path/to/content-repo
```

### Configuration

#### Environment variables

The following values may be present in the environment:

 * `CONTENT_ROOT` is a path containing Sphinx content to prepare. *Default: $(pwd)*
 * `ENVELOPE_DIR` is the destination directory for metadata envelopes. *Default: $(pwd)/_build/deconst-envelopes/*
 * `ASSET_DIR` is the destination directory for referenced assets. *Default: $(pwd)/_build/deconst-assets/*
 * `CONTENT_ID_BASE` is a prefix that's unique among the content repositories associated with the target deconst instance. Our convention is to use the base URL of the GitHub repository. *Default: Read from _deconst.json*

#### `conf.py`

By default, the preparer will use the `deconst-serial` builder, which will generate a separate HTML file for every ReST file in your repository. This behavior is similar to running `make html`. If you would rather generate a single HTML file with the contents of your entire repo (à la `make singlehtml`), you must add the following line to your `conf.py` file:

```python
builder = 'deconst-single'
```

The `deconst_default_unsearchable` property may be set to `True` to exclude *all* content from this content repository from being indexed for search.

```python
deconst_default_unsearchable = True
```

One or more page categories can be specified for the entire content repository at once with the `deconst_categories` property. These are useful for constraining search results and may be used by site templates.

```python
deconst_categories = ['global category one', 'global category two']
```

#### Per-page metadata

The Sphinx preparer offers page-level customization by reading [per-page metadata](http://sphinx-doc.org/markup/misc.html#file-wide-metadata) that's present on each page.

The page title offered to Deconst templates may be overridden with the `deconsttitle` attribute:

```rst
:deconsttitle: Not the Sphinx title
```

This is especially important for your `index.rst` file, which by default generates a title of "&lt; no title &gt;".

Set additional categories for individual pages with the `deconstcategories` attribute. Use a comma-separated list of category names. Whitespace will be trimmed from each category.

```rst
:deconstcategories: page category one, page category two
```

Individual pages can be excluded from search indexing with the `deconstunsearchable` attribute. Use the string `true` to exclude a specific page.

```rst
:deconstunsearchable: true
```

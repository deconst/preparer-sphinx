# Deconst Sphinx preparer

.rst :point_right: :wrench: :point_right: .json

[![Build Status](https://travis-ci.org/deconst/preparer-sphinx.svg?branch=master)](https://travis-ci.org/deconst/preparer-sphinx) [![Docker Repository on Quay.io](https://quay.io/repository/deconst/preparer-sphinx/status "Docker Repository on Quay.io")](https://quay.io/repository/deconst/preparer-sphinx)

The *deconst Sphinx preparer* builds [Sphinx documentation](http://sphinx-doc.org/contents.html) into a custom JSON metadata envelope and broadcasts it to a *Content Storage* service that performs storage and indexing for presentation and search.

It's intended to be used within a CI system to present content to the rest of build pipeline.

## Running Locally

To run the Sphinx preparer locally, you'll need to install:

 * [Docker](https://docs.docker.com/installation/#installation) for your platform. Choose the boot2docker option for Mac OS X or Windows.

Once you have Docker set up, export any desired configuration variables, run `deconst-preparer-sphinx.sh` with the path of a control repository clone to prepare the assets found there.

```bash
export CONTENT_STORE_URL=http://my-content-store.com:9000/
export CONTENT_STORE_APIKEY="cd54a09f6593cb5b17177..."
export CONTENT_ID_BASE=https://github.com/myorg/myrepo

# Ignore TLS certificate verification
# Very bad, but sometimes necessary in development or local environments
# export CONTENT_STORE_TLS_VERIFY="false"

./deconst-preparer-sphinx.sh /path/to/control-repo
```

### Configuration

By default, the preparer will use the `deconst-serial` builder, which will generate a separate HTML file for every ReST file in your repository. This behavior is similar to running `make html`. If you would rather generate a single HTML file with the contents of your entire repo (à la `make singlehtml`), you must add the following line to your `conf.py` file:

```python
builder = 'deconst-single'
```

The following values must be present in the build environment to submit assets:

 * `CONTENT_STORE_URL` must be the base URL of the publicly available content store service. The prepare script defaults this to one consistent with our docker-compose setups.
 * `CONTENT_STORE_APIKEY` must be a valid API key issued by the content service. See [the content service documentation](https://github.com/deconst/content-service#post-keysnamedname) for instructions on generating an API key.
 * `CONTENT_ID_BASE` must be set to a prefix that's unique among the content repositories associated with the target deconst instance. Our convention is to use the base URL of the GitHub repository.
 * `TRAVIS_PULL_REQUEST` must be set to `"false"`. Travis automatically sets this value for your build environment on the primary branch of your repository.

## reStructuredText integration

### Layout

Sphinx doesn't natively have the concept of a per-page layout. To tell Deconst which layout to use for a specific page, add the following field to a field list that's the *first thing* within a page, along with any other [per-page metadata](http://sphinx-doc.org/markup/misc.html#file-wide-metadata) that's present:

```rst
:deconstlayout: this-page-layout-key
```

If this field isn't specified, a setting in your `conf.py` will be used:

```python
deconst_default_layout = "default-layout-key"
```

Finally, the preparer will fall back to `"default"` if no other key is specified.

### Title

Similary, you can override the `"title"` Sphinx generates for any page by specifying a `deconsttitle` per-page attribute:

```rst
:deconsttitle: The real title
```

This is especially important for your `index.rst` file, which by default generates a title of "&lt; no title &gt;".

### Categories

You can set the Deconst categories for each page with the `deconstcategories` per-page attribute:

```rst
:deconstcategories: category one, category two
```

Categories that should be applied to *all* pages may be specifed in your `conf.py` file, with the rest of your Sphinx settings:

```python
deconst_categories = ['global category', 'global category']
```

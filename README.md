# Deconst Sphinx preparer

.rst :point_right: .json :point_right: :wrench: :point_right: content service

[![Docker Repository on Quay.io](https://quay.io/repository/deconst/preparer-sphinx/status "Docker Repository on Quay.io")](https://quay.io/repository/deconst/preparer-sphinx)

The *deconst Sphinx preparer* builds [Sphinx documentation](http://sphinx-doc.org/contents.html) into a custom JSON metadata envelope and broadcasts it to a *Content Storage* service that performs storage and indexing for presentation and search.

It's intended to be used within a CI system to present content to the rest of build pipeline.

## Running Locally

To run the Sphinx preparer locally, you'll need to install:

 * [Docker](https://docs.docker.com/installation/#installation) for your platform. Choose the boot2docker option for Mac OS X or Windows.

Once you have Docker set up, export any desired configuration variables, run `deconst-preparer-sphinx.sh` with the path of a control repository clone to prepare the assets found there.

```bash
export CONTENT_STORE_URL=http://my-content-store.com:9000/
export CONTENT_ID_BASE=https://github.com/myorg/myrepo

./deconst-preparer-sphinx.sh /path/to/control-repo
```

### Configuration

The following values must be present in the build environment to submit assets:

 * `CONTENT_STORE_URL` must be the base URL of the publicly available content store service. The prepare script defaults this to one consistent with our docker-compose setups.
 * `CONTENT_ID_BASE` must be set to a prefix that's unique among the content repositories associated with the target deconst instance. Our convention is to use the base URL of the GitHub repository.
 * `TRAVIS_PULL_REQUEST` must be set to `"false"`. Travis automatically sets this value for your build environment on the primary branch of your repository.

## reStructuredText integration

Sphinx doesn't natively have the concept of a per-page layout. To tell Deconst which layout to use for a specific page, add the following field to a field list that's the *first thing* within a page, along with any other [per-page metadata](http://sphinx-doc.org/markup/misc.html#file-wide-metadata) that's present:

```rst
:deconstlayout: this-page-layout-key
```

If this field isn't specified, a setting in your `conf.py` will be used:

```python
deconst_default_layout = "default-layout-key"
```

Finally, the preparer will fall back to `"default"` if no other key is specified.

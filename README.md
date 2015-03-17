# Deconst RST preparer

.rst :point_right: .json :point_right: :wrench: :point_right: content service

*deconstrst* builds [Sphinx documentation](http://sphinx-doc.org/contents.html) into a custom JSON metadata envelope and broadcasts it to a *Content Storage* service that performs storage and indexing for presentation and search.

It's intended to be used within a CI system to present content to the rest of build pipeline.

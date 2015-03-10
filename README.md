# Deconst RST renderer

.rst :point_right: .json :point_right: :wrench: :point_right: cloud files

*deconstrst* builds [Sphinx documentation](http://sphinx-doc.org/contents.html) into a custom JSON format and broadcasts it to:

 1. *Cloud Files* for direct access by the presentation layer
 2. A *Content Storage* service that performs indexing for search
 3. The *GitHub status API* to indicate the success or failure of a specific SHA.

It's intended to be used within a CI system to present content to the rest of build pipeline.

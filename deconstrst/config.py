# -*- coding: utf-8 -*-


def _normalize(url):
    """
    Ensure that its argument ends with a trailing / if it's nonempty.
    """

    if url and not url.endswith("/"):
        return url + "/"
    else:
        return url


class Configuration:
    """
    Configuration settings derived from the environment and current git branch.
    """

    def __init__(self, env):
        self.content_store_url = _normalize(env.get("CONTENT_STORE_URL"))
        self.content_id_base = _normalize(env.get("CONTENT_ID_BASE"))
        self.is_primary = env.get("TRAVIS_PULL_REQUEST") == "false"

    def skip_submit_reasons(self):
        """
        Determine whether or not the current build should result in submission
        to the content service. If not, return a list of reasons why it won't.
        """

        reasons = []

        if not self.content_store_url:
            reasons.append("CONTENT_STORE_URL is missing. It should be the "
                           "base URL of the content storage service.")

        if not self.content_id_base:
            reasons.append("CONTENT_ID_BASE is missing. It should be the base "
                           "URL used to generate IDs for content within this "
                           "repository.")

        if not self.is_primary:
            reasons.append("This looks like a pull request build on Travis.")

        return reasons

    @classmethod
    def load(cls, env):
        """
        Derive the current configuration from the environment.
        """

        return cls(env)

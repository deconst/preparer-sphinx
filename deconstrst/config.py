# -*- coding: utf-8 -*-

import json
from os import path


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
        self.content_store_apikey = env.get("CONTENT_STORE_APIKEY")
        self.content_id_base = _normalize(env.get("CONTENT_ID_BASE"))
        self.is_primary = env.get("TRAVIS_PULL_REQUEST") == "false"
        self.tls_verify = env.get("CONTENT_STORE_TLS_VERIFY") != "false"
        self.meta = {}
        self.github_url = ""
        self.github_branch = "master"

    def apply_file(self, f):
        """
        Parse the contents of an open filehandle as JSON and apply recognized
        settings found there to this configuration.

        Environment variables take precedence over any values found here.
        """

        doc = json.load(f)

        if "contentIDBase" in doc:
            if not self.content_id_base:
                self.content_id_base = _normalize(doc["contentIDBase"])
            elif self.content_id_base != _normalize(doc["contentIDBase"]):
                print("Using environment variable CONTENT_ID_BASE=[{}] "
                      "instead of _deconst.json setting [{}]."
                      .format(self.content_id_base, doc["contentIDBase"]))

        if "meta" in doc:
            self.meta = doc["meta"]

        if "githubUrl" in doc:
            self.github_url = doc["githubUrl"]
            self.github_issues_url = '/'.join(segment.strip('/') for segment in [doc["githubUrl"], 'issues'])
            self.meta.update({'github_issues_url': self.github_issues_url})

        if "githubBranch" in doc:
            self.github_branch = doc["githubBranch"]
        else:
            self.github_branch = "master"

    def get_git_root (self, d):
        """
        Walk up until we find the ".git" directory, and return its parent
        """
        if(path.isdir(path.join(d, '.git'))):
            return d

        if(d == '/'):
            raise FileNotFoundError

        return self.get_git_root(path.realpath(path.join(d, '..')))

    def skip_submit_reasons(self):
        """
        Determine whether or not the current build should result in submission
        to the content service. If not, return a list of reasons why it won't.
        """

        reasons = []

        if not self.content_store_url:
            reasons.append("CONTENT_STORE_URL is missing. It should be the "
                           "base URL of the content storage service.")

        if not self.content_store_apikey:
            reasons.append("CONTENT_STORE_APIKEY is missing. It should be a "
                           "valid API key issued by the content service.")

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

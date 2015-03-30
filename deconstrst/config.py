# -*- coding: utf-8 -*-

import sh
import re


class Configuration:
    """
    Configuration settings derived from the environment and current git branch.
    """

    def __init__(self, env):
        self.content_store_url = env.get("CONTENT_STORE_URL")
        self.content_id_base = env.get("CONTENT_ID_BASE")
        self.deployment_ref = re.compile(env.get("DEPLOY_REF",
                                                 "refs/heads/master"))

        try:
            self.refname = self.sh.git("symbolic-ref", "HEAD").strip()
        except sh.ErrorReturnCode:
            self.refname = ""

    def skip_submit_reasons(self):
        """
        Determine whether or not the current build should result in submission
        to the content service. If not, return a list of reasons why it won't.
        """

        reasons = []

        if not self.content_store_url:
            reasons.append("Missing CONTENT_STORE_URL, the base URL of the "
                           "content storage service.")

        if not self.content_id_base:
            reasons.append("Missing CONTENT_ID_BASE, the base URL used to "
                           "generate IDs for content within this repository.")

        if not self.deployment_ref.match(self.refname):
            reasons.append(
                "The current git ref ({}) doesn't match the deployment ref "
                "regexp ({}).".format(self.refname,
                                      self.deployment_ref.pattern))

        return reasons

    @classmethod
    def load(cls, env):
        """
        Derive the current configuration from the environment.
        """

        return cls(env)

# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import subprocess
import urllib.request


def _download(url, path):
    # TODO: this is AI-generated code; human review pending
    with urllib.request.urlopen(url) as r, open(path, 'wb') as fh:
        while chunk := r.read(1 << 20):
            fh.write(chunk)


def _run(cmd, env=None):
    # TODO: this is AI-generated code; human review pending
    subprocess.run(cmd, check=True, env=env)

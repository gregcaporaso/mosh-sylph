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
    with urllib.request.urlopen(url) as r, open(path, 'wb') as fh:
        # read chunks of 1 MiB
        while chunk := r.read(1 << 20):
            fh.write(chunk)


def _run(cmd):
    subprocess.run(cmd, check=True)

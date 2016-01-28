#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

import os
import py2exe

from distutils.core import setup

try:
    target = os.environ['PY2EXE_MODE']
except KeyError:
    target = 'multi'

if target == 'single':
    ZIPFILE = None
    BUNDLES = 3
else:
    ZIPFILE = 'shared-converter.lib'
    BUNDLES = 3

setup(console=[{'script': 'convert-video.py'}],
      options={'py2exe': {'includes': [],
                          'compressed': True,
                          'bundle_files': BUNDLES,
                          'dll_excludes': ['MSVCP90.dll']
                          },
               },
      zipfile=ZIPFILE)

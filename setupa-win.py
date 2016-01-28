#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

import os
import py2exe

# sys.path.append(os.path.abspath('../'))

from distutils.core import setup

try:
    target = os.environ['PY2EXE_MODE']
except KeyError:
    target = 'multi'

if target == 'single':
    ZIPFILE = None
    BUNDLES = 3
else:
    ZIPFILE = 'shared.lib'
    BUNDLES = 3

setup(windows=[{'script': 'convert-video.py',
                'icon_resources': [(0, 'flash-video-encoder.ico')]}],
      options={'py2exe': {'includes': [],
                          'compressed': True,
                          'bundle_files': BUNDLES,
                          'dll_excludes': ['MSVCP90.dll']
                          },
               },
      zipfile=ZIPFILE)

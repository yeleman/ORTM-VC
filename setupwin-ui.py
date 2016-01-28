#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

import os
import py2exe

from distutils.core import setup

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    target = os.environ['PY2EXE_MODE']
except KeyError:
    target = 'multi'

if target == 'single':
    ZIPFILE = None
    BUNDLES = 3
else:
    ZIPFILE = 'shared-ui.lib'
    BUNDLES = 3

setup(windows=[{'script': 'convert-video-tk.py',
                'icon_resources': [
                    (0, os.path.join(ROOT_DIR, 'flash-video-encoder.ico'))]}],
      options={'py2exe': {'includes': [],
                          'compressed': True,
                          'bundle_files': BUNDLES,
                          'dll_excludes': ['MSVCP90.dll']
                          },
               },
      zipfile=ZIPFILE)

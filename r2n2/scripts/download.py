#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import shapenet.r2n2.tgz as tgz


tgz.BinvoxManager().download()
tgz.RenderingsManager().download()

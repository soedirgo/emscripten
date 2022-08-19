# Copyright 2022 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

"""Utilities for mapping browser versions to llvm feature flags."""

import logging
from enum import IntEnum, auto

from .settings import settings

logger = logging.getLogger('feature_matrix')


class Feature(IntEnum):
  NON_TRAPPING_FPTOINT = auto()
  SIGN_EXT = auto()
  BULK_MEMORY = auto()
  MUTABLE_GLOBALS = auto()


min_browser_versions = {
  Feature.NON_TRAPPING_FPTOINT: {
    'chrome': 75,
    'firefox': 65,
    'safari': 150000,
  },
  Feature.SIGN_EXT: {
    'chrome': 74,
    'firefox': 62,
    'safari': 141000,
  },
  Feature.BULK_MEMORY: {
    'chrome': 75,
    'firefox': 79,
    'safari': 150000,
  },
  Feature.MUTABLE_GLOBALS: {
    'chrome': 74,
    'firefox': 61,
    'safari': 120000,
  },
}


def caniuse(feature):
  min_versions = min_browser_versions[feature]
  if settings.MIN_CHROME_VERSION < min_versions['chrome']:
    return False
  if settings.MIN_FIREFOX_VERSION < min_versions['firefox']:
    return False
  if settings.MIN_SAFARI_VERSION < min_versions['safari']:
    return False
  # IE and Edge don't support any non-MVP features
  if settings.MIN_IE_VERSION != 0x7FFFFFFF or settings.MIN_EDGE_VERSION != 0x7FFFFFFF:
    return False
  return True


def get_feature_flags():
  flags = []

  # Enabling threads, or PIC implicitly opts into many of these features.
  # TODO(sbc): We should probably have USE_PTHREADS/RELOCATABLE
  # implicitly bump the min browser versions instead.
  if settings.USE_PTHREADS or settings.RELOCATABLE:
    return flags

  if not caniuse(Feature.NON_TRAPPING_FPTOINT):
    logger.debug('adding -mno-nontrapping-fptoint due to target browser selection')
    flags.append('-mno-nontrapping-fptoint')

  if not caniuse(Feature.SIGN_EXT):
    logger.debug('adding -mnosign-ext due to target browser selection')
    flags.append('-mno-sign-ext')

  if not caniuse(Feature.BULK_MEMORY):
    logger.debug('adding -mnobulk-memory due to target browser selection')
    flags.append('-mno-bulk-memory')

  if not caniuse(Feature.MUTABLE_GLOBALS):
    logger.debug('adding -mnomutable-globals due to target browser selection')
    flags.append('-mno-mutable-globals')

  return flags

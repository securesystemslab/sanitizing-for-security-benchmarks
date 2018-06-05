import os
import util
import clang
import common


command = 'cfi-forward-edge'
configs = common.configs
CFI_FORWARD_EDGE_OPTIONS = [
    'cfi-nvcall',
    'cfi-vcall',
    'cfi-icall'
]


def test(config):
    return True


def setup(config):
    common.setup(command, config, CFI_FORWARD_EDGE_OPTIONS)


def clean(config):
    clang.common.clean(config)


def run(config):
    common.run(command, config)

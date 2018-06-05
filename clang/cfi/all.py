import os
import util
import clang
import common


command = 'cfi'
configs = common.configs
CFI_ALL_OPTIONS = ['cfi']


def test(config):
    return True


def setup(config):
    common.setup(command, config, CFI_ALL_OPTIONS)


def clean(config):
    clang.common.clean(config)


def run(config):
    common.run(command, config)

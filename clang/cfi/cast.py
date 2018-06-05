import os
import util
import clang
import common


command = 'cfi-cast'
configs = common.configs

# only the ones enabled with the sanitizer group -fsanitize=cfi
CFI_CAST_OPTIONS = [
    'cfi-unrelated-cast',
    'cfi-derived-cast'
]


def test(config):
    return True


def setup(config):
    common.setup(command, config, CFI_CAST_OPTIONS)


def clean(config):
    clang.common.clean(config)


def run(config):
    common.run(command, config)

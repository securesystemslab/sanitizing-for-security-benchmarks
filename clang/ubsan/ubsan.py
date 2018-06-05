import os
import util
import clang.common as common


command = 'ubsan'
configs = ['baseline-spec', 'spec']


def test(config):
    return True


def setup(config):
    common.setup(config)

    # Create spec config file
    print 'creating spec config file...'

    spec_cfg = '-'.join([command, config]) + '.cfg'

    if os.path.exists(spec_cfg):
        os.remove(spec_cfg)

    cflags = list()
    if config == configs[1]:
        cflags.append('-fsanitize=undefined')

    path = os.path.abspath(os.path.join('llvm-%s' % common.llvmver, 'bin'))
    cc = [os.path.join(path, 'clang')]
    cc.extend(cflags)
    cxx = [os.path.join(path, 'clang++')]
    cxx.extend(cflags)

    util.spec.create_config(dir=os.getcwd(), file=spec_cfg,
                            name='-'.join([command, config]),
                            cc=' '.join(cc), cxx=' '.join(cxx),
                            cxxportability=common.cxxportability)


def clean(config):
    common.clean(config)


def run(config):
    benchmarks = util.spec.all_benchmarks
    common.run(command, config, benchmarks)

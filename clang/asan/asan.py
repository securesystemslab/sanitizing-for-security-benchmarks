import os
import util
import clang.common as common


command = 'asan'
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
    cflags.append('-DPATCH_PERLBENCH_OVERFLOW')
    cflags.append('-DPATCH_H264REF_OVERFLOW')

    cxxflags = list()
    cxxflags.append('-DNO_OMNETPP_OPERATOR_NEW')

    if config == configs[1]:
        cflags.append('-fsanitize=address')
        cxxflags.append('-fsanitize=address')

        # workaround for global buffer overflow in 464.h264ref
        blacklist = os.path.join(os.path.dirname(__file__), 'blacklist.txt')
        cflags.append('-fsanitize-blacklist=%s' % blacklist)

    path = os.path.abspath(os.path.join('llvm-%s' % common.llvmver, 'bin'))
    cc = [os.path.join(path, 'clang')]
    cc.extend(cflags)
    cxx = [os.path.join(path, 'clang++')]
    cxx.extend(cxxflags)

    util.spec.create_config(dir=os.getcwd(), file=spec_cfg,
                            name='-'.join([command, config]),
                            cc=' '.join(cc), cxx=' '.join(cxx),
                            cxxportability=common.cxxportability)


def clean(config):
    common.clean(config)


def run(config):
    ASAN_OPTIONS = ['detect_leaks=0', 'alloc_dealloc_mismatch=0']
    if config == configs[1]:
        os.environ['ASAN_OPTIONS'] = ':'.join(ASAN_OPTIONS)

    benchmarks = util.spec.all_benchmarks
    common.run(command, config, benchmarks)

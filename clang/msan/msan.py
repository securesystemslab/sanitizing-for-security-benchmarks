import os
import util
import clang.common as common


command = 'msan'
configs = ['baseline-spec', 'spec', 'spec-recover']


def test(config):
    return True


def setup(config):
    common.setup(config=config)

    # Compile libcxx & libcxxabi
    projects_dir = os.path.join('llvm', 'projects')
    libcxx_dir = os.path.join(projects_dir, 'libcxx')
    libcxxabi_dir = os.path.join(projects_dir, 'libcxxabi')
    util.llvm.download_libcxx(version=common.llvmver,
                              libcxx=not os.path.exists(libcxx_dir),
                              libcxxabi=not os.path.exists(libcxxabi_dir))

    if not os.path.exists('libcxx'):
        os.mkdir('libcxx')
        path = os.path.abspath(os.path.join('llvm-%s' % common.llvmver, 'bin'))
        os.environ['PATH'] = ':'.join([path, os.environ['PATH']])

        options = [
            '-DCMAKE_C_COMPILER=clang',
            '-DCMAKE_CXX_COMPILER=clang++'
        ]

        if config == configs[1]:
            options.append('-DLLVM_USE_SANITIZER=Memory')

        util.llvm.compile_libcxx(src_dir=os.path.abspath('llvm'),
                                 build_dir=os.path.abspath('libcxx'),
                                 install_dir=os.path.abspath(os.getcwd()),
                                 options=options)

    # Create spec config file
    print 'creating spec config file...'

    spec_cfg = '-'.join([command, config]) + '.cfg'

    if os.path.exists(spec_cfg):
        os.remove(spec_cfg)

    cflags = list()

    if config == configs[1] or config == configs[2]:
        cflags.append('-fsanitize=memory')

    if config == configs[2]:
        cflags.append('-fsanitize-recover=memory')

    libcxx_path = os.path.abspath('libcxx')

    cxxflags = list(cflags)
    cxxflags.append('-DNO_OMNETPP_OPERATOR_NEW')
    cxxflags.append('-DNO_DEALII_STD_PAIR')
    cxxflags.extend([
        '-stdlib=libc++',
        '-I%s' % os.path.join(libcxx_path, 'include'),
        '-I%s' % os.path.join(libcxx_path, 'include', 'c++', 'v1')
    ])

    path = os.path.abspath(os.path.join('llvm-%s' % common.llvmver, 'bin'))
    cc = [os.path.join(path, 'clang')]
    cc.extend(cflags)
    cxx = [os.path.join(path, 'clang++')]
    cxx.extend(cxxflags)

    extra_cxxlibs = [
        '-L%s' % os.path.join(libcxx_path, 'lib'),
        '-Wl,-rpath=%s' % os.path.join(libcxx_path, 'lib'),
        '-lc++abi'
    ]

    util.spec.create_config(dir=os.getcwd(), file=spec_cfg,
                            name='-'.join([command, config]),
                            cc=' '.join(cc), cxx=' '.join(cxx),
                            extra_cxxlibs=' '.join(extra_cxxlibs),
                            cxxportability=common.cxxportability)


def clean(config):
    common.clean(config)


def run(config):
    benchmarks = util.spec.all_benchmarks
    if config == configs[2]:
        os.environ['MSAN_OPTIONS'] = 'halt_on_error=0'
        benchmarks = ['403.gcc']

    common.run(command, config, benchmarks)

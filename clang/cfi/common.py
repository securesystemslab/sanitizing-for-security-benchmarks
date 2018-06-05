import os
import shutil
import util
import clang


binutils_tarball_format = 'binutils-VERSION.tar.bz2'
binutils_url_format = 'http://ftp.gnu.org/gnu/binutils/TARBALL'
binutils_version = '2.30'

configs = ['baseline-spec-cpp', 'spec-cpp']


def prepare_gold(version):
    curdir = os.getcwd()
    binutils_tarball = binutils_tarball_format.replace('VERSION', version)
    binutils_url = binutils_url_format.replace('TARBALL', binutils_tarball)
    util.download(binutils_url)
    util.untar(binutils_tarball)
    os.chdir('binutils-VERSION'.replace('VERSION', version))
    util.configure('--prefix=%s --enable-gold --enable-plugins --disable-werror' % curdir)
    util.make('-j4')
    util.make('-j4 all-gold')
    util.make('install')
    os.chdir(curdir)


def setup(command, config, cfi_flags):
    workdir = os.getcwd()

    if not os.path.exists('bin/ld'):
        prepare_gold(binutils_version)
        os.remove('bin/ld')
        shutil.copy('bin/ld.gold', 'bin/ld')

    compile_flags = ['-DLLVM_BINUTILS_INCDIR=%s/include' % workdir]
    clang.common.setup(config, compile_flags)

    # Create spec config file
    print 'creating spec config file...'

    spec_cfg = '-'.join([command, config]) + '.cfg'

    if os.path.exists(spec_cfg):
        os.remove(spec_cfg)

    cflags = list()

    if config == configs[1]:
        cflags.append('-fsanitize=%s' % ','.join(cfi_flags))
        cflags.append('-fno-sanitize-trap=%s' % ','.join(cfi_flags))
        cflags.append('-fsanitize-recover=all')

    cflags.append('-flto')
    cflags.append('-fvisibility=hidden')

    path = os.path.abspath(os.path.join('llvm-%s' % clang.common.llvmver, 'bin'))
    cc = [os.path.join(path, 'clang')]
    cc.extend(cflags)
    cxx = [os.path.join(path, 'clang++')]
    cxx.extend(cflags)

    util.spec.create_config(dir=os.getcwd(), file=spec_cfg,
                            name='-'.join([command, config]),
                            cc=' '.join(cc), cxx=' '.join(cxx),
                            cxxportability=clang.common.cxxportability)


def run(command, config):
    os.environ['PATH'] = ':'.join([os.path.abspath('bin'), os.environ['PATH']])
    benchmarks = util.spec.cpp_benchmarks
    clang.common.run(command, config, benchmarks)

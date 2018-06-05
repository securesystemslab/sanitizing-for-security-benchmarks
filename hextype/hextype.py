import os
import shutil
import subprocess
import util


command = 'hextype'
configs = ['baseline-spec-cpp', 'spec-cpp']
hextype_repo = 'https://github.com/HexHive/HexType.git'
hextype_commit = '64c5469c53bd6b79b404c1b203da8a114107ec96'
llvm_commit = '8f4f26c9c7fec12eb039be6b20313a51417c97bb'
clang_commit = 'd59a142ef50bf041797143db71d2d4777fd32d27'
compilerrt_commit = '961e78720a32929d7e4fc13a72d7266d59672c42'


def test(config):
    cwd = os.getcwd()

    os.chdir('test')

    if not os.path.exists('shrc'):
        raise Exception('no shrc found in directory %s' % testdir)

    try:
        f = open('shrc', 'r')
        lines = f.readlines()
        for line in lines:
            (key, _, value) = line.partition('=')
            os.environ[key.split()[1]] = value.rstrip().replace('"', '')
    finally:
        f.close()

    util.make('clean')
    util.make()
    util.make('test')

    os.chdir(cwd)


def setup(config):
    workdir = os.path.abspath(os.getcwd())

    if not os.path.exists('HexType'):
        util.git.clone(hextype_repo)
        os.chdir('HexType')
        util.git.checkout(hextype_commit)
        os.chdir('..')

    if not os.path.exists('llvm'):
        util.llvm.checkout(llvm_commit, clang_commit, compilerrt_commit)

        # apply HexType patches
        if config == configs[1]:
            os.chdir('llvm')
            llvm_patch = os.path.join(os.path.dirname(__file__), 'llvm.patch')
            util.git.patch(llvm_patch)

            os.chdir(workdir)

            os.chdir('llvm/tools/clang')
            clang_patch = os.path.join(os.path.dirname(__file__), 'clang.patch')
            util.git.patch(clang_patch)

            os.chdir(workdir)

            os.chdir('llvm/projects/compiler-rt')
            compilerrt_patch = os.path.join(os.path.dirname(__file__), 'compiler-rt.patch')
            util.git.patch(compilerrt_patch)

            os.chdir(workdir)

    if not os.path.exists('llvm-build'):
        os.mkdir('llvm-build')
        util.llvm.compile(src_dir=os.path.abspath('llvm'),
                          build_dir='llvm-build',
                          install_dir=os.getcwd())

    # Create spec config file
    print 'creating spec config file...'

    spec_cfg = '-'.join([command, config]) + '.cfg'

    os.chdir(workdir)

    if os.path.exists(spec_cfg):
        os.remove(spec_cfg)

    path = os.path.join('llvm-build', 'bin')

    cflags = []

    if config == configs[1]:
        cflags.append('-fsanitize=hextype')
        cflags.append('-mllvm -handle-reinterpret-cast')
        cflags.append('-mllvm -handle-placement-new')
        cflags.append('-mllvm -stack-opt')
        cflags.append('-mllvm -safestack-opt')
        cflags.append('-mllvm -cast-obj-opt')
        cflags.append('-mllvm -inline-opt')
        cflags.append('-mllvm -compile-time-verify-opt')
        cflags.append('-mllvm -enhance-dynamic-cast')

    cc = [os.path.abspath(os.path.join(path, 'clang'))]
    cc.extend(cflags)
    cxx = [os.path.abspath(os.path.join(path, 'clang++'))]
    cxx.extend(cflags)

    util.spec.create_config(dir=os.getcwd(), file=spec_cfg,
                            name='-'.join([command, config]),
                            cc=' '.join(cc), cxx=' '.join(cxx))

    # create shrc for testing
    print('creating test directory...')

    if not os.path.exists('test'):
        testdir = os.path.join(os.path.dirname(__file__), 'test')
        shutil.copytree(testdir, os.path.join(workdir, 'test'))

    if os.path.exists('test/shrc'):
        os.remove('test/shrc')

    util.test.create_shrc(
        dir=os.path.abspath('test'),
        cc=' '.join(cc), cxx=' '.join(cxx), ld=' '.join(cxx)
    )


def clean(config):
    workdir = '-'.join(['hextype', config])
    if not os.path.exists(workdir):
        print 'nothing to clean'
        return

    shutil.rmtree(workdir)


def run(config):
    if config.find('spec') > -1:
        print 'running ' + config + '...'
        spec_cfg = '-'.join([command, config]) + '.cfg'
        benchmarks = util.spec.cpp_benchmarks

        print 'running spec2006 cpu benchmark %s using %s...' % (', '.join(benchmarks), spec_cfg)

        util.spec.runspec(config=os.path.abspath(spec_cfg),
                          benchmarks=benchmarks)

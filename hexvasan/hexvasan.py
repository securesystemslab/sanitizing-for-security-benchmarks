import glob
import os
import shutil
import subprocess
import util


command = 'hexvasan'
configs = ['baseline-spec', 'spec']
repo = 'https://github.com/HexHive/HexVASAN.git'
llvm_commit = '4607999'
clang_commit = 'c3709e7'
compiler_rt_commit = '38631af'


def test(config):
    return True


def setup(config):
    workdir = os.getcwd()

    if not os.path.exists('llvm'):
        util.llvm.checkout(llvm_commit, clang_commit, compiler_rt_commit)

        if config == configs[1]:
            llvm_patch = os.path.join(os.path.dirname(__file__), 'llvm.patch')
            clang_patch = os.path.join(os.path.dirname(__file__), 'clang.patch')
            compilerrt_patch = os.path.join(os.path.dirname(__file__), 'compiler-rt.patch')

            os.chdir(os.path.join(workdir, 'llvm'))
            util.git.patch(llvm_patch)
            os.chdir(os.path.join(workdir, 'llvm/tools/clang'))
            util.git.patch(clang_patch)
            os.chdir(os.path.join(workdir, 'llvm/projects/compiler-rt'))
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

    if os.path.exists(spec_cfg):
        os.remove(spec_cfg)

    path = os.path.join('llvm-build', 'bin')

    cflags = list()
    if config == configs[1]:
        cflags = ['-fsanitize=vasan']

    cc = [os.path.abspath(os.path.join(path, 'clang'))]
    cc.extend(cflags)
    cxx = [os.path.abspath(os.path.join(path, 'clang++'))]
    cxx.extend(cflags)

    util.spec.create_config(dir=os.getcwd(), file=spec_cfg,
                            name='-'.join([command, config]),
                            cc=' '.join(cc), cxx=' '.join(cxx),
                            cld=' '.join(cxx))


def clean(config):
    workdir = '-'.join(['hexvasan', config])
    if not os.path.exists(workdir):
        print 'nothing to clean'
        return

    shutil.rmtree(workdir)


def run(config):
    if config.find('spec') > -1:
        print 'running ' + config + '...'

        spec_cfg = '-'.join([command, config]) + '.cfg'
        benchmarks = util.spec.all_benchmarks

        print 'running spec2006 cpu benchmark %s using %s...' % (', '.join(benchmarks), spec_cfg)

        util.spec.runspec(config=os.path.abspath(spec_cfg), benchmarks=benchmarks)

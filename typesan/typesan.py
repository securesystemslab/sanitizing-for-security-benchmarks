import glob
import os
import shutil
import util


command = 'typesan'
configs = ['baseline-spec-cpp', 'spec-cpp']
typesan_repo = 'https://github.com/vusec/typesan.git'
llvm_commit = '8f4f26c9c7fec12eb039be6b20313a51417c97bb'
clang_commit = 'd59a142ef50bf041797143db71d2d4777fd32d27'
compilerrt_commit = '961e78720a32929d7e4fc13a72d7266d59672c42'
gperftools_repo = 'https://github.com/gperftools/gperftools.git'
gperftools_commit = 'c46eb1f3d2f7a2bdc54a52ff7cf5e7392f5aa668'


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

    os.environ['LD_LIBRARY_PATH'] = os.path.join(cwd, 'lib') # tcmalloc
    util.make('test')

    os.chdir(cwd)


def setup(config):
    workdir = os.path.abspath(os.getcwd())

    if not os.path.exists('typesan'):
        util.git.clone(typesan_repo)

    if not os.path.exists('llvm'):
        util.llvm.checkout(llvm_commit, clang_commit, compilerrt_commit)

    if not os.path.exists('llvm-build'):
        os.mkdir('llvm-build')

        # Apply TypeSan patches
        if config == configs[1]:
            llvm_patch = os.path.join(os.path.dirname(__file__), 'llvm.patch')
            clang_patch = os.path.join(os.path.dirname(__file__), 'clang.patch')
            compilerrt_patch = os.path.join(os.path.dirname(__file__), 'compiler-rt.patch')

            os.chdir('llvm')
            util.git.patch(llvm_patch)
            os.chdir(os.path.join(workdir, 'llvm/tools/clang'))
            util.git.patch(clang_patch)
            os.chdir(os.path.join(workdir, 'llvm/projects/compiler-rt'))
            util.git.patch(compilerrt_patch)
            os.chdir(workdir)

        util.llvm.compile(src_dir=os.path.abspath('llvm'),
                          build_dir=os.path.abspath('llvm-build'),
                          install_dir=os.getcwd())

    if not glob.glob('gperftools*'):
        util.git.clone(gperftools_repo)
        os.chdir('gperftools')
        util.git.checkout(gperftools_commit)
        util.git.patch(os.path.join(os.path.dirname(__file__), 'GPERFTOOLS_SPEEDUP.patch'))

        if config == configs[1]:
            os.chdir(workdir)

            # Build metapagetable
            if not os.path.exists('gperftools-metalloc'):
                shutil.move('gperftools', 'gperftools-metalloc')

            if not os.path.exists('metapagetable'):
                config_fixedcompression = 'false'
                config_metadatabytes = 16
                config_deepmetadata = 'false'
                os.environ['METALLOC_OPTIONS'] = '-DFIXEDCOMPRESSION=%s -DMETADATABYTES=%d -DDEEPMETADATA=%s' % (config_fixedcompression, config_metadatabytes, config_deepmetadata)

                shutil.copytree(os.path.join('typesan', 'metapagetable'), 'metapagetable')
                os.chdir('metapagetable')
                util.make('config')
                util.make()
                os.chdir(workdir)

            # Apply TypeSan patches for gperftool
            os.chdir('gperftools-metalloc')
            util.git.patch(os.path.join(os.path.dirname(__file__), 'GPERFTOOLS_TYPESAN.patch'))

        util.run('autoreconf -fi')
        util.configure('--prefix=' + workdir)
        util.make()
        util.make('install')
        os.chdir(workdir)

    # Create spec config file
    print 'creating spec config file...'

    spec_cfg = '-'.join([command, config]) + '.cfg'

    if os.path.exists(spec_cfg):
        os.remove(spec_cfg)

    path = os.path.join('llvm-build', 'bin')

    cflags = []
    extra_libs = []
    if config == configs[1]:
        cflags = ['-fsanitize=typesan']

    extra_libs.extend(['-ltcmalloc', '-lpthread', '-lunwind'])
    extra_libs.append('-L' + os.path.join(workdir, 'lib')) # tcmalloc

    cc = [os.path.abspath(os.path.join(path, 'clang'))]
    cc.extend(cflags)
    cxx = [os.path.abspath(os.path.join(path, 'clang++'))]
    cxx.extend(cflags)

    util.spec.create_config(dir=os.getcwd(), file=spec_cfg,
                            name='-'.join([command, config]),
                            cc=' '.join(cc), cxx=' '.join(cxx),
                            extra_libs=' '.join(extra_libs))

    # create shrc for testing
    print('creating test directory...')

    if not os.path.exists('test'):
        testdir = os.path.join(os.path.dirname(__file__), 'test')
        shutil.copytree(testdir, os.path.join(workdir, 'test'))

    if os.path.exists('test/shrc'):
        os.remove('test/shrc')

    util.test.create_shrc(
        dir=os.path.abspath('test'),
        cc=' '.join(cc), cxx=' '.join(cxx), ld=' '.join(cxx),
        ldflags=' '.join(extra_libs)
    )


def clean(config):
    workdir = '-'.join([command, config])
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

        os.environ['LD_LIBRARY_PATH'] = os.path.join(os.getcwd(), 'lib') # tcmalloc
        util.spec.runspec(config=os.path.abspath(spec_cfg),
                          benchmarks=benchmarks)

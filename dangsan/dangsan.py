import glob
import os
import shutil
import subprocess
import util


command = 'dangsan'
configs = ['baseline-spec', 'spec', 'spec-debug']
dangsan_repo = 'https://github.com/vusec/dangsan.git'
llvm_svn_commit = '251286'
binutils_tarball_format = 'binutils-VERSION.tar.bz2'
binutils_url_format = 'http://ftp.gnu.org/gnu/binutils/TARBALL'
binutils_version = '2.26.1'
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

    util.make()

    os.environ['LD_LIBRARY_PATH'] = os.path.join(cwd, 'lib')
    util.make('test')

    os.chdir(cwd)


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


def setup(config):
    workdir = os.path.abspath(os.getcwd())

    if not os.path.exists('dangsan'):
        util.git.clone(dangsan_repo)

    if not os.path.exists('llvm-svn'):
        util.llvm.checkout_svn(llvm_svn_commit)
        os.chdir('llvm-svn')
        util.patch(os.path.join(workdir, 'dangsan', 'patches', 'LLVM-gold-plugins-3.8.diff'), '-p0')
        util.patch(os.path.join(workdir, 'dangsan', 'patches', 'LLVM-safestack-3.8.diff'), '-p0')
        os.chdir('projects/compiler-rt')
        util.patch(os.path.join(workdir, 'dangsan', 'patches', 'COMPILERRT-safestack-3.8.diff'), '-p0')
        os.chdir(workdir)

    if not os.path.exists('bin/ld'):
        prepare_gold(binutils_version)
        os.remove('bin/ld')
        shutil.copy('bin/ld.gold', 'bin/ld')

    if not os.path.exists('llvm-build'):
        os.mkdir('llvm-build')
        util.llvm.compile(src_dir=os.path.abspath('llvm-svn'),
                          build_dir=os.path.abspath('llvm-build'),
                          install_dir=os.getcwd(),
                          options=['-DLLVM_BINUTILS_INCDIR=%s/include' % workdir])
        util.llvm.install(os.path.abspath('llvm-build'))

    if not glob.glob('gperftools*'):
        util.git.clone(gperftools_repo)
        os.chdir('gperftools')
        util.git.checkout(gperftools_commit)

        # gperftools patch for both baseline and DangSan
        util.git.patch(os.path.join(workdir, 'dangsan', 'patches', 'GPERFTOOLS_SPEEDUP.patch'))

        if config == configs[1] or config == configs[2]:
            os.chdir(workdir)

            # Build metapagetable
            if not os.path.exists('gperftools-metalloc'):
                shutil.move('gperftools', 'gperftools-metalloc')

            if not os.path.exists('metapagetable'):
                config_fixedcompression = 'false'
                config_metadatabytes = 8
                config_deepmetadata = 'false'
                config_alloc_size_hook = 'dang_alloc_size_hook'
                metalloc_options = []
                metalloc_options.append('-DFIXEDCOMPRESSION=%s' % config_fixedcompression)
                metalloc_options.append('-DMETADATABYTES=%d' % config_metadatabytes)
                metalloc_options.append('-DDEEPMETADATA=%s' % config_deepmetadata)
                metalloc_options.append('-DALLOC_SIZE_HOOK=%s' % config_alloc_size_hook)
                os.environ['METALLOC_OPTIONS'] = ' '.join(metalloc_options)

                shutil.copytree(os.path.join('dangsan', 'metapagetable'), 'metapagetable')
                os.chdir('metapagetable')
                util.make('config')
                util.make()
                os.chdir(workdir)

            # Apply DanSan patches for gperftool
            os.chdir('gperftools-metalloc')
            util.git.patch(os.path.join(os.path.dirname(__file__), 'GPERFTOOLS_DANGSAN.patch'))

        util.run('autoreconf -fi')
        util.configure('--prefix=%s' % workdir)
        util.make('-j4')
        util.make('install')
        os.chdir(workdir)

    # build llvm-plugins
    llvmplugins_dir = os.path.join(workdir, 'llvm-plugins')
    libplugins_so = os.path.join(llvmplugins_dir, 'libplugins.so')
    if config == configs[1] or config == configs[2]:
        if not os.path.exists('staticlib'):
            os.environ['PATH'] = ':'.join([os.path.join(workdir, 'bin'), os.environ['PATH']])
            shutil.copytree('dangsan/staticlib', 'staticlib')
            os.chdir('staticlib')
            util.make('METAPAGETABLEDIR=%s' % os.path.join(workdir, 'metapagetable', 'obj'))
            os.chdir(workdir)

        if not os.path.exists(libplugins_so):
            os.environ['PATH'] = ':'.join([os.path.join(workdir, 'bin'), os.environ['PATH']])
            os.chdir('dangsan/llvm-plugins')
            util.make('-j4 GOLDINSTDIR=%s TARGETDIR=%s' % (workdir, llvmplugins_dir))
            os.chdir(workdir)

    # Create spec config file
    print 'creating spec config file...'

    spec_cfg = '-'.join([command, config]) + '.cfg'

    if os.path.exists(spec_cfg):
        os.remove(spec_cfg)

    cflags = ['-flto']
    cxxflags = ['-flto']
    ldflags = []
    if config == configs[1] or config == configs[2]:
        cflags.append('-fsanitize=safe-stack')
        cxxflags.append('-fsanitize=safe-stack')
        cxxflags.append('-DSOPLEX_DANGSAN_MASK')
        ldflags.append('-Wl,-plugin-opt=-load=%s' % libplugins_so)
        ldflags.append('-Wl,-plugin-opt=%s' % '-largestack=false')
        # ldflags.append('-Wl,-plugin-opt=%s' % '-stats') # option not found
        ldflags.append('-Wl,-plugin-opt=%s' % '-mergedstack=false')
        ldflags.append('-Wl,-plugin-opt=%s' % '-stacktracker')
        ldflags.append('-Wl,-plugin-opt=%s' % '-globaltracker')
        ldflags.append('-Wl,-plugin-opt=%s' % '-pointertracker')
        ldflags.append('-Wl,-plugin-opt=%s' % '-FreeSentryLoop')
        ldflags.append('-Wl,-plugin-opt=%s' % '-custominline')
        ldflags.append('-Wl,-whole-archive,-l:libmetadata.a,-no-whole-archive') # staticlib
        ldflags.append('@%s' % os.path.join(workdir, 'metapagetable', 'obj', 'linker-options'))

    extra_libs = ['-ltcmalloc', '-lpthread', '-lunwind']
    extra_libs.append('-L%s' % os.path.join(workdir, 'lib'))
    if config == configs[1] or config == configs[2]:
        extra_libs.append('-ldl')
        extra_libs.append('-L%s' % os.path.join(workdir, 'staticlib', 'obj'))

    if config == configs[2]:
        cflags.append('-g')
        cxxflags.append('-g')

    cc = [os.path.abspath(os.path.join(workdir, 'bin', 'clang'))]
    cc.extend(cflags)
    cxx = [os.path.abspath(os.path.join(workdir, 'bin', 'clang++'))]
    cxx.extend(cxxflags)
    cld = list(cc)
    cld.extend(ldflags)
    cxxld = list(cxx)
    cxxld.extend(ldflags)

    util.spec.create_config(dir=os.getcwd(), file=spec_cfg,
                            name='-'.join([command, config]),
                            cc=' '.join(cc), cxx=' '.join(cxx),
                            cld=' '.join(cld), cxxld=' '.join(cxxld),
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
        cc=' '.join(cc), cxx=' '.join(cxx), ld=' '.join(cld),
        ldflags=' '.join(extra_libs)
    )


def clean(config):
    workdir = '-'.join(['dangsan', config])
    if not os.path.exists(workdir):
        print 'nothing to clean'
        return

    shutil.rmtree(workdir)


def run(config):
    if config.find('spec') > -1:
        print 'running ' + config + '...'
        spec_cfg = '-'.join([command, config]) + '.cfg'
        benchmarks = util.spec.all_benchmarks

        if config == configs[1] or config == configs[2]:
            os.environ['SAFESTACK_OPTIONS'] = '"largestack=true"'

        print 'running spec2006 cpu benchmark %s using %s...' % (', '.join(benchmarks), spec_cfg)

        os.environ['LD_LIBRARY_PATH'] = os.path.join(os.getcwd(), 'lib')
        util.spec.runspec(config=os.path.abspath(spec_cfg),
                          benchmarks=benchmarks)

import os
import shutil
import subprocess
import util


command = 'lowfat'
configs = ['baseline-spec', 'spec', 'spec-debug', 'spec-noabort']
repo = 'https://github.com/GJDuck/LowFat.git'
llvmver = '4.0.0'


def test(config):
    return True


def setup(config):
    workdir = os.path.abspath(os.getcwd())
    configdir = os.path.join(os.path.dirname(__file__), 'config')
    INSTRUMENTATION_PATH = os.path.abspath('llvm/lib/Transforms/Instrumentation')

    if not os.path.exists('llvm'):
        util.llvm.download(llvmver, os.getcwd())

        # Apply patches common to both baseline and LowFat
        bug81066_patch = os.path.join(os.path.dirname(__file__), 'bug81066.patch')
        os.chdir('llvm/projects/compiler-rt')
        util.patch(os.path.abspath(bug81066_patch), '-p0')
        os.chdir(workdir)

    if not os.path.exists('llvm-4.0.0') and not os.path.exists('llvm-lowfat'):
        os.mkdir('llvm-4.0.0')
        util.llvm.compile(src_dir=os.path.abspath('llvm'),
                          build_dir=os.path.abspath('llvm-4.0.0'),
                          install_dir=workdir)

    if config != configs[0]:
        os.environ['CC'] = os.path.abspath('llvm-4.0.0/bin/clang')
        os.environ['CXX'] = os.path.abspath('llvm-4.0.0/bin/clang++')

        if not os.path.exists('llvm-lowfat'):
            print 'patching llvm/clang/compiler-rt version ' + llvmver + '...'

            llvm_patch = os.path.join(os.path.dirname(__file__), 'llvm.patch')
            clang_patch = os.path.join(os.path.dirname(__file__), 'clang.patch')
            compilerrt_patch = os.path.join(os.path.dirname(__file__), 'compiler-rt.patch')

            legacy_compilerrt_patch = os.path.join(os.path.dirname(__file__), 'legacy_compiler-rt.patch')
            modern_compilerrt_patch = os.path.join(os.path.dirname(__file__), 'modern_compiler-rt.patch')

            os.chdir('llvm')
            util.patch(os.path.abspath(llvm_patch))
            os.chdir(workdir)

            os.chdir('llvm/tools/clang')
            util.patch(os.path.abspath(clang_patch))
            os.chdir(workdir)

            os.chdir('llvm/projects/compiler-rt')
            util.patch(os.path.abspath(compilerrt_patch))

            cpuinfo = util.stdout(['cat', '/proc/cpuinfo']).strip().split('\n')

            legacy = False

            if not [s for s in cpuinfo if ' bmi1' in s]:
                legacy = True

            if not [s for s in cpuinfo if ' bmi2' in s]:
                legacy = True

            if not [s for s in cpuinfo if ' abm' in s]:
                legacy = True

            if legacy:
                util.patch(os.path.abspath(legacy_compilerrt_patch))
            else:
                util.patch(os.path.abspath(modern_compilerrt_patch))

            os.chdir(workdir)

            print 'building the LowFat config builder...'

            CONFIG = 'sizes.cfg 32'
            os.chdir(os.path.join(os.path.dirname(__file__), 'config'))
            util.make()
            util.run('./lowfat-config ' + CONFIG)
            util.make('lowfat-check-config')
            util.run('./lowfat-check-config')
            os.chdir(workdir)

            print 'copying the LowFat config files...'

            RUNTIME_PATH = os.path.abspath('llvm/projects/compiler-rt/lib/lowfat')
            shutil.copy(os.path.join(configdir, 'lowfat_config.h'), RUNTIME_PATH)
            shutil.copy(os.path.join(configdir, 'lowfat_config.c'), RUNTIME_PATH)

            CLANGLIB_PATH = os.path.abspath('llvm/tools/clang/lib/Basic')
            shutil.copy(os.path.join(RUNTIME_PATH, 'lowfat_config.c'),
                        os.path.join(INSTRUMENTATION_PATH, 'lowfat_config.inc'))
            shutil.copy(os.path.join(RUNTIME_PATH, 'lowfat_config.h'),
                        os.path.join(INSTRUMENTATION_PATH, 'lowfat_config.h'))
            shutil.copy(os.path.join(RUNTIME_PATH, 'lowfat_config.h'),
                        os.path.join(CLANGLIB_PATH, 'lowfat_config.h'))
            shutil.copy(os.path.join(RUNTIME_PATH, 'lowfat.h'),
                        os.path.join(INSTRUMENTATION_PATH, 'lowfat.h'))

            os.mkdir('llvm-lowfat')

            util.llvm.compile(src_dir=os.path.abspath('llvm'),
                              build_dir=os.path.abspath('llvm-lowfat'),
                              install_dir=workdir)

        os.chdir('llvm-lowfat')

        if not os.path.exists('lib/LowFat'):
            if not os.path.exists('lib'):
                os.mkdir('lib')
            os.mkdir('lib/LowFat')
            shutil.copy(os.path.join(configdir, 'lowfat.ld'),
                        os.path.join('lib/LowFat', 'lowfat.ld'))

        if not os.path.exists('bin/lowfat-ptr-info'):
            os.chdir(configdir)
            util.make('lowfat-ptr-info')
            shutil.copy('lowfat-ptr-info', os.path.join(workdir, 'llvm-lowfat', 'bin'))

        os.chdir(workdir)

        if not os.path.exists('LowFat.so'):
            clangxx = os.path.join('llvm-4.0.0', 'bin', 'clang++')
            llvm_config = os.path.join('llvm-4.0.0', 'bin', 'llvm-config')

            cxxflags = util.stdout([llvm_config, '--cxxflags']).rstrip('\n')
            includedir = util.stdout([llvm_config, '--includedir']).rstrip('\n')
            cmd = ' '.join([clangxx, '-DLOWFAT_PLUGIN',
                            os.path.join(INSTRUMENTATION_PATH, 'LowFat.cpp'),
                            '-c -Wall -O2',
                            '-I' + INSTRUMENTATION_PATH,
                            '-o LowFat.o',
                            cxxflags, includedir])
            util.run(cmd)

            ldflags = util.stdout([llvm_config, '--ldflags']).rstrip('\n')
            cmd = ' '.join([clangxx, '-shared -rdynamic -o LowFat.so LowFat.o', ldflags])
            util.run(cmd)

        os.chdir(workdir)

    # Create spec config file
    print 'creating spec config file...'

    spec_cfg = '-'.join([command, config]) + '.cfg'

    if os.path.exists(spec_cfg):
        os.remove(spec_cfg)

    if config == configs[0]:
        path = os.path.join('llvm-4.0.0', 'bin')
        cflags = []
    else:
        path = os.path.join('llvm-lowfat', 'bin')
        cflags = ['-fsanitize=lowfat']
        blacklist = os.path.join(os.path.dirname(__file__), 'blacklist.txt')
        cflags.extend(['-mllvm', '-lowfat-no-check-blacklist=%s' % blacklist])

    cflags.append('-DPATCH_PERLBENCH_OVERFLOW')
    cflags.append('-DPATCH_H264REF_OVERFLOW')

    if config == configs[2]:
        cflags.append('-g')
        cflags.append('-fno-inline-functions')

    if config == configs[3]:
        cflags.append('-mllvm -lowfat-no-abort')

    cc = [os.path.abspath(os.path.join(path, 'clang'))]
    cc.extend(cflags)
    cxx = [os.path.abspath(os.path.join(path, 'clang++'))]
    cxx.extend(cflags)

    util.spec.create_config(dir=os.getcwd(), file=spec_cfg,
                            name='-'.join([command, config]),
                            cc=' '.join(cc), cxx=' '.join(cxx))


def clean(config):
    workdir = '-'.join(['lowfat', config])
    if not os.path.exists(workdir):
        print 'nothing to clean'
        return

    shutil.rmtree(workdir)


def run(config):
    if config.find('spec') > -1:
        print 'running ' + config + '...'
        spec_cfg = '-'.join([command, config]) + '.cfg'
        benchmarks = util.spec.all_benchmarks

        if config == configs[2] or config == configs[3]:
            benchmarks = ['400', '403', '464', '444', '450']

        print 'running spec2006 cpu benchmark %s using %s...' % (', '.join(benchmarks), spec_cfg)

        util.spec.runspec(config=os.path.abspath(spec_cfg),
                          benchmarks=benchmarks)

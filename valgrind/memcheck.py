import os
import util
import clang
import valgrind


command = 'memcheck'
configs = ['baseline-spec', 'spec']
llvmver = '6.0.0'


def setup(config):
    workdir = os.path.abspath(os.getcwd())

    if not os.path.exists('llvm'):
        util.llvm.download(llvmver, os.getcwd())

    if not os.path.exists('llvm-' + llvmver):
        os.mkdir('llvm-' + llvmver)
        util.llvm.compile(src_dir=os.path.abspath('llvm'),
                          build_dir=os.path.abspath('llvm-' + llvmver),
                          install_dir=workdir)

    if config == configs[1]:
        if not os.path.exists('valgrind'):
            valgrind.download(os.path.abspath('valgrind'))

            if os.path.exists(os.path.join('bin', 'valgrind')):
                print('valgrind exists. skipping installation...')
            else:
                os.chdir('valgrind')
                util.configure('--prefix=' + workdir)
                util.make()
                util.make('install')
                os.chdir(workdir)

    # Create spec config file
    print 'creating spec config file...'

    spec_cfg = '-'.join([command, config]) + '.cfg'

    if os.path.exists(spec_cfg):
        os.remove(spec_cfg)

    cflags = list()

    valgrind_path = os.path.abspath(os.path.join('bin', 'valgrind'))
    spec_wrapper = ''
    if config == configs[1]:
        spec_wrapper = valgrind_path + ' --tool=memcheck'

    llvm_bin_path = os.path.join(workdir, 'llvm-' + llvmver, 'bin')

    cc = [os.path.join(llvm_bin_path, 'clang')]
    cc.extend(cflags)
    cxx = [os.path.join(llvm_bin_path, 'clang++')]
    cxx.extend(cflags)

    util.spec.create_config(dir=os.getcwd(), file=spec_cfg,
                            name='-'.join([command, config]),
                            cc=' '.join(cc), cxx=' '.join(cxx),
                            cld=' '.join(cxx),
                            spec_wrapper=spec_wrapper,
                            cxxportability=clang.common.cxxportability)


def run(config):
    if config.find('spec') > -1:
        print 'running ' + config + '...'

        spec_cfg = '-'.join([command, config]) + '.cfg'
        benchmarks = util.spec.all_benchmarks
        benchmarks.remove('447.dealII') # takes too long time (more than 49 hours)

        print 'running spec2006 cpu benchmark %s using %s...' % (', '.join(benchmarks), spec_cfg)

        util.spec.runspec(config=os.path.abspath(spec_cfg),
                          benchmarks=benchmarks)

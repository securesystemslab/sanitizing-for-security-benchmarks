import os
import shutil
import util


llvmver = '6.0.0'
llvmdir = '-'.join(['llvm', llvmver])
cxxportability = {
    '473.astar': '-Wno-reserved-user-defined-literal',
    '483.xalancbmk': '-Wno-c++11-narrowing',
    '447.dealII': '-std=gnu++98',
    '450.soplex': '-std=gnu++98'
}

def setup(config, compile_flags=[]):
    workdir = os.getcwd()

    if not os.path.exists('llvm'):
        util.llvm.download(llvmver, os.getcwd())

    if not os.path.exists('llvm-' + llvmver):
        os.mkdir('llvm-' + llvmver)
        util.llvm.compile(src_dir=os.path.abspath('llvm'),
                          build_dir=os.path.abspath('llvm-' + llvmver),
                          install_dir=workdir,
                          options=compile_flags)


def clean(config):
    if not os.path.exists(llvmdir):
        print 'nothing to clean'
        return

    shutil.rmtree(llvmdir)


def run(command, config, benchmarks=['int']):
    if config.find('spec') > -1:
        print 'running ' + config + '...'

        spec_cfg = '-'.join([command, config]) + '.cfg'

        print 'running spec2006 cpu benchmark %s using %s...' % (', '.join(benchmarks), spec_cfg)

        util.spec.runspec(config=os.path.abspath(spec_cfg),
                          benchmarks=benchmarks)

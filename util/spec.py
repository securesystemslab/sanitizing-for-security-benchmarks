import os
import subprocess


default_cfg = """
monitor_wrapper = $SPEC_WRAPPER $command
monitor_specrun_wrapper = $SPECRUN_WRAPPER $command
ignore_errors = yes
tune          = base
ext           = $name
output_format = asc, Screen
output_root = $OUTPUT_ROOT
reportable    = 1
teeout        = yes
teerunout     = yes
strict_rundir_verify = 0
makeflags = -j$SPEC_J
default=default=default=default:
CC  = $CC
CXX = $CXX
CLD = $CLD
CXXLD = $CXXLD
EXTRA_LIBS = $EXTRA_LIBS
EXTRA_CXXLIBS = $EXTRA_CXXLIBS
FC         = echo

default=base=default=default:
COPTIMIZE   = $OPT_LEVEL
CXXOPTIMIZE = $OPT_LEVEL

default=base=default=default:
PORTABILITY = -DSPEC_CPU_LP64

400.perlbench=default=default=default:
CPORTABILITY= -DSPEC_CPU_LINUX_X64
EXTRA_CFLAGS= -std=gnu89

462.libquantum=default=default=default:
CPORTABILITY = -DSPEC_CPU_LINUX

483.xalancbmk=default=default=default:
CXXPORTABILITY = -DSPEC_CPU_LINUX

481.wrf=default=default=default:
CPORTABILITY   = -DSPEC_CPU_CASE_FLAG -DSPEC_CPU_LINUX
"""


int_benchmarks = ['400.perlbench',
                  '401.bzip2',
                  '403.gcc',
                  '429.mcf',
                  '445.gobmk',
                  '456.hmmer',
                  '458.sjeng',
                  '462.libquantum',
                  '464.h264ref',
                  '471.omnetpp',
                  '473.astar',
                  '483.xalancbmk']
fp_benchmarks = ['433.milc',
                 '444.namd',
                 '447.dealII',
                 '450.soplex',
                 '453.povray',
                 '470.lbm',
                 '482.sphinx3']
cpp_benchmarks = ['471.omnetpp',
                  '473.astar',
                  '483.xalancbmk',
                  '444.namd',
                  '447.dealII',
                  '450.soplex',
                  '453.povray']
all_benchmarks = int_benchmarks + fp_benchmarks


# SPEC CPU2006 support only
def install(mountdir, installdir):
    if not os.path.exists(mountdir):
        raise Exception('mount dir does not exist')

    print 'installing SPEC CPU2006...'

    cwd = os.getcwd()
    os.mkdir(installdir)
    os.chdir(mountdir)

    subprocess.check_output(['./install.sh'])

    os.chdir(cwd)


def create_config(dir,
                  file,
                  name,
                  cc,
                  cxx,
                  cld='',
                  cxxld='',
                  opt_level='-O2 -fno-strict-aliasing',
                  extra_libs='',
                  extra_cxxlibs='',
                  spec_wrapper='',
                  cxxportability={}):
    if not os.path.exists(dir):
        raise Exception('config dir does not exist')

    if os.path.exists(file):
        raise Exception('config file already exists')

    if cld == '':
        cld = cc

    if cxxld == '':
        cxxld = cxx

    cfg = default_cfg
    cfg = cfg.replace('$name', name)
    cfg = cfg.replace('$CLD', cld)
    cfg = cfg.replace('$CC', cc)
    cfg = cfg.replace('$CXXLD', cxxld)
    cfg = cfg.replace('$CXX', cxx)
    cfg = cfg.replace('$SPEC_J', '4')  # TODO
    cfg = cfg.replace('$OPT_LEVEL', opt_level)
    cfg = cfg.replace('$EXTRA_LIBS', extra_libs)
    cfg = cfg.replace('$EXTRA_CXXLIBS', extra_cxxlibs)
    cfg = cfg.replace('$SPEC_WRAPPER', spec_wrapper)
    cfg = cfg.replace('$SPECRUN_WRAPPER', '')
    cfg = cfg.replace('$OUTPUT_ROOT', dir)

    for bench in cxxportability.keys():
        if not bench in all_benchmarks:
            raise Exception('%s not found' % bench)

        section_header = '%s=default=default=default:' % bench
        lines = cfg.split('\n')

        if section_header in lines:
            idx = lines.index(section_header)
            for i in range(idx + 1, len(lines) - 1):
                if lines[i].startswith('CXXPORTABILITY'):
                    lines[i] += ' %s' % cxxportability[bench]
                    cfg = '\n'.join(lines)
                    break
                if lines[idx] == '':
                    new_cxxport = ('CXXPORTABILITY = %s' % cxxportability[bench])
                    lines.insert(idx, new_cxxport + '\n')
                    cfg = '\n'.join(lines)
                    break
        else:
            new_section = [section_header]
            new_section.append('CXXPORTABILITY = %s' % cxxportability[bench])
            cfg += '\n' + '\n'.join(new_section) + '\n'

    if cfg.replace('$command', '').find('$') > -1:
        raise Exception('config incomplete %s' % cfg)

    try:
        cfg_file = open(os.path.join(dir, file), 'w')
        cfg_file.write(cfg)
    finally:
        print os.path.abspath(cfg_file.name)
        cfg_file.close()


def runspec(config, benchmarks, action='run', size='ref', iterations=3):

    assert os.path.exists(config), 'config does not exist'

    action = action.lower()

    assert action in ['build', 'clean', 'run'], 'invalid action'

    size = size.lower()

    assert size in ['test', 'train', 'ref'], 'invalid size'

    pathspec = os.getenv('SPEC')
    if not pathspec:
        raise Exception('SPEC not found')
    if not os.path.exists(pathspec):
        raise Exception('SPEC dir does not exist: ' + pathspec)

    os.chdir(pathspec)

    cmd = ['runspec']
    cmd.extend(['--config', config])
    cmd.extend(['--action', action])
    cmd.extend(['--size', size])
    cmd.extend(['--iterations', str(iterations)])
    cmd.extend(['--ignore_errors', '--loose'])
    cmd.extend(benchmarks)

    print ' '.join(cmd)
    p = subprocess.Popen(' '.join(cmd), shell=True)
    p.wait()


import glob
import os


def create_shrc(dir, cc, cxx, ld, cflags='', cxxflags='', ldflags=''):
    cwd = os.getcwd()
    os.chdir(dir)

    lines = []
    lines.append('export CC="%s"' % cc)
    lines.append('export CXX="%s"' % cxx)
    lines.append('export LD="%s"' % ld)
    lines.append('export CFLAGS="%s"' % cflags)
    lines.append('export CXXFLAGS="%s"' % cxxflags)
    lines.append('export LDFLAGS="%s"' % ldflags)

    try:
        shrc = open(os.path.join(dir, 'shrc'), 'w')
        shrc.write('\n'.join(lines))
    finally:
        print os.path.abspath(shrc.name)
        shrc.close()

    os.chdir(cwd)

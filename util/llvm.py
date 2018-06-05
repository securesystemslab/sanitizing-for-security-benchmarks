import os
import shutil
import subprocess
import git
import svn


MAX_CPU_CORES = 10


llvm_url_format = 'http://releases.llvm.org/VERSION/llvm-VERSION.EXT'
clang_url_format = 'http://releases.llvm.org/VERSION/cfe-VERSION.EXT'
compilerrt_url_format = 'http://releases.llvm.org/VERSION/compiler-rt-VERSION.EXT'
libcxx_url_format = 'http://releases.llvm.org/6.0.0/libcxx-VERSION.EXT'
libcxxabi_url_format = 'http://releases.llvm.org/6.0.0/libcxxabi-VERSION.EXT'

llvm_git_repo = 'https://git.llvm.org/git/llvm.git'
clang_git_repo = 'https://git.llvm.org/git/clang.git'
compilerrt_git_repo = 'https://git.llvm.org/git/compiler-rt.git'

llvm_svn_repo = 'http://llvm.org/svn/llvm-project/llvm/trunk'
clang_svn_repo = 'http://llvm.org/svn/llvm-project/cfe/trunk'
compilerrt_svn_repo = 'http://llvm.org/svn/llvm-project/compiler-rt/trunk'


def checkout(llvm_commit, clang_commit, compilerrt_commit):
    cwd = os.path.abspath(os.getcwd())

    if not os.path.exists('llvm'):
        git.clone(llvm_git_repo, ['-n'])
    os.chdir('llvm')
    git.checkout(llvm_commit)

    os.chdir(os.path.join(cwd, 'llvm', 'tools'))
    if not os.path.exists('clang'):
        git.clone(clang_git_repo, ['-n'])
    os.chdir('clang')
    git.checkout(clang_commit)

    os.chdir(os.path.join(cwd, 'llvm', 'projects'))
    if not os.path.exists('compiler-rt'):
        git.clone(compilerrt_git_repo, ['-n'])
    os.chdir('compiler-rt')
    git.checkout(compilerrt_commit)

    os.chdir(cwd)


def checkout_svn(llvm_rev=''):
    svn.checkout(llvm_rev, llvm_svn_repo, 'llvm-svn')
    svn.checkout(llvm_rev, clang_svn_repo, os.path.join('llvm-svn', 'tools', 'clang'))
    svn.checkout(llvm_rev, compilerrt_svn_repo, os.path.join('llvm-svn', 'projects', 'compiler-rt'))


def download(version, dir):
    if not os.path.exists(dir):
        raise Exception('target directory does not exist')

    ver_major = int(version.split('.')[0])
    ver_minor = int(version.split('.')[1])

    cwd = os.getcwd()
    os.chdir(dir)

    file_ext = 'src.tar.xz'
    if ver_major <= 3 and ver_minor <= 5:
        file_ext = 'src.tar.gz'

    print 'downloading llvm ' + version + '...'
    url = llvm_url_format.replace('VERSION', version).replace('EXT', file_ext)
    tar_file = '.'.join(['llvm-' + version, file_ext])
    if not os.path.exists(tar_file):
        subprocess.check_output(['wget', url])
    if not os.path.exists('llvm'):
        subprocess.check_output(['tar', '-xvf', tar_file])
        if ver_major <= 3 and ver_minor <= 5:
            shutil.move('llvm-' + version, 'llvm-' + version + '.src')
        shutil.move('llvm-' + version + '.src', 'llvm')

    print 'downloading clang ' + version + '...'
    url = clang_url_format.replace('VERSION', version).replace('EXT', file_ext)
    tar_file = '.'.join(['cfe-' + version, file_ext])
    if ver_major <= 3 and ver_minor <= 5:
        url = url.replace('cfe', 'clang')
        tar_file = '.'.join(['clang-' + version, file_ext])
    if not os.path.exists(tar_file):
        subprocess.check_output(['wget', url])
    if not os.path.exists(os.path.join('llvm', 'tools', 'clang')):
        subprocess.check_output(['tar', '-xvf', tar_file])
        if ver_major <= 3 and ver_minor <= 5:
            shutil.move('clang-' + version, 'cfe-' + version + '.src')
        shutil.move('cfe-' + version + '.src', os.path.join('llvm', 'tools', 'clang'))

    print 'downloading compiler-rt ' + version + '...'
    url = compilerrt_url_format.replace('VERSION', version).replace('EXT', file_ext)
    tar_file = '.'.join(['compiler-rt-' + version, file_ext])
    if not os.path.exists(tar_file):
        subprocess.check_output(['wget', url])
    if not os.path.exists(os.path.join('llvm', 'projects', 'compiler-rt')):
        subprocess.check_output(['tar', '-xvf', tar_file])
        if ver_major <= 3 and ver_minor <= 5:
            shutil.move('compiler-rt-' + version, 'compiler-rt-' + version + '.src')
        shutil.move('compiler-rt-' + version + '.src', os.path.join('llvm', 'projects', 'compiler-rt'))

    os.chdir(cwd)


def download_libcxx(version, libcxx, libcxxabi):
    if not os.path.exists('llvm'):
        raise Exception('llvm does not exist')

    ver_major = int(version.split('.')[0])
    ver_minor = int(version.split('.')[1])

    cwd = os.path.abspath(os.getcwd())

    file_ext = 'src.tar.xz'
    if ver_major <= 3 and ver_minor <= 5:
        file_ext = 'src.tar.gz'

    if libcxx:
        print 'downloading libcxx ' + version + '...'
        url = libcxx_url_format.replace('VERSION', version).replace('EXT', file_ext)
        tar_file = '.'.join(['libcxx-' + version, file_ext])
        if not os.path.exists(tar_file):
            subprocess.check_output(['wget', url])
        if not os.path.exists(os.path.join('llvm', 'projects', 'libcxx')):
            subprocess.check_output(['tar', '-xvf', tar_file])
            if ver_major <= 3 and ver_minor <= 5:
                shutil.move('libcxx-' + version, 'libcxx-' + version + '.src')
            shutil.move('libcxx-' + version + '.src', os.path.join('llvm', 'projects', 'libcxx'))

    if libcxxabi:
        print 'downloading libcxxabi ' + version + '...'
        url = libcxxabi_url_format.replace('VERSION', version).replace('EXT', file_ext)
        tar_file = '.'.join(['libcxxabi-' + version, file_ext])
        if not os.path.exists(tar_file):
            subprocess.check_output(['wget', url])
        if not os.path.exists(os.path.join('llvm', 'projects', 'libcxxabi')):
            subprocess.check_output(['tar', '-xvf', tar_file])
            if ver_major <= 3 and ver_minor <= 5:
                shutil.move('libcxxabi-' + version, 'libcxxabi-' + version + '.src')
            shutil.move('libcxxabi-' + version + '.src', os.path.join('llvm', 'projects', 'libcxxabi'))

    os.chdir(cwd)


def compile(src_dir, build_dir, install_dir, options=[], ninja=True):
    if not build_dir or not os.path.exists(build_dir):
        raise Exception('build dir does not exist')

    cwd = os.getcwd()
    os.chdir(build_dir)

    if not src_dir or not os.path.exists(src_dir):
        raise Exception('llvm does not exist')

    if not install_dir or not os.path.exists(install_dir):
        raise Exception('install dir does not exist')

    print 'compiling llvm...'

    gen_build_cmd = ['cmake']
    if ninja:
        gen_build_cmd.append('-GNinja')
    gen_build_cmd.append(src_dir)
    gen_build_cmd.append('-DCMAKE_INSTALL_PREFIX=' + install_dir)
    gen_build_cmd.append('-DCMAKE_BUILD_TYPE=Release')
    gen_build_cmd.append('-DLLVM_TARGETS_TO_BUILD=X86')
    gen_build_cmd.extend(options)
    p = subprocess.Popen(' '.join(gen_build_cmd), shell=True)
    p.wait()

    build_cmd = []
    if ninja:
        build_cmd.append('ninja -j%d' % MAX_CPU_CORES)
    else:
        build_cmd.append('make -j%d' % MAX_CPU_CORES)

    p = subprocess.Popen(' '.join(build_cmd), shell=True)
    p.wait()

    os.chdir(cwd)


def compile_libcxx(src_dir, build_dir, install_dir, options=[], ninja=True):
    if not build_dir or not os.path.exists(build_dir):
        raise Exception('build dir does not exist')

    cwd = os.getcwd()
    os.chdir(build_dir)

    if not src_dir or not os.path.exists(src_dir):
        raise Exception('llvm does not exist')

    if not install_dir or not os.path.exists(install_dir):
        raise Exception('install dir does not exist')

    print 'compiling libcxx/libcxxabi...'

    gen_build_cmd = ['cmake']
    if ninja:
        gen_build_cmd.append('-GNinja')
    gen_build_cmd.append(src_dir)
    gen_build_cmd.append('-DCMAKE_INSTALL_PREFIX=' + install_dir)
    gen_build_cmd.append('-DCMAKE_BUILD_TYPE=Release')
    gen_build_cmd.extend(options)
    p = subprocess.Popen(' '.join(gen_build_cmd), shell=True)
    p.wait()

    build_cmd = []
    if ninja:
        build_cmd.append('ninja cxx -j%d' % MAX_CPU_CORES)
    else:
        build_cmd.append('make cxx -j%d' % MAX_CPU_CORES)

    p = subprocess.Popen(' '.join(build_cmd), shell=True)
    p.wait()

    os.chdir(cwd)


def install(build_dir):
    cwd = os.getcwd()
    os.chdir(build_dir)

    build_cmd = ['ninja', 'install']
    p = subprocess.Popen(' '.join(build_cmd), shell=True)
    p.wait()

    os.chdir(cwd)

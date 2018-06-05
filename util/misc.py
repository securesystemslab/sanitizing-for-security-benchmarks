import subprocess


def run(cmd_str):
    p = subprocess.Popen(cmd_str, shell=True)
    p.wait()


def stdout(cmd_list):
    p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)
    stdout = p.communicate()[0]
    return stdout


def configure(options):
    run('./configure ' + options)


def make(target=''):
    run('make ' + target)


def patch(patch, options='-p1'):
    run('patch ' + options + ' <' + patch)


def download(url):
    run('wget ' + url)


def untar(tarball):
    run('tar -xvf ' + tarball)

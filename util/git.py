import subprocess


def clone(repo, options=[]):
    print 'cloning ' + repo + '...'
    cmd = ['git', 'clone']
    cmd.extend(options)
    cmd.append(repo)
    subprocess.check_output(cmd)


def checkout(commit):
    p = subprocess.Popen('git checkout ' + commit, shell=True)
    p.wait()


def patch(diff):
    p = subprocess.Popen('git apply --ignore-whitespace ' + diff, shell=True)
    p.wait()

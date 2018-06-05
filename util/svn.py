import subprocess


def checkout(rev, repo, dir):
    if rev != '':
        rev = '-r' + rev
    p = subprocess.Popen(' '.join(['svn', 'co', rev, repo, dir]), shell=True)
    p.wait()

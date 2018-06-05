import shutil
import util


VALGRIND_VER = '3.13.0' # Latest version available as of 4 Mar 2018
                        # Announced on 14 June 2017
                        # http://valgrind.org/downloads
VALGRIND_URL_FORMAT = 'ftp://sourceware.org/pub/valgrind/valgrind-VER.tar.bz2'


def download(untar_dir):
    valgrind_release_url = VALGRIND_URL_FORMAT.replace('VER', VALGRIND_VER)
    util.download(valgrind_release_url)

    valgrind_tarball = 'valgrind-VER.tar.bz2'.replace('VER', VALGRIND_VER)
    util.untar(valgrind_tarball)

    shutil.move('valgrind-VER'.replace('VER', VALGRIND_VER), untar_dir)

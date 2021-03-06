from distutils.core import setup
import os
from os.path import join, normpath
import sys

import py2exe

from sinisterducks import NAME, VERSION


NAME = NAME.replace(' ', '')
DIST_DIR = 'dist\\%s' % (NAME,)



def get_py2exe_options():
    py2exe_options = dict(
        ascii=True,
        bundle_files=1, # causes problems with C extensions loaded at runtime
        dist_dir=DIST_DIR,
        dll_excludes=["pywintypes26.dll"],
        optimize=2,
        excludes=[
            # silence some warnings of missing modules
            '_imaging_gif',
            '_scproxy',
            'dummy.Process',
            'email',
            'email.utils',
            'email.Utils',
            'ICCProfile',
            'Image',

            # filter out unused .pyd files
            '_ssl',
            '_imaging',
            '_hashlib',
            'pyexpat',
            'pyreadline',
            'win32api',
            'bz2',
            '_socket',
            '_multiprocessing',
            'win32pipe',
            'select',

            # filter out unused .pyo files in library.zip
            'difflib',
            'doctest',
            'pdb',
            'pyglet.window.xlib',
            'pyglet.window.carbon',
            'pyglet.window.carbon.constants',
            'pyglet.window.carbon.types',
            'unittest',
            'win32con',
        ],
    )
    return py2exe_options


def all_files(src):
    retval = []
    for (root, dirs, files) in os.walk(normpath(src)):
        if '.svn' in dirs:
            dirs.remove('.svn')
        retval.append((root, [join(root, file) for file in files]))
    return retval


def get_data_files():
    ms_visualc_runtime = (
        r'Microsoft.VC90.CRT', [
            r'lib\Microsoft.VC90.CRT\Microsoft.VC90.CRT.manifest',
            r'lib\Microsoft.VC90.CRT\msvcr90.dll',
    ])
    data_files = [
        ms_visualc_runtime,
        (r'lib', [r'lib\avbin.dll']),
    ]
    data_files += all_files(r'data')
    return data_files


def get_config():
    return dict(
        windows=[dict(
            script='SinisterDucks.py',
            icon_resources=[(1, 'data\SinisterDucks.ico')],
        )],
        data_files=get_data_files(),
        options=dict(
            py2exe=get_py2exe_options(),
        ),
        zipfile='lib\library.zip',
    )



def main():
    setup(**get_config())
    os.system('erase dist\SinisterDucks\w9xpopen.exe')


if __name__ == '__main__':
    main()


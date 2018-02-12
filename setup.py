from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
import sys
import setuptools

__version__ = '2.0.3'


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path

    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


ext_modules = [
    Extension(
        'DeepRTSEngine',
        [
            # Engine
            'src/Game.cpp',

            # Player
            'src/player/Player.cpp',

            # Environment
            'src/environment/Map.cpp',
            'src/environment/Tile.cpp',
            'src/environment/Tilemap.cpp',

            # Unit
            'src/unit/Unit.cpp',
            'src/unit/UnitManager.cpp',

            # State
            'src/state/StateManager.cpp',
            'src/state/BaseState.cpp',
            'src/state/Walking.cpp',
            'src/state/Spawning.cpp',
            'src/state/Idle.cpp',
            'src/state/Despawned.cpp',
            'src/state/Harvesting.cpp',
            'src/state/Building.cpp',
            'src/state/Combat.cpp',
            'src/state/Dead.cpp',

            # Util
            'src/util/Pathfinder.cpp',

            # Loaders
            'src/loaders/ResourceLoader.cpp',



            'src/wrapper/Constants.cpp',
            'src/wrapper/Unit.cpp',
            'src/wrapper/Map.cpp',
            'src/wrapper/Tile.cpp',
            'src/wrapper/Tilemap.cpp',
            'src/wrapper/Game.cpp',
            'src/wrapper/Player.cpp',
            'src/wrapper/DeepRTS.cpp'



         ],
        include_dirs=[
            # Path to pybind11 headers
            get_pybind_include(),
            get_pybind_include(user=True)

        ],
        language='c++',
        debug=False

    ),
]


# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.

    The c++14 is prefered over c++11 (when it is available).
    """
    if has_flag(compiler, '-std=c++14'):
        return '-std=c++14'
    elif has_flag(compiler, '-std=c++11'):
        return '-std=c++11'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++11 support '
                           'is needed!')


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }

    if sys.platform == 'darwin':
        c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)

setup(
    name='DeepRTS',
    version=__version__,
    author='Per-Arne Andersen',
    author_email='per@sysx.no',
    url='https://github.com/UIA-CAIR/DeepRTS',
    description='A Real-Time-Strategy game for Deep Learning research ',
    long_description='',
    include_package_data=True,
    packages=find_packages(exclude=["examples", "*.tests", "*.tests.*", "tests.*", "tests"]),
    ext_modules=ext_modules,
    install_requires=['pybind11>=2.2.1', 'pygame', 'pillow', 'scipy'],
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
)

"""
import shutil
import glob
import os
file = list(glob.iglob('build/**/*.so', recursive=True))[0]
filename = os.path.basename(file)

shutil.copy(file, filename)
shutil.copy(file, os.path.join("pyDeepRTS", filename))
"""
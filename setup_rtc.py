# Copyright 2023 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pathlib
import platform
import subprocess

import setuptools
import setuptools.command.build_py
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
from wheel.bdist_wheel import get_platform

here = pathlib.Path(__file__).parent.resolve()
about = {}
with open(os.path.join(here, 'livekit', 'version.py'), 'r') as f:
    exec(f.read(), about)


class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        self.plat_name = get_platform(None)  # force a platform tag
        _bdist_wheel.finalize_options(self)


class BuildPyCommand(setuptools.command.build_py.build_py):
    """ Download a prebuilt version of livekit_ffi """

    def run(self):

        download_script = here / 'client-sdk-rust' / 'download_ffi.py'
        cmd = ['python3', download_script.absolute(), '--output',
               'livekit/resources']

        # cibuildwheel is crosscompiling to arm64 on macos, make sure we download the
        # right binary (kind of a hack here...)
        if os.environ.get("CIBUILDWHEEL") == "1" \
                and "arm64" in os.environ.get("ARCHFLAGS", ""):
            cmd += ['--arch', 'arm64']

        subprocess.run(cmd, capture_output=True, check=True)
        setuptools.command.build_py.build_py.run(self)


if platform.system() == "Linux":
    libname = "liblivekit_ffi.so"
elif platform.system() == "Darwin":
    libname = "liblivekit_ffi.dylib"
elif platform.system() == "Windows":
    libname = "livekit_ffi.dll"


setuptools.setup(
    name="livekit",
    version=about['__version__'],
    description="LiveKit Python Client SDK for LiveKit",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/livekit/client-sdk-python",
    cmdclass={
        'bdist_wheel': bdist_wheel,
        'build_py': BuildPyCommand,
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["webrtc", "realtime", "audio", "video", "livekit"],
    license="Apache-2.0",
    packages=["livekit"],
    python_requires=">=3.7.0",
    install_requires=["pyee>=11.0.0",
                      "protobuf>=3.1.0",
                      "types-protobuf>=3.1.0"],
    package_data={
        "livekit": [f'resources/{libname}', '_proto/*.py'],
    },
    project_urls={
        "Documentation": "https://docs.livekit.io",
        "Website": "https://livekit.io/",
        "Source": "https://github.com/livekit/client-sdk-python/",
    },
)

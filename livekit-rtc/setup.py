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
import sys
from typing import Any, Dict

import setuptools  # type: ignore
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel  # type: ignore

here = pathlib.Path(__file__).parent.resolve()
about: Dict[Any, Any] = {}
with open(os.path.join(here, "livekit", "rtc", "version.py"), "r") as f:
    exec(f.read(), about)


def get_platform_tag():
    """Get the wheel platform tag for the current/target platform.

    On macOS, we must respect MACOSX_DEPLOYMENT_TARGET and ARCHFLAGS environment
    variables that cibuildwheel sets, rather than using sysconfig.get_platform()
    which returns Python's compile-time values.
    """
    if sys.platform == "darwin":
        # Get deployment target from environment (set by cibuildwheel) or fall back
        target = os.environ.get("MACOSX_DEPLOYMENT_TARGET")
        if not target:
            target = platform.mac_ver()[0]
            parts = target.split(".")
            target = f"{parts[0]}.{parts[1] if len(parts) > 1 else '0'}"

        version_tag = target.replace(".", "_")

        # Check ARCHFLAGS for cross-compilation (cibuildwheel sets this)
        archflags = os.environ.get("ARCHFLAGS", "")
        if "-arch arm64" in archflags:
            arch = "arm64"
        elif "-arch x86_64" in archflags:
            arch = "x86_64"
        else:
            arch = platform.machine()

        return f"macosx_{version_tag}_{arch}"
    elif sys.platform == "linux":
        return f"linux_{platform.machine()}"
    elif sys.platform == "win32":
        arch = platform.machine()
        if arch == "AMD64":
            arch = "amd64"
        return f"win_{arch}"
    else:
        return f"{platform.system().lower()}_{platform.machine()}"


class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        self.plat_name = get_platform_tag()
        _bdist_wheel.finalize_options(self)


setuptools.setup(
    name="livekit",
    version=about["__version__"],
    description="Python Real-time SDK for LiveKit",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/livekit/python-sdks",
    cmdclass={
        "bdist_wheel": bdist_wheel,
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["webrtc", "realtime", "audio", "video", "livekit"],
    license="Apache-2.0",
    packages=setuptools.find_namespace_packages(include=["livekit.*"]),
    python_requires=">=3.9.0",
    install_requires=["protobuf>=4.25.0", "types-protobuf>=3", "aiofiles>=24", "numpy>=1.26"],
    package_data={
        "livekit.rtc": ["_proto/*.py", "py.typed", "*.pyi", "**/*.pyi"],
        "livekit.rtc.resources": [
            "*.so",
            "*.dylib",
            "*.dll",
            "LICENSE.md",
            "*.h",
            "jupyter-html/index.html",
        ],
    },
    project_urls={
        "Documentation": "https://docs.livekit.io",
        "Website": "https://livekit.io/",
        "Source": "https://github.com/livekit/python-sdks/",
    },
)

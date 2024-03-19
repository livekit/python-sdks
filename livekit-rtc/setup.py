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
from typing import Any, Dict

import setuptools  # type: ignore
import setuptools.command.build_py  # type: ignore
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel  # type: ignore
from wheel.bdist_wheel import get_platform  # type: ignore

here = pathlib.Path(__file__).parent.resolve()
about: Dict[Any, Any] = {}
with open(os.path.join(here, "livekit", "rtc", "version.py"), "r") as f:
    exec(f.read(), about)


class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        self.plat_name = get_platform(None)  # force a platform tag
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
    install_requires=["protobuf>=3", "types-protobuf>=3"],
    package_data={
        "livekit.rtc": ["_proto/*.py", "py.typed", "*.pyi", "**/*.pyi"],
        "livekit.rtc.resources": ["*.so", "*.dylib", "*.dll", "LICENSE.md", "*.h"],
    },
    project_urls={
        "Documentation": "https://docs.livekit.io",
        "Website": "https://livekit.io/",
        "Source": "https://github.com/livekit/python-sdks/",
    },
)

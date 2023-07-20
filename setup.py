import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="livekit",
    version="0.1.3",
    description="LiveKit Python Client SDK for LiveKit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/livekit/client-sdk-python",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],

    keywords="webrtc, livekit",
    packages=["livekit"],
    python_requires=">=3.7, <4",
    install_requires=["pyee>=11.0.0",
                      "protobuf>=3.1.0", "types-protobuf>=3.1.0"],
    package_data={
        "livekit": ['lib/*/*/*.*', '_proto/*.py'],
    },
    project_urls={
        "Website": "https://livekit.io/",
        "Source": "https://github.com/livekit/client-sdk-python/",
    },
)

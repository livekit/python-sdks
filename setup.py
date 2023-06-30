from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="livekit",
    version="0.1.0",
    description="A sample Python project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/livekit/client-sdk-python",
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
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
    install_requires=["pyee>=9.0.0"],
    package_data={
        "livekit": ['lib/*/*/*.*'],
    },
    project_urls={
        "Website": "https://livekit.io/",
        "Source": "https://github.com/livekit/client-sdk-python/",
    },
)

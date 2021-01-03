import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


entry_points = {
    "console_scripts": [
        "dowut = dowut.vis:main"
    ]
}

runtime = set([
    "matplotlib==3.3.3",
    "pandas==1.2.0",
    "python-daemon==2.2.4",
    "xlib==0.21",
])

develop = set([
    "coverage",
    "flake8",
    "ipython",
    "pytest",
    "pytest-cov",
    "setuptools",
    "Sphinx",
    "sphinx_rtd_theme",
    "twine",
    "wheel",
])

if __name__ == "__main__":
    with open(os.path.join(here, "README.md")) as f:
        long_description = f.read()

    setup(
        name="dowut",
        version="0.0.1",
        description="Xlib based personal desktop activity monitor.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/csams/dowut",
        author="Christopher Sams",
        author_email="cwsams@gmail.com",
        packages=find_packages(),
        install_requires=list(runtime),
        package_data={"": ["LICENSE"]},
        license="Apache 2.0",
        extras_require={
            "develop": list(develop),
        },
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8"
        ],
        include_package_data=True,
        entry_points=entry_points
    )

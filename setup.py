from setuptools import setup

setup(
    name="notter",
    version="0.2.3",
    description="A simple note taking tool for software projects.",
    author="Taylan Dogan",
    author_email="taylandogan.nl@gmail.com",
    py_modules=["notter"],
    include_package_data=True,
    install_requires=["click", "pygments"],
    extras_require={
        "dev": ["black", "flake8", "isort", "mypy", "coverage", "pytest", "pyinstaller"],
    },
    entry_points={
        "console_scripts": ["notter=notter.cli:cli"],
    },
)

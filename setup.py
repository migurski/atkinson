from setuptools import setup, Extension, find_packages

atk_extension = Extension("atkinson.atkinson", sources = ["atkinson/atk.c"])

setup(
    name = "atkinson",
    version = "1.1.3",
    description = "C implementation of Atkinson dithering",
    ext_modules = [atk_extension],
    packages = find_packages(),
    package_data = {"atkinson": ["*.pyi", "py.typed"]},
    setup_requires = ["setuptools"]
)

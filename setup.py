from setuptools import setup, find_packages

setup(
    name="notebooklm",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'playwright',
        'opencv-python',
        'numpy',
        'colorama',
    ],
)

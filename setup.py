from setuptools import setup, find_packages

setup(
    name="wff_agent",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "fastmcp",
        "akshare",
        "pandas",
        "numpy",
        "requests",
    ],
) 
from setuptools import setup

setup(
    name="NAS Management Tool",
    version="0.1.0",
    author="Florian Schmid",
    packages=["NAS_mgmt"],
    install_requires=["flask",
                      "pydngconverter"
                      "PIL",
                      ],
)
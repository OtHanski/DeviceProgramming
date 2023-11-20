import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="HbeamController-ETH",
    version="2.3.2",
    author="Otto Hanski",
    author_email="otolha@utu.fi",
    description="Program for controlling Hbeam setup at ETH",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OtHanski/HbeamController",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    include_package_data = True
)

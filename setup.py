import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    dependencies = [line.rstrip() for line in f]

setuptools.setup(
    name="BirdsongSpectrogram",
    version="0.4.0",
    author="Ralf Antonius Timmermann",
    author_email="ralf.timmermann@gmx.de",
    description="Birdsong Spectrogramm",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tamburasca/BirdsongSpectrogram",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=dependencies

)

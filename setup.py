import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="example-pkg-Tamburasca", # Replace with your own username
    version="0.0.1",
    author="Ralf Antonius Timmermann",
    author_email="rtimmermann@astro.uni-bonn.de",
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
    python_requires='>=3.6',
    install_requires=['keyboard     >=0.13.5',
                      'PyAudio      >=0.2.11',
                      'numpy        >=1.18.1',
                      'matplotlib   >=3.2.1',
                      'scikit-image >=0.17.2'],
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyneg",
    version="1.0.2",
    author="Sam Vente",
    author_email="savente93@gmail.com",
    description="A python package for simulating automated negotiations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dvente/pyneg",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["numpy", "problog"]
)

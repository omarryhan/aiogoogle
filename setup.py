import setuptools

with open('requirements.txt', "r") as f:
    requirements = f.read().splitlines()

with open('test_requirements.txt', "r") as f:
    test_requirements = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='aiogoogle',
    version="0.0.1a",
    author='Omar Ryhan',
    author_email='omarryhan@gmail.com',
    license='GNU',
    description="Aiogoogle is an async-framework agnostic async library for Google's Discovery Service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    tests_require=test_requirements,
    url='https://github.com/omarryhan/aiogoogle',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
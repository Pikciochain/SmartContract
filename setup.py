# coding: utf-8

from setuptools import setup, find_packages

with open('requirements.txt', 'r') as fin:
    requires = [line for line in fin if not line.startswith(
        '-i')]  # Excepted index instructions lines.

setup(
    name="pikciosc",
    version="version='0.1.0'",
    description="Pikcio Smart Contracts tools",
    author='Pikcio SAS',
    author_email='thibault.drevon@pikcio.com',
    url='https://github.com/Didiercc/SmartContract',
    license='Apache2',
    classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Pikcio Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3'
      ],
    keywords=["Blockchain", "Smart", "Contract", "Pikcio"],
    install_requires=requires,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    packages=find_packages(),
    test_suite='tests'
)

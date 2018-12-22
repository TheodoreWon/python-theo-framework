import setuptools

setuptools.setup(
    name='theo-framework',
    version='0.4.0',
    install_requires=['theo-database'],
    url='https://github.com/TheodoreWon/python-theo-framework',
    license='MIT',
    author='Theodore Won',
    author_email='taehee.won@gmail.com',
    description='theo-framework',
    packages=['theo', 'theo.src.framework'],
    long_description='GitHub : https://github.com/TheodoreWon/python-theo-framework',
    # long_description=open('README.md').read(),
    zip_safe=False,
)

'''
NOTE: How to make a package and release the software
0. pip install setuptools, pip install wheel, pip install twine
1. python setup.py bdist_wheel
2. cd dist
3. twine upload xxx.whl
'''

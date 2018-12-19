import setuptools

setuptools.setup(
    name='theo-framework',
    version='0.0.3',
    url='https://github.com/TheodoreWon/python-theo-framework',
    license='MIT',
    author='Theodore Won',
    author_email='taehee.won@gmail.com',
    description='Theo Framework',
    packages=setuptools.find_packages(),
    long_description=open('README.md').read(),
    zip_safe=False,
    # setup_requires=['nose>=1.0'],
    # test_suite='nose.collector',
)

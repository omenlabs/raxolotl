import setuptools

setuptools.setup(
    name="raxolotl",
    version="0.1.0",
    url="https://github.com/omenlabs/raxolotl",

    author="John Hickey",
    author_email="jjh-github@daedalian.us",

    description="Simple remote backups using rsync and ZFS snapshots",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)

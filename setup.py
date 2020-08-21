from datasf import __version__
from setuptools import setup

setup(
    name='datasf',
    version=__version__,
    description='Simple tool to retrieve data from DataSF',
    long_description='Streak API Client in Python',
    url='http://github.com/mehmetg/datasf',
    author='Mehmet Gerceker',
    author_email='mehmetg@msn.com',
    license='MIT',
    packages=['datasf'],
    package_dir={'datasf': 'datasf'},
    keywords=('food', 'data', "san francisco", "sf", "truck"),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
    ],
    provides=[],
    install_requires=[
        'colorama',
        'requests',
        'pytz'
    ],
    message_extractors={},
    entry_points={
        'console_scripts': [
            'datasf-cli = datasf.cli:main'
        ]
    },
    zip_safe=True,

)

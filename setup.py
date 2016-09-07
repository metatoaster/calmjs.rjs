from setuptools import setup
from setuptools import find_packages

version = '1.0.0'

package_json = {
    "dependencies": {
        "requirejs": "~2.1.17",
        # This should be provided by some templating library that
        # require text templates through the same import mechanism.
        # "requirejs-text": "~2.0.12",
    },
    "devDependencies": {
        "grunt-contrib-requirejs": "~0.4.4",
        "karma-requirejs": "~0.2.2",
    },
}


long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(
    name='calmjs.rjs',
    version=version,
    description="",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      "Programming Language :: Python",
      ],
    keywords='',
    author='Tommy Yu',
    author_email='tommy.yu@auckland.ac.nz',
    url='https://github.com/calmjs/calmjs.rjs',
    license='gpl',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['calmjs'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'calmjs>=1.0.3',
    ],
    extras_require={
        'dev': [
            'calmjs.dev',
        ],
    },
    entry_points={
        # If to be unleashed as a standalone tool.
        # 'console_scripts': [
        #     'rjs = calmjs.rjs.runtime:default',
        # ],
        'calmjs.runtime': [
            'rjs = calmjs.rjs.runtime:default',
        ],
    },
    package_json=package_json,
    test_suite="calmjs.rjs.tests.make_suite",
)

#!/usr/bin/python

from setuptools import setup, find_packages


setup(
    name='zeit.alexa',
    url='https://github.com/rdrongow/zeit.alexa',
    version='0.1.dev0',
    author=(
        'Ron Drongowski'
    ),
    author_email=(
        'ron.drongowski@zeit.de'
    ),
    install_requires=[
        'waitress',
        'zeit.talk>=0.1.dev0',
        'Flask>=0.12.2',
        'Flask-Ask>=0.9.7'
    ],
    description='Enable ZEIT ONLINE via Amazon Echo',
    long_description=open('README.md', 'r').read(),
    entry_points={
        'paste.app_factory': [
            'main=zeit.alexa.skill:factory'
        ],
        'console_scripts': [
            'serve=pyramid.scripts.pserve:main'
        ]
    },
    setup_requires=['setuptools_git'],
    namespace_packages=['zeit'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    keywords='amazon alexa skill echo',
    license='Proprietary license',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
    ]
)

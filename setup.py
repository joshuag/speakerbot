from setuptools import setup, find_packages

setup(
    name='SpeakerBot',
    version='0.10',
    long_description='A communal soundboard written in Flask',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests',
        'oauthlib',
        'flask',
        'pyquery',
        'fuzzywuzzy',
        'requests-oauthlib',
        'MySQL-python',
        'flask-ripozo',
        'ripozo-sqlalchemy'
    ]
)

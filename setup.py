from setuptools import setup, find_packages

setup(
    name='SpeakerBot',
    version='0.9',
    long_description="A communal soundboard written in Flask",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['flask', 'requests', 'twython', 'pyquery', 'fuzzywuzzy']
)
from setuptools import setup

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='pyecobee',
    version='1.1.1',
    description='A Python implementation of the ecobee API',
    long_description=readme,
    url='https://github.com/sfanous/Pyecobee',
    author='Sherif Fanous',
    author_email='pyecobee_support@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    packages=['pyecobee', 'pyecobee.objects'],
    install_requires=[
        'enum34>=1.1.6; python_version < "3.4"',
        'pytz>=2017.2',
        'requests>=2.13.0',
        'six>=1.10.0'],
    package_data={
        'license': ['LICENSE'],
    },
)

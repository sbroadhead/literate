from setuptools import setup

setup(
    name='literate',
    version='0.1',
    description='Literate code preprocessor for LaTeX',
    url='https://github.com/sbroadhead/literate',
    author='Simon Broadhead',
    author_email='sbroadhead@gmail.com',
    license='MIT',
    install_requires=['setuptools', 'pygments'],
    packages=['literate', 'literate.renderer'],
    entry_points={
        'console_scripts': {
            'lit=literate.frontend:main'
        },
    },
    zip_safe=False)

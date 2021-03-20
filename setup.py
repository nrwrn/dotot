'''Package configuraton for dotot.'''
import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='dotod',
    version='0.1',
    description='A batteries-not-included dotfile manager.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nrwrn/dotod',
    author='nrwrn',
    author_email='nrwrn@protonmail.com',
    py_modules=['dotod'],
    python_requires=">=3.7",
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'dotod=dotod:cli_dotod',
            'todot=dotod:cli_todot',
        ],
    },
)

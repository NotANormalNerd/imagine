from setuptools import setup

setup(
    name='imagine',
    version='1.0',
    py_modules=['imagine'],
    url='',
    license='BSD License',
    author='Dennis Schmalacker',
    author_email='github@progde.de',
    description='',
    install_requires=(
        'click<7',
        'requests<3'
    ),
    entry_points={
        'console_scripts': [
            'imagine = imagine:main',
        ],
    },
)

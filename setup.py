from setuptools import setup

setup(
    name='protox',
    version='0.4.1',
    description='Protobuf for humans',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url='http://github.com/sergey-tikhonov/protox',
    author='Sergey Tikhonov',
    author_email='srg.tikhonov@gmail.com',
    license='MIT',
    entry_points={
        'console_scripts': [
            'protoc-gen-protox=protox.plugin:main'
        ]
    },
    packages=[
        'protox',
        'protox.plugin',
        'protox.well_known_types',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

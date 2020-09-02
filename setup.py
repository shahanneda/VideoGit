import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="VideoGit",
    version="0.1.0",
    author="Shahan Neda",
    author_email="shahan.neda@gmail.com",
    description="Convert git commit history, to a animated beautiful coding video.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shahanneda/videogit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'videogit=videogit.videogit:run',
            'VideoGit=videogit.videogit:run',
        ]
    },
    install_requires=[
          'termcolor',
    ],
    python_requires='>=3.6',
)

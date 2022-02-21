import setuptools

with open("README.md", "r", encoding="utf-8", errors="ignore") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DiscordUtils",
    version="1.3.5",
    author="toxicrecker modified by Dhruvacube",
    description="DiscordUtils is a very useful library made to be used with discord.py",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/The-4th-Hokage/DiscordUtils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">= 3.6",
    include_package_data=True,
    extras_require={
        "voice": ["youtube-dl"],
        'docs': [
            'sphinx==4.3.1',
            'sphinxcontrib_trio==1.1.2',
            'sphinxcontrib-websupport',
        ],
        "all": [
            "youtube-dl",
            'sphinx==4.3.1',
            'sphinxcontrib_trio==1.1.2',
            'sphinxcontrib-websupport'
        ]
    }
)

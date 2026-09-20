from setuptools import setup, find_packages

setup(
    name="vader-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "rich>=13.7.0",
        "prompt-toolkit>=3.0.40",
        "httpx>=0.27.0",
        "pydantic>=2.6.0",
        "pyyaml>=6.0.1",
        "croniter>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "vader=vader.cli.main:cli",
        ],
    },
)

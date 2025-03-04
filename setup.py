#!/usr/bin/env python
"""
Setup script for fractrade-executor
"""

from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="fractrade-executor",
    version="0.1.0",
    description="Executor for Fractrade trading signals and actions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/fractrade-executor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8,<4.0",
    install_requires=[
        "fractrade-hl-simple",
        "websockets",
        "python-dotenv",
        "pydantic",
        "asyncio",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "black",
            "isort",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "fractrade-executor=fractrade_executor.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 
from setuptools import setup, find_packages

setup(
    name="webscraper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
        "python-dateutil>=2.8.2",
        "requests>=2.26.0",
        "beautifulsoup4>=4.9.3",
        "lxml>=4.9.0",
        "feedparser>=6.0.0",
    ],
    python_requires=">=3.7",
) 
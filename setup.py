from setuptools import setup, find_packages

setup(
    name="govbuyscrapy",
    version="0.1",
    packages=find_packages(),
    entry_points={'scrapy': ['settings = govbuyscrapy.settings']},
    # to make the scrapyd can import you "scrapy" package and set you project setting file
)

from setuptools import find_packages, setup

setup(
    name="disney-fireworks-scraper",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "selenium==4.8.3",
        "google-api-python-client==2.146.0",
        "google-auth-httplib2==0.2.0",
        "google-auth-oauthlib==1.2.1",
    ],
    scripts=[
        "src/google_calendar.py",
    ],
)

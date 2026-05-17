from setuptools import setup, find_packages

setup(
    name="flick-shared",
    version="0.1.0",
    description="Shared utilities and infrastructure for Flick microservices",
    author="Flick Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "PyJWT>=2.12.0,<3.0",
        "requests>=2.33.0,<3.0",
        "redis>=5.0.0",
        "psycopg[binary]>=3.1.0",
    ],
)

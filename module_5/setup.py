from setuptools import setup, find_packages

# setup.py makes this project installable (including editable installs with `pip install -e .`).
# That improves import consistency across local runs, tests, and CI environments.

setup(
    name="grad-cafe-analytics",
    version="0.1.0",
    description="Flask + PostgreSQL app for Grad Cafe applicant analytics.",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    py_modules=["app", "load_data", "query_data", "db"],
    include_package_data=True,
    install_requires=[
        "Flask==3.1.3",
        "psycopg[binary]==3.1.19",
        "beautifulsoup4==4.12.3",
        "urllib3==2.6.3",
    ],
    extras_require={
        "dev": [
            "pytest==8.3.5",
            "pytest-cov==7.0.0",
            "pylint==3.2.7",
            "pydeps==1.12.20",
        ]
    },
)

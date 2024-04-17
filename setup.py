from setuptools import setup, find_packages

setup(
	name="personal_dashboard",
	version="2023.12.22",
	packages=find_packages(),
    install_requires=[
        'pysmb',
        'streamlit',
        'openpyxl',
        'plotly',
    ],
)

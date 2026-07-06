from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in go1_cms/__init__.py
from go1_cms import __version__ as version

setup(
	name="go1_cms",
	version=version,
	description="Go1 CMS",
	author="Tridotstech",
	author_email="info@tridotstech.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)

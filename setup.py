import re
from setuptools import setup, find_packages

def getVersion():
    with open('apps/__init__.py') as file:
        return re.search(r"""__version__\s+=\s+(['"])(?P<ver>.+?)\1""",
                         file.read()).group('ver')

longDescription = """This is CLI tool for docker volume and image backup. It can backup volumes of all existing
                     containers, all images or it can take the list of containers and images to backup as an option."""
setup(
    name="docker-backup-tool",
    description="CLI tool for docker volume and image backup.",
    long_description=longDescription,
    version=getVersion(),
    py_modules=["apps"],
    license="MIT",
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    author="Nino Tsulaia",
    author_email="tsulaianino01@mail.com",
    classifiers=[
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6", ],
    entry_points={
        "console_scripts": [
        "docker-backup=apps.docker_backup:mainfunc"
        ]
    }
)

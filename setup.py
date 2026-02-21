from setuptools import setup, find_packages

setup(
    name="tasksync",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tasksync=tasksync.cli:main",
        ],
    },
    data_files=[
        (".", ["tasksync.service", "install-systemd.sh", "SYSTEMD_SETUP.md"]),
    ],
    include_package_data=True,
)

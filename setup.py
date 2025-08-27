from setuptools import setup, find_packages

setup(
    name="zkatt-attendance-system",
    version="1.0.0",
    description="Système de gestion de présence biométrique avec ZKTeco",
    author="Votre Nom",
    author_email="votre.email@entreprise.com",
    packages=find_packages(),
    install_requires=[
        "pyzk==0.9.1",
        "customtkinter==5.2.0",
        "openpyxl==3.1.2",
        "reportlab==4.0.8",
        "Pillow==10.1.0",
        "schedule==1.2.0",
        "python-dateutil==2.8.2"
    ],
    entry_points={
        'console_scripts': [
            'zkatt=main:main',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)

from setuptools import setup, find_packages

setup(
    name="llama-cleanup",
    version="1.7.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "langchain_ollama"
    ],
    include_package_data=True,
    description="A package to process addresses and filter out noise",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Andrew",
    author_email="gordienko.adg@gmail.com",
    url="https://github.com/AndrewGordienko/address-cleanup",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'llama_cleanup_process=llama_cleanup.main:process_addresses',  # Update to the correct package name
        ],
    },
    python_requires='>=3.8',
)


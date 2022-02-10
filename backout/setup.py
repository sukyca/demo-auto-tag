import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='backout-functions-iolap',
    version='0.0.1',
    author='iOLAP',
    author_email='ahrelja@iolap.com',
    description='A small package including undo functions to revert Snowflake SQL changes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sukyca/snowlake-test-repo',
    project_urls={
        'Bug Tracker': 'https://github.com/sukyca/snowlake-test-repo/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=setuptools.find_packages(where='backout_scripts'),
    package_dir={'': 'backout_scripts'},
    package_data={'backout_functions': ['templates/*.sql']},
    python_requires='==3.9.*',
    install_requires=[
        'asn1crypto==1.4.0',
        'azure-common==1.1.27',
        'azure-core==1.17.0',
        'azure-storage-blob==12.8.1',
        'boto3==1.18.30',
        'botocore==1.21.30',
        'certifi==2021.5.30',
        'cffi==1.14.6',
        'chardet==4.0.0',
        'charset-normalizer==2.0.4',
        'cryptography==3.4.8',
        'idna==3.2',
        'isodate==0.6.0',
        'jmespath==0.10.0',
        'msrest==0.6.21',
        'oauthlib==3.1.1',
        'oscrypto==1.2.1',
        'pycparser==2.20',
        'pycryptodomex==3.10.1',
        'PyJWT==2.1.0',
        'pyOpenSSL==20.0.1',
        'python-dateutil==2.8.2',
        'pytz==2021.1',
        'requests==2.26.0',
        'requests-oauthlib==1.3.0',
        's3transfer==0.5.0',
        'six==1.16.0',
        'snowflake-connector-python==2.6.2',
        'urllib3==1.26.6'
    ]
)
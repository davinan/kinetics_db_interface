from setuptools import setup

setup(
    name='kinetics_api',
    version='0.1.0',    
    description='An open-source package for accessing chemical kinetics databases',
    url='https://github.com/davinan/kinetics_db_interface/',
    author='Davi Nakajima An',
    author_email='dnan@uw.edu',
    license='MIT License',
    packages=['kinetics_interface'],
    install_requires=['tellurium',
                      'numpy==1.24.0',                     
                      'pandas',
                      'requests',
    ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
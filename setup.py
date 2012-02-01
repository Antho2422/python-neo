# -*- coding: utf-8 -*-

from setuptools import setup, find_packages



long_description='''
NEO stands for Neural Ensemble Objects and is a project to provide a common set of base classes to be used
in neural data analysis, with the aim of getting OpenElectrophy, NeuroTools, GNode, DABBSIP and maybe other projects
with similar goals more close together.

It provide a set of basic class to manipulate electro-physiological (in vivo and/or simulated) data 
and an IO module to read/write as many as possible file format.

'''

#~ print find_packages()

import os

from neo import version as neov

if __name__=="__main__":
    
    
    
    setup(
        name = "neo",
        version = neov.version,
        packages = find_packages(),

        
        include_package_data=True,
        
        install_requires=[
                        'numpy>=1.3.0',
                        #'scipy>=0.7.0',
                        'quantities>=0.9.0',
                        ],
                        
        requires = [
                          ],
        
        # metadata for upload to PyPI
        author = "S.garcia, A.Davison, P.Rautenberg, A.Sobolev, F.Jaillet, Y.Mahnoun, T.Brizzi, T.Wachtler, L.Estebannez, P.Yger, Yury V. Zaytsev",
        author_email = "sgarcia at olfac.univ-lyon1.fr",
        long_description = long_description,
        license = "BSD",
        description = "neo : objects and IO to manipulate electro-physiological (in vivo and/or simulated) data",
        url='http://neuralensemble.org/trac/neo',
        classifiers=['Development Status :: 3 - Alpha',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Bio-Informatics'
            ]
    )



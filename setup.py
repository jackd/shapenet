#!python3

from setuptools import setup

setup(name= 'ShapeNet',
      version= '1.0',
      discription= 'Python library for handling shapenet dataset',
      author= 'Dominic Jack',
      author_email= 'thedomjack@gmail.com',
      url= 'https://www.github.com/ziwenzhuang/shapenet',
      packages= [
            'shapenet', 'dids', 'util3d'
      ],
      install_requires= [
            'numpy', 'h5py', 'progress', 'wget', 'mayavi'
      ]
)


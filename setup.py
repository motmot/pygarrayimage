from setuptools import setup

setup(name='pygarrayimage',
      description="Allow numpy arrays as source of texture data for pyglet.",
      long_description = \
"""pygarrayimage allows display of Python objects supporting the array
interface as OpenGL textures without a copy. The OpenGL texture
handling is done using pyglet.

In other words, this allows fast transfer of data from numpy arrays
(or any other data source supporting the array interface) to the video
card.
""",
      version='0.0.5', # keep in sync with arrayimage.py
      install_requires=['pyglet>=1.0',],
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      url='http://code.astraw.com/projects/motmot/wiki/pygarrayimage',
      license='BSD',
      packages=['pygarrayimage'],
      )

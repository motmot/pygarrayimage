from setuptools import setup
import os

kws = {}
if not int(os.getenv( 'DISABLE_INSTALL_REQUIRES','0' )):
    kws['install_requires'] = ['pyglet>=1.0']

setup(name='pygarrayimage',
      description="Allow numpy arrays as source of texture data for pyglet.",
      long_description = \
"""pygarrayimage allows display of Python objects supporting the array
interface as OpenGL textures without a copy. The OpenGL texture
handling is done using pyglet.

In other words, this allows fast transfer of data from numpy arrays
(or any other data source supporting the array interface) to the video
card.

TODO: support the buffer interface added with Python 2.6/3.0 rather
than the numpy-defined array interface.

""",
      version='0.0.7', # keep in sync with pygarrayimage/arrayimage.py
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      url='http://code.astraw.com/projects/motmot/wiki/pygarrayimage',
      license='BSD',
      packages=['pygarrayimage'],
      **kws)

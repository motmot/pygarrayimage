*********************************************************************
:mod:`pygarrayimage` -- fast display of numpy arrays to OpenGL/pyglet
*********************************************************************

.. module:: pygarrayimage
  :synopsis: fast display of numpy arrays to OpenGL/pyglet
.. index::
  module: pygarrayimage
  single: pygarrayimage

Description
===========

pygarrayimage allows display of Python objects supporting the `array
interface`__ as OpenGL textures without a copy. The OpenGL texture
handling is done using pyglet__. 

__ http://numpy.scipy.org/array_interface.shtml
__ http://pyglet.org pyglet

In other words, this allows fast transfer of data from numpy arrays
(or any other data source supporting the array interface) to the video
card.

Discussion
==========

For the time being, all discussion for this software should happen on
the `pyglet-users mailing list`__.

__ http://groups.google.com/group/pyglet-users 

Screenshot
==========

One use case of pygarrayimage is the :mod:`wxglvideo`. Here is a
screenshot of the wxglvideo_demo program:

.. image:: _static/wxglvideo_demo_screenshot.png
  :alt: Screenshot of wxglvideo_demo

Download
========

Download official releases from `the download page`__.

__ http://pypi.python.org/pypi/pygarrayimage

The `development (SVN) version of pygarrayimage`__ may be downloaded
via subversion::

  svn co http://code.astraw.com/motmot/trunk/pygarrayimage

__ http://code.astraw.com/motmot/trunk/pygarrayimage#egg=pygarrayimage-dev

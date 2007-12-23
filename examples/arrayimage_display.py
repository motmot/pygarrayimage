#!/usr/bin/env python

'''Display data supporting the __array_interface__ (e.g. numpy arrays, PIL images, etc.).

Usage::

    numpy_display.py [filename]

A checkerboard background is visible behind any transparent areas of the
image.

If given, the filename parameter will load an image file using the
Python Imaging Library and then display it. Otherwise, a numpy array
will be generated and displayed. In both cases, the data is
transferred using the __array_interface__ protocol specified by numpy.

'''

import sys

from pyglet.gl import *
from pyglet import window
from pyglet import image
from pygarrayimage.arrayimage import ArrayInterfaceImage

import numpy

if __name__ == '__main__':
    if len(sys.argv) > 2:
        print __doc__
        sys.exit(1)

    filename = None
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    w = window.Window(visible=False, resizable=True)
    
    if filename is None:
        # test constructor from numpy array
        width, height= 320,240
        depth=4 # 1, 3, or 4
        arr = numpy.arange( width*height*depth, dtype=numpy.uint8)
        arr.shape = height,width,depth
        if depth==1 and 1:
            # test 2D array
            arr.shape = height,width
    else:
        # test constructor from PIL image
        import Image
        if Image.VERSION < '1.1.6':
            # new PIL necessary for __array_interface__
            raise ValueError("Need Image (PIL) version 1.1.6 ")
        arr = Image.open(filename)
        #arr = numpy.asarray( pil_image )
    aii = ArrayInterfaceImage(arr)

    img = aii.texture

    checks = image.create(32, 32, image.CheckerImagePattern())
    background = image.TileableTexture.create_for_image(checks)

    w.width = img.width
    w.height = img.height
    w.set_visible()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    i=0
    while not w.has_exit:
        w.dispatch_events()
        
        background.blit_tiled(0, 0, 0, w.width, w.height)
        img.blit(0, 0, 0)
        w.flip()

        if filename is None and 1:
            # modify numpy array in-place

            arr.fill(i)
            aii.dirty() # dirty the ArrayInterfaceImage because the data changed
            i=(i+1)%256

            if i == 1 and 0:
                arr = numpy.ones_like( arr ) # create a new array
                aii.view_new_array(arr) # switch ArrayInterfaceImage to view the new array

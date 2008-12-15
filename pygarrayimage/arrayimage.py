# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2007-2008 Andrew Straw
# Copyright (c) 2005-2008, Enthought, Inc.
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

from pyglet.image import ImageData
import ctypes
import pyglet
import pyglet.gl as gl

__version__ = '0.0.6-svn' # keep in sync with setup.py
__all__ = ['ArrayInterfaceImage']

def is_c_contiguous(inter):
    strides = inter.get('strides')
    shape = inter.get('shape')
    if strides is None:
        return True
    else:
        test_strides = strides[-1]
        N = len(strides)
        for i in range(N-2):
            test_strides *= test_strides * shape[N-i-1]
            if test_strides == strides[N-i-2]:
                continue
            else:
                return False
        return True

def get_stride0(inter):
    strides = inter.get('strides')
    if strides is not None:
        return strides[0]
    else:
        # C contiguous
        shape = inter.get('shape')
        cumproduct = 1
        for i in range(1,len(shape)):
            cumproduct *= shape[i]
        return cumproduct

class ArrayInterfaceImage(ImageData):
    def __init__(self,arr,format=None,allow_copy=True):
        '''Initialize image data from the numpy array interface

        :Parameters:
            `arr` : array
                data supporting the __array_interface__ protocol. If
                rank 2, the shape must be (height, width). If rank 3,
                the shape is (height, width, depth). Typestr must be
                '|u1' (uint8).
            `format` : str or None
                If specified, a format string describing the data
                format array (e.g. 'L', 'RGB', or 'RGBA'). Defaults to
                a format determined from the shape of the array.
            `allow_copy` : bool
                If False, no copies of the data will be made, possibly
                resulting in exceptions being raised if the data is
                unsuitable. In particular, the data must be C
                contiguous in this case. If True (default), the data
                may be copied to avoid such exceptions.

        '''

        self.inter = arr.__array_interface__
        self.allow_copy = allow_copy
        self.data_ptr = ctypes.c_void_p()
        self.data_ptr.value = 0

        if len(self.inter['shape'])==2:
            height,width = self.inter['shape']
            if format is None:
                format = 'L'
        elif len(self.inter['shape'])==3:
            height,width,depth = self.inter['shape']
            if format is None:
                if depth==3:
                    format = 'RGB'
                elif depth==4:
                    format = 'RGBA'
                elif depth==1:
                    format = 'L'
                else:
                    raise ValueError("could not determine a format for "
                                     "depth %d"%depth)
        else:
            raise ValueError("arr must have 2 or 3 dimensions")
        data = None
        pitch = get_stride0(self.inter)
        super(ArrayInterfaceImage, self).__init__(
            width, height, format, data, pitch=pitch)

        self.view_new_array( arr )

    def get_data(self):
        if self._real_string_data is not None:
            return self._real_string_data

        if not self.allow_copy:
            raise ValueError("cannot get a view of the data without "
                             "allowing copy")

        # create a copy of the data in a Python str
        shape = self.inter['shape']
        nbytes = 1
        for i in range(len(shape)):
            nbytes *= shape[i]
        mydata = ctypes.create_string_buffer( nbytes )
        ctypes.memmove( mydata, self.data_ptr, nbytes)
        return mydata.value

    data = property(get_data,None,"string view of data")

    def _convert(self, format, pitch):
        if format == self._current_format and pitch == self._current_pitch:
            # do something with these values to convert to a ctypes.c_void_p
            if self._real_string_data is None:
                return self.data_ptr
            else:
                # XXX pyglet may copy this to create a pointer to the buffer?
                return self._real_string_data
        else:
            if self.allow_copy:
                raise NotImplementedError("XXX")
            else:
                raise ValueError("cannot convert to desired "
                                 "format/pitch without copying")

    def _ensure_string_data(self):
        if self.allow_copy:
            raise NotImplementedError("XXX")
        else:
            raise ValueError("cannot create string data without copying")

    def dirty(self):
        '''Force an update of the texture data.
        '''

        texture = self.texture
        internalformat = None
        self.blit_to_texture(
            texture.target, texture.level, 0, 0, 0, internalformat )

    def view_new_array(self,arr):
        '''View a new array of the same shape.

        The same texture will be kept, but the data from the new array
        will be loaded.

        :Parameters:
            `arr` : array
                data supporting the __array_interface__ protocol. If
                rank 2, the shape must be (height, width). If rank 3,
                the shape is (height, width, depth). Typestr must be
                '|u1' (uint8).
        '''

        inter = arr.__array_interface__

        if not is_c_contiguous(inter):
            if self.allow_copy:
                # Currently require numpy to deal with this
                # case. POSSIBLY TODO: re-implement copying into
                # string buffer so that numpy is not required.
                import numpy
                arr = numpy.array( arr, copy=True, order='C' )
                inter = arr.__array_interface__
            else:
                raise ValueError('copying is not allowed but data is not '
                                 'C contiguous')

        if inter['typestr'] != '|u1':
            raise ValueError("data is not type uint8 (typestr=='|u1')")

        if inter['shape'] != self.inter['shape']:
            raise ValueError("shape changed!")

        self._real_string_data = None
        self.data_ptr.value = 0

        idata = inter['data']
        if isinstance(idata,tuple):
            data_ptr_int,readonly = idata
            self.data_ptr.value = data_ptr_int
        elif isinstance(idata,str):
            self._real_string_data = idata
        else:
            raise ValueError("__array_interface__ data attribute was not "
                             "tuple or string")

        # maintain references so they're not de-allocated
        self.inter = inter
        self.arr = arr

        self.dirty()

# Port of Enthought's ArrayImage, found at
# https://svn.enthought.com/enthought/changeset/18241 Robert Kern's
# log message says "Correct some edge artifacts when drawing images."

class ArrayImage(ArrayInterfaceImage):
    """ pyglet ImageData made from numpy arrays.

    Customized from pygarrayimage's ArrayInterfaceImage to override
    the texture creation. blit_to_texture seems to be modified from
    pyglet's ImageData class.
    """

    def create_texture(self, cls, rectangle=False):
        """Create a texture containing this image.

        If the image's dimensions are not powers of 2, a TextureRegion of
        a larger Texture will be returned that matches the dimensions of this
        image.

        :Parameters:
            `cls` : class (subclass of Texture)
                Class to construct.
            `rectangle` : bool
                ``True`` if a rectangle can be created; see
                `AbstractImage.get_texture`.

                **Since:** pyglet 1.1

        :rtype: cls or cls.region_class
        """
        internalformat = self._get_internalformat(self.format)
        texture = cls.create(self.width, self.height, internalformat, rectangle)
        subimage = False
        if texture.width != self.width or texture.height != self.height:
            texture = texture.get_region(0, 0, self.width, self.height)
            subimage = True

        gl.glBindTexture(texture.target, texture.id)
        gl.glTexParameteri(texture.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(texture.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(texture.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(texture.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)

        if subimage:
            width = texture.owner.width
            height = texture.owner.height
            blank = (ctypes.c_ubyte * (width * height * 4))()
            gl.glTexImage2D(texture.target, texture.level,
                         internalformat,
                         width, height,
                         1,
                         gl.GL_RGBA, gl.GL_UNSIGNED_BYTE,
                         blank)
            internalformat = None

        self.blit_to_texture(texture.target, texture.level,
            0, 0, 0, internalformat)

        return texture

    def blit_to_texture(self, target, level, x, y, z, internalformat=None):
        '''Draw this image to to the currently bound texture at `target`.

        If `internalformat` is specified, glTexImage is used to initialise
        the texture; otherwise, glTexSubImage is used to update a region.
        '''

        data_format = self.format
        data_pitch = abs(self._current_pitch)

        # Determine pixel format from format string
        matrix = None
        format, type = self._get_gl_format_and_type(data_format)
        if format is None:
            if (len(data_format) in (3, 4) and
                gl.gl_info.have_extension('GL_ARB_imaging')):
                # Construct a color matrix to convert to GL_RGBA
                def component_column(component):
                    try:
                        pos = 'RGBA'.index(component)
                        return [0] * pos + [1] + [0] * (3 - pos)
                    except ValueError:
                        return [0, 0, 0, 0]
                # pad to avoid index exceptions
                lookup_format = data_format + 'XXX'
                matrix = (component_column(lookup_format[0]) +
                          component_column(lookup_format[1]) +
                          component_column(lookup_format[2]) +
                          component_column(lookup_format[3]))
                format = {
                    3: gl.GL_RGB,
                    4: gl.GL_RGBA}.get(len(data_format))
                type = gl.GL_UNSIGNED_BYTE

                gl.glMatrixMode(gl.GL_COLOR)
                gl.glPushMatrix()
                gl.glLoadMatrixf((gl.GLfloat * 16)(*matrix))
            else:
                # Need to convert data to a standard form
                data_format = {
                    1: 'L',
                    2: 'LA',
                    3: 'RGB',
                    4: 'RGBA'}.get(len(data_format))
                format, type = self._get_gl_format_and_type(data_format)

        # Workaround: don't use GL_UNPACK_ROW_LENGTH
        if pyglet.version[:3] >= '1.1':
            # tested on 1.1beta1
            if gl.current_context._workaround_unpack_row_length:
                data_pitch = self.width * len(data_format)
        else:
            # tested on 1.0
            if gl._current_context._workaround_unpack_row_length:
                data_pitch = self.width * len(data_format)

        # Get data in required format (hopefully will be the same format it's
        # already in, unless that's an obscure format, upside-down or the
        # driver is old).
        data = self._convert(data_format, data_pitch)

        if data_pitch & 0x1:
            alignment = 1
        elif data_pitch & 0x2:
            alignment = 2
        else:
            alignment = 4
        row_length = data_pitch / len(data_format)
        gl.glPushClientAttrib(gl.GL_CLIENT_PIXEL_STORE_BIT)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, alignment)
        gl.glPixelStorei(gl.GL_UNPACK_ROW_LENGTH, row_length)
        self._apply_region_unpack()
        gl.glTexParameteri(target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)


        if target == gl.GL_TEXTURE_3D:
            assert not internalformat
            gl.glTexSubImage3D(target, level,
                            x, y, z,
                            self.width, self.height, 1,
                            format, type,
                            data)
        elif internalformat:
            gl.glTexImage2D(target, level,
                         internalformat,
                         self.width, self.height,
                         0,
                         format, type,
                         data)
        else:
            gl.glTexSubImage2D(target, level,
                            x, y,
                            self.width, self.height,
                            format, type,
                            data)
        gl.glPopClientAttrib()

        if matrix:
            gl.glPopMatrix()
            gl.glMatrixMode(gl.GL_MODELVIEW)


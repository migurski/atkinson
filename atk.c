#include <Python.h>
#include <string.h>
#include <stdio.h>

// adds the error so that it doesn't overflow an unsigned char
#ifndef adderror
    #define adderror( b, e ) ( ((b) < -(e)) ? 0x00 : ( ((0xFF - (b)) < (e)) ? 0xFF : (b + e) ) )
#endif

/* atk.atk()
 *   Given image dimensions and a raw string of grayscale pixels, dithers the "image"
 */
static PyObject *atk(PyObject *self, PyObject *args)
{
    int i, x, y, w, h, off, len, err;
    unsigned char *pixels, threshold[256];
    unsigned char old, new;
    
    if(!PyArg_ParseTuple(args, "iis#", &w, &h, &pixels, &len))
    {
        /* fail unless I got two ints and a single string as input */
        return NULL;
    }
    
    if(w * h != len)
    {
        // fail if the given dimensions don't seem to match the passed image
        return NULL;
    }
    
    // set up a basic threshold table to save some if/else later on
    for(i = 0; i < 128; i++) {
        threshold[i] = 0x00;
    }
    
    for(i = 128; i < 256; i++) {
        threshold[i] = 0xFF;
    }
    
    for(y = 0; y < h; y++)
    {
        for(x = 0; x < w; x++)
        {
            // offset in the string for a given (x, y) pixel
            off = (y * w) + x;
            
            // threshold and get the error
            old = pixels[off];
            new = threshold[ pixels[off] ];
            err = (old - new) >> 3; // divide by 8

            // update the image
            pixels[off] = new;
            
            // now distribute the error...
            
            // x+1, y
            if(x+1 < w) {
                pixels[off + 1] = adderror(pixels[off + 1], err);
            }
            
            // x+2, y
            if(x+2 < w) {
                pixels[off + 2] = adderror(pixels[off + 2], err);
            }
            
            // x-1, y+1
            if(x > 0 && y+1 < h) {
                pixels[off + w - 1] = adderror(pixels[off + w - 1], err);
            }
            
            // x, y+1
            if(y+1 < h) {
                pixels[off + w] = adderror(pixels[off + w], err);
            }
            
            // x+1, y+1
            if(x+1 < w && y+1 < h) {
                pixels[off + w + 1] = adderror(pixels[off + w + 1], err);
            }
            
            // x, y+2
            if(y+2 < h) {
                pixels[off + 2 * w] = adderror(pixels[off + 2 * w], err);
            }
        }
    }
    
    return Py_BuildValue("s#", pixels, len);
}

/* map between python function name and C function pointer */
static PyMethodDef AtkMethods[] = {
    {"atk", atk, METH_VARARGS, "Dither an image"},
    {NULL, NULL, 0, NULL}
};

/* bootstrap function, called automatically when you 'import atk' */
PyMODINIT_FUNC initatk(void) {
    (void)Py_InitModule("atk", AtkMethods);
}

__author__ = 'keithd'

import math
from PIL import Image
import PIL.ImageFilter as PIF
import PIL.ImageEnhance as PIE
from prims1 import *
import kd_array
import fileops

# from tkinter import *
# root = Tk() # This must be done before tkinter will do anything

class Imager():

    _pixel_colors_ = {'red':(255,0,0), 'green': (0,255,0), 'blue': (0,0,255), 'white': (255,255,255),
                      'black': (0,0,0)}
    _pixel_color_indices_ = {'red':0,'green':1,'blue':2}

    def __init__(self,fid=False,image=False,width=100,height=100,background='black',mode='RGB'):
        self.fid = fid # The image file
        self.image = image # A PIL image object
        self.pixmap = False # A matrix of rgb lists, one for each pixel.  The numpy version is a 3-d array object.
        self.colims = False # 3 image objects, one each for the R, G and B components.
        self.xmax = width; self.ymax = height # These can change if there's an input image or file
        self.mode = mode
        self.init_image(background=background)

    def init_image(self,background='black'):
        if self.fid: self.load_image()
        if self.image: self.preprocess_image()
        else: self.image = self.gen_plain_image(self.xmax,self.ymax,background)
        self.gen_pixmap()

    # Load image from file
    def load_image(self):
        self.image = Image.open(self.fid)  # the image is actually loaded as needed (automatically by PIL)
        if self.image.mode != self.mode:
            self.image = self.image.convert(self.mode)

    # Save image to a file.  Only if fid has no extension is the type argument used.  When writing to a jpeg
    # file, use the extension JPEG, not JPG, which seems to cause some problems.
    def dump_image(self,fid,type='gif'):
        fname = fid.split('.')
        type = fname[1] if len(fname) > 1 else type
        self.image.save(fname[0]+'.'+type,format=type)

    def get_image(self): return self.image
    def set_image(self,im): self.image = im

    def preprocess_image(self):
        self.get_image_dims()
        # self.gen_pixmap()
        # self.gen_colims()

    def display(self):
        self.image.show()

    def get_image_dims(self):
         self.xmax = self.image.size[0]
         self.ymax = self.image.size[1]

    def copy_image_dims(self,im2):
        im2.xmax = self.xmax; im2.ymax = self.ymax

    def gen_plain_image(self,x,y,color,mode=None):
        m = mode if mode else self.mode
        return Image.new(m,(x,y),self.get_color_rgb(color))

    def get_pixel(self,x,y): return self.image.getpixel((x,y))
    def set_pixel(self,x,y,rgb): self.image.putpixel((x,y),rgb)

    def listify_image_rgb(self,x,y):
         val = self.get_pixel(x,y)
         return list(val) if type(val) == tuple else val

    # The use of Image.eval applies the func to each BAND, independently, if image pixels are RGB tuples.
    def map_image(self,func,image=False):
        "Apply func to each pixel of the image, returning a new image"
        image = image if image else self.image
        return Imager(image=Image.eval(image,func)) # Eval creates a new image, so no need for me to do a copy.

    # This applies the function to each RGB TUPLE, returning a new tuple to appear in the new image.  So func
    # must return a 3-tuple if the image has RGB pixels.

    def map_image2(self,func,image=False):
        im2 = image.copy() if image else self.image.copy()
        for i in range(self.xmax):
            for j in range(self.ymax):
                im2.putpixel((i,j),func(im2.getpixel((i,j))))
        return Imager(image = im2)

    # This applies the function to each pixel but does not modify the image nor create a new one.  So the result is
    # in the side effects incured by the function call.

    def mapc_image(self,func,image=False):
        im = image if image else self.image
        for i in range(self.xmax):
            for j in range(self.ymax):
                func(im.getpixel((i,j)))

    # This returns a resized copy of the image
    def resize(self,new_width,new_height,image=False):
        image = image if image else self.image
        return Imager(image=image.resize((new_width,new_height)))

    def scale(self,xfactor,yfactor):
        return self.resize(round(xfactor*self.xmax),round(yfactor*self.ymax))

    # Note that grayscale uses the RGB triple to define shades of gray.
    def gen_grayscale(self,image=False): return self.scale_colors(image=image,degree=0)

    def scale_colors(self,image=False,degree=0.5):
        image = image if image else self.image
        return Imager(image=ImageEnhance.Color(image).enhance(degree))

    def paste(self,im2,x0=0,y0=0):
        self.get_image().paste(im2.get_image(),(x0,y0,x0+im2.xmax,y0+im2.ymax))

    # WTA = winner take all: The dominant color becomes the ONLY color in each pixel.  However, the winner must
    # dominate by having at least thresh fraction of the total.
    def map_color_wta(self,image=False,thresh=0.34):
        image = image if image else self.image
        def wta(p):
            s = sum(p); w = max(p)
            if s > 0 and w/s >= thresh:
                return tuple([(x if x == w else 0) for x in p])
            else:
                return (0,0,0)
        return self.map_image2(wta,image)

    def get_color_rgb(self,colorname): return Imager._pixel_colors_[colorname]
    def get_pixmap_rgb(self,x,y): return self.pixmap[x][y]
    def get_pixmap_red(self,x,y): return self.pixmap[x][y][0]
    def get_pixmap_green(self,x,y): return self.pixmap[x][y][1]
    def get_pixmap_blue(self,x,y): return self.pixmap[x][y][2]
    def get_pixel_index(self,band='red'): return Imager._pixel_color_indices_[band]
    def get_colim_value(self,color_index,x,y): return self.colims[color_index].getpixel((x,y));

    def combine_pixels(self,p1,p2,alpha=0.5):
        return tuple([round(alpha*p1[i] + (1 - alpha)*p2[i]) for i in range(3)])

    # The pixmap is stored in column-major format such that elements of a[i] are one COLUMN of the image.
    # The origin of each image is presumably the upper left corner.

    # This one does not require numpy
    def gen_pixmap(self):
        self.pixmap = [[self.listify_image_rgb(x,y) for y in range(self.ymax)] for x in range(self.xmax)]

    def gen_colims(self):
        "Generate the three color images"
        r,g,b = self.image.split()
        self.colims = [r,g,b]

    # This requires numpy (in kd_array).  It doesn't seem significantly faster.
    def gen_numpy_pixmap(self):
        self.pixmap = kd_array.gen_array([self.xmax,self.ymax,3],init_elem=0)
        for i in range(self.xmax):
            for j in range(self.ymax):
                rgb = self.get_pixel(i,j)
                for k in range(3):
                    self.pixmap[i][j][k] = rgb[k]

    def center_of_mass(self,image=False, thresh = 0):
        im = image if image else self.image
        sumx = 0; countx = 0; sumy = 0; county = 0
        def test1(p):
            return (p > thresh)
        def test2(p):
            return (sum(p) > thresh)
        f = test1 if len(im.getbands()) == 1 else test2
        for i in range(self.xmax):
            for j in range(self.ymax):
                if f(im.getpixel((i,j))):
                    countx += 1; county += 1; sumx += i; sumy += j
        return [sumx/countx, sumy/county]

    # This compares two pixels and computes the mean square error between them.  For RGB images, these
    # pixels are 3-element lists, whereas black-white or grayscale pixels consist of scalar values.

    def pixel_error(self,p1,p2, vector = True):
        if vector:
            return  math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)
        else:
            return abs(p1 - p2)

    # This calculates an average pixel over an entire image.
    def avg_color(self, vector = True):
        return self.avg_rgb() if vector else self.avg_scalar_color()

    # Calc avg r, g and b values over an entire image.
    def avg_rgb(self):
        total = float(self.xmax * self.ymax)
        sum_r, sum_g, sum_b = 0.0, 0.0, 0.0
        for i in range(self.xmax):
            for j in range(self.ymax):
                r,g,b = self.get_pixmap_rgb(i,j)
                sum_r, sum_g, sum_b = sum_r + r, sum_g + g, sum_b + b
        return [sum_r/total, sum_g/total, sum_b/total]

    # Returns an array of average band strengths, one per column.  band = red, green, blue, gray or bw(black-white)
    def column_avg(self,band='red'):
        k = self.get_pixel_index(band)
        a = n_of(self.xmax,0.0)
        for i in range(self.xmax):
            sum_band = 0
            for j in range(self.ymax):
                p = self.get_pixmap_rgb(i,j)
                sum_band += p[k]
            a[i] = float(sum_band)/float(self.ymax)
        return a

    def column_avg3(self):
        return [self.column_avg(band) for band in ['red','green','blue']]

    # Apply func to each R,G,B triple of the image, returning an array of whatever type that func returns.

    def map_pixels(self,func):
        init_elem = func(self.get_pixmap_rgb(0,0))
        a = [[init_elem for y in range(self.ymax)] for x in range(self.xmax)] # Create the array
        for i in range(self.xmax):
            for j in range(self.ymax):
                a[i][j] = func(self.get_pixmap_rgb(i,j))
        return a

    def gen_binary_image(self,thresh = 1):
        def gen_binary_pixel(rgb):
            return 1 if (rgb[0] + rgb[1] + rgb[2]) >= thresh else 0
        return self.map_pixels(gen_binary_pixel)

    # The func is applied to each pixel to produce an integer.  This allows all types of scaling.

    def gen_integer_image(self,func=None):
        def gen_scalar_pixel(rgb):
            return (rgb[0] + rgb[1] + rgb[2])
        f = func if func else gen_scalar_pixel
        return self.map_pixels(f)

    # The array (a) is anything derived from the rgb pixel array, so it's in column-major format.
    def transpose_pixel_array(self,a):
        rows, cols = self.ymax, self.xmax # The flipping is done right here, since num rows become length y axis, etc.
        init_elem=a[0][0]
        a2 = [[init_elem for c in range(cols)] for r in range(rows)]
        for r in range(rows):
            for c in range(cols):
                a2[r][c] = a[c][r]
        return a2

    # Arrays corresponding to the pixmap are stored in column-major format (i.e. items in the same column are
    # contiguous in memory), but to display in a file, it helps to put stuff in row-major format by transposing
    # the array

    def file_dump_pixel_array(self,fid,a,gap=''):
        a2 = self.transpose_pixel_array(a)
        rows = len(a2); cols = len(a2[0])

        def row_to_str(r):
            s = ''
            for item in a2[r]:
                s +=  gap + str(item)
            return s

        strings = [row_to_str(r) for r in range(rows)]
        file_dump_strings(fid,strings)

## ****** Image Filtering methods **************
##   This uses the PIL ImageFilter module to get various filters, which are then applied to the image using
##   the "filter" method for PIL's image class.

    def filter(self,imagefilter):
        return Imager(image=self.image.filter(imagefilter))

    def blur(self,radius=2): return self.filter(PIF.GaussianBlur(radius))

    def contour(self): return self.filter(PIF.CONTOUR)
    def emboss(self):  return self.filter(PIF.EMBOSS)

    # size = an ODD integer, else error message.  It's the width and height of the MedianFilter, which must have a
    # unique center pixel.

    def smooth(self,size=3): return self.filter(PIF.MedianFilter(size))


##  ***** Image Enhancement Methods ********
##  This uses the PIL ImageEnhance module.  These enhancements include a control factor, a real number (pos or neg).
##  factor == 1 => no change; factor < 1 => reductions in color; factor > 1 => MORE color than in the original.

    def sharpen(self,factor):
        enhancer = PIE.Sharpness(self.image)  # 2-step process:  create enhancer, then call "enhance" on it.
        return Imager(image=enhancer.enhance(factor))

    def brighten(self,factor): return Imager(image=PIE.Brightness(self.image).enhance(factor))

    def contrast(self,factor):  return Imager(image=PIE.Contrast(self.image).enhance(factor))

    ### Combining imagers in various ways.

    ## The two concatenate operations will handle images of different sizes
    def concat_vert(self,im2=False,background='black'):
        im2 = im2 if im2 else self # concat with yourself if no other imager is given.
        im3 = Imager()
        im3.xmax = max(self.xmax,im2.xmax)
        im3.ymax = self.ymax + im2.ymax
        im3.image = im3.gen_plain_image(im3.xmax,im3.ymax,background)
        im3.paste(self,0,0)
        im3.paste(im2, 0,self.ymax)
        return im3

    def concat_horiz(self,im2=False,background='black'):
        im2 = im2 if im2 else self # concat with yourself if no other imager is given.
        im3 = Imager()
        im3.ymax = max(self.ymax,im2.ymax)
        im3.xmax = self.xmax + im2.xmax
        im3.image = im3.gen_plain_image(im3.xmax,im3.ymax,background)
        im3.paste(self, 0,0)
        im3.paste(im2, self.xmax,0)
        return im3

    # This requires self and im2 to be of the same size
    def morph(self,im2,alpha=0.5):
        im3 = Imager(width=self.xmax,height=self.ymax) # Creates a plain image
        for x in range(self.xmax):
            for y in range(self.ymax):
                rgb = self.combine_pixels(self.get_pixel(x,y), im2.get_pixel(x,y), alpha=alpha)
                im3.set_pixel(x,y,rgb)
        return im3

    def morph4(self,im2):
        im3 = self.morph(im2,alpha=0.66)
        im4 = self.morph(im2,alpha=0.33)
        return self.concat_horiz(im3).concat_vert(im4.concat_horiz(im2))

    def morphroll(self,im2,steps=3):
        delta_alpha = 1/(1+steps)
        roll = self
        for i in range(steps):
            alpha = (i + 1)*delta_alpha
            roll = roll.concat_horiz(self.morph(im2,1-alpha))
        roll = roll.concat_horiz(im2)
        return roll

    def split4(self,levels=1):
        def rec(dx,dy,level):
            if level == 0:
                return self.resize(dx,dy)
            else:
                im = rec(round(dx/2),round(dy/2),level-1)
                return im.concat_horiz().concat_vert()
        return rec(self.xmax,self.ymax,levels)

    def spiral(self,levels=3,toggle=True):
        im1 = self.scale(2/3,1)
        im2 = im1.scale(1/2,1/2)
        if levels == 0:
            im3 = im2.concat_vert(im2)
        else:
            rec = im2.spiral(levels-1,not(toggle))
            im3 = im2.concat_vert(rec) if toggle else rec.concat_vert(im2)

        return im1.concat_horiz(im3) if toggle else im3.concat_horiz(im1)

    # Put a picture inside a picture inside a picture....
    def tunnel(self,levels=5, scale=0.75):
        if levels == 0: return self
        else:
            child = self.scale(scale,scale) # child is a scaled copy of self
            child.tunnel(levels-1,scale)
            dx = round((1-scale)*self.xmax/2); dy = round((1-scale)*self.ymax/2)
            self.paste(child, dx,dy)
            return self

    def mortun(self,im2,levels=5,scale=0.75):
        return self.tunnel(levels,scale).morph4(im2.tunnel(levels,scale))

### *********** TESTS ************************

# Generate a binary text file from a normal file.

def grab_image(filename,intype='gif'):
    fid = fileops.build_default_file_path(filename, intype+'age')
    return Imager(fid)

def gen_bintext(filename,intype='gif',thresh=100,outype='txt'):
    fid1 = fileops.build_default_file_path(filename, intype+'age')
    fid2 = fileops.build_default_file_path(filename + '_bit', outype+'age')
    im = Imager(fid1)
    b = im.gen_binary_image(thresh)
    im.file_dump_pixel_array(fid2,b)


def ptest2(filename,type='jpeg',thresh=0.8,newsize=False):
    fid = fileops.build_default_file_path(filename,type+'age')
    im = Imager(fid)
    if newsize:
        im = im.resize(newsize,newsize)
    im2 = im.map_color_wta(thresh=thresh)
    im2.gen_colims()
    print(im2.center_of_mass(image=im2.colims[0]))
    im.display(); im2.colims[0].show()
    return [im,im2]

def ptest3(f1='kdfinger', f2="einstein",steps=3,newsize=250):
    fid1 = fileops.build_default_file_path(f1,'gifage'); fid2 = fileops.build_default_file_path(f2,'gifage')
    im1 = Imager(fid1); im2 = Imager(fid2)
    im1 = im1.resize(newsize,newsize); im2 = im2.resize(newsize,newsize)
    roll = im1.morphroll(im2,steps=steps)
    roll.display()
    return roll

def ptest4(f1='einstein',f2='tunnel',levels=3,newsize=250,scale=0.8):
    fid1 = fileops.build_default_file_path(f1,'gifage')
    outfid = fileops.build_default_file_path(f2,'gifage',extension='gif')
    im1 = Imager(fid1);
    im1 = im1.resize(newsize,newsize);
    im2 = im1.tunnel(levels=levels,scale=scale)
    im2.display()
    im2.dump_image(outfid)
    return im2

def ptest5(f1='kdfinger', f2="einstein",steps=3,newsize=250):
    fid1 = fileops.build_default_file_path(f1,'gifage'); fid2 = fileops.build_default_file_path(f2,'gifage')
    im1 = Imager(fid1); im2 = Imager(fid2)
    im1 = im1.resize(newsize,newsize); im2 = im2.resize(newsize,newsize)
    roll = im1.morphroll(im2,steps=steps)
    roll = roll.concat_vert().split4().spiral(3)
    roll.display()
    roll.dump_image(build_default_file_path('testout','gifage',extension='gif'))
    return roll

def ptest6(f1='kdfinger', f2="einstein",newsize=250,levels=4,scale=0.75):
    fid1 = fileops.build_default_file_path(f1,'gifage'); fid2 = fileops.build_default_file_path(f2,'gifage')
    im1 = Imager(fid1); im2 = Imager(fid2)
    im1 = im1.resize(newsize,newsize); im2 = im2.resize(newsize,newsize)
    box = im1.mortun(im2,levels=levels,scale=scale)
    box.display()
    box.dump_image(build_default_file_path('testout','gifage',extension='gif'))
    return box

def wta_test(f1='birds',f2='purebirds',in_ext='jpeg',out_ext='gif'):
    in_fid = fileops.build_default_file_path(f1,in_ext+'age')
    out_fid = fileops.build_default_file_path(f2,out_ext+'age')
    out_fid2 = fileops.build_default_file_path(f1,out_ext+'age')
    im1 = Imager(in_fid)
    im2 = im1.map_color_wta()
    im1.dump_image(out_fid2)
    im2.dump_image(out_fid)


def reformat(fid,in_ext='gif',out_ext='jpeg',scalex=1.0,scaley=1.0):
    in_fid = fileops.build_default_file_path(fid,in_ext+'age')
    out_fid = fileops.build_default_file_path(fid,out_ext+'age')
    im = Imager(in_fid)
    im = im.scale(scalex,scaley)
    im.dump_image(out_fid)



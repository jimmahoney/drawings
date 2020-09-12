"""drawing.py

about
=====
 
A graphics library for use in jupyter[1] python notebooks, 
built on top of the ipycanvas[2] package, 
with an API similar to parts of Zelle's graphics[3] library.

It can draw pictures made up of points, text, circles, lines,
rectangles, polygons, and even "crude" lines (something like
hand-drawn lines) from a cell in a jupyter notebook.

Here's an example.

    from drawing import *
    image = Drawing(400, 400)
    image.set_coords(0, 0, 1, 1)
    image.add( Polygon([Point(0.3,.4), Point(0.5,0.9), Point(0.8,0.4)]) )
    image.add( Text( Point(0.2, 0.1), "It's a triangle!") )
    image.draw()

To use this library, the workflow is

   (1) Create a drawing object.
   (2) Add Shape objects to it.
   (3) Draw it.

API
===

Here are the supplied classes and functions.

  Drawing

      The Drawing contains all the shapes to be drawn.

      drawing = Drawing(width, height)    # size in pixels

                Optional arguments and their default values are :
                  background   = '#eeeeeeff'     # nearly white opaque 
                  border       = '#666666ff'     # grey opaque
                  border_width = 2               # in pixels

      drawing.set_coords(xll, yll, xur, yur)     

         The coordinate system for the drawing and all its shapes
         can be set by defining a lower-left and upper-right corner.
         If not set, the default values are 
             (xll, yll) = (0, height)
             (xur, yur) = (width, 0)
         which puts (0,0) at the top left with  y increasing down.

      drawing.add(shape)                  # Add a shape (see below).

      drawing.draw()                      # display the drawing.

      drawing.to_file('filename.png')     # After being displayed, a drawing
                                          # can be saved as a PNG image file.

  Shapes 

      All the other classes represent graphical elements within the drawing,
      most with similar parameters.

          shapes                               optional arguments
          -----                                ------------------
          Point(x, y)                          color
          Text(point, message)                 color, face
          Line(point1, point2)                 color, line_width
          CrudeLine(point1, point2)            color, line_width, crudity             
          Circle(point, radius)                color, outline, line_width
          Rectangle(point1, point2)            color, outline, line_width
          Polygon([points])                    color, outline, line_width

      Colors are given by a string, either names as defined in the CSS standard
      or as CSS hex string starting with #, such as '#ff00cc' (r,g,b 0 to 255) 
      or '#00ff00cc' (r,g,b,t) where t is the transparency, also from 0 to 255.
      Google "CSS color" for more information on these data types.

      Two color conversion utility functions are provided which can generate 
      color strings from (red,green,blue) or (r,g,b,t) values : 

          color_css_string = color_rgb(red, green, blue)
          color_css_string = color_rgbt(red, green, blue, transparency)

      The Point class can be displayed, but is primarily intended 
      for defining the positions of the other shapes. Points can
      be added and subtracted from each other, acting as two dimensional
      vectors. Scalar multiplication and the dot product are also supported.
      Points have one optional argument, color.

      The Text class displays a character string, with its left starting
      position defined by the given point. The font and text size can
      be set by the face string argument, which behaves much like the
      CSS font property. For example, face="12px sans-serif" or
      face="8px Times".

      The Line and CrudeLine classes draw a line between two points.
      The width can be adjusted with the line_width optional argument
      (whose units are pixels, not changed by set_coords.) 

      A CrudeLine is an approximately placed, not-quite-straight line,
      which is intended to imitate a hand-drawn line. Its "crudity"
      optional argument, in pixels, sets roughly how far off the 
      ends will be from their given position. 

      The Rectangle, Circle, and Polygon may be filled in, have an 
      outline, or both. The outline argument gives the color of
      the outline; if omitted then the outline is omitted. The 
      width of the outline is given by the line_width parameter.

complications 
=============

The simplest way to make a drawing appear, the .draw() method, has
several limitations. A few other alternatives are implemented here,
but all have their own issues.

    I) notebook saved images: drawing.render() ... drawing.display()

      The first issue is that .draw() does not put the graphics 
      display into the jupyter notebook in a way that is saved when 
      the notebook is saved. This means that if you download the 
      notebook using "save_as_html", the drawing will not be part
      of the .html file. 

      An alternative to .draw() that does put save the graphics
      in the notebook is to (a) .render() the drawing, and 
      then in a different notebook cell (after the drawing 
      has finished processing), (b) call .display() to show it.
      
      Then when the notebook is downloaded with "save as html",
      the images are visible.

      However, this does not work all in one cell: the drawing must 
      be completely evaluated before .render() is called.

    I) animations : drawing.show()

      The second issue is animated drawings - things that change or move.

      The .draw() method shows the drawing all at once, with the 
      underlying ipycanvas cache set to True, which has the advantage
      of being fast but does not permit animations.

      The draw.show() method is the start of allowing animations,
      since it displays graphics as soon as jupyter is ready.
      However, it uses a call-back routine which means that runtime
      errors fail silently. 

      While animations were working in an earlier version of this
      software, they are not yet supported here.

coordinates       
===========

The underlying canvas API allows for floating point coordinates,
which is part of the model of the smooth bezier curves and paths
supported by the underlying web canvas display system.

So even though the drawings are displayed in terms of pixels,
the default coordinate system actually refers to the edges of 
those pixels.

Consider for example a canvas with a height of 2 pixels and width of 4
pixels. Using the default coordinate system, that looks like this :

         +----+----+----+----+           0  = y
         |    |    |    |    |
         |    |    |    |    |
         +----+----+----+----+           1
         |    |    |    |    |
         |    |    |    |    |
         +----+----+----+----+           2

         0    1    2    3    4  = x

credits
=======

Tested with python 3.6.7, jupyterhub 0.9.4, and ipycanvas 0.4.6.
  
* [1] jupyter : https://jupyter.org
* [2] ipycanvas : https://ipycanvas.readthedocs.io/en/latest/
* [3] Zelle's graphics : https://mcsp.wartburg.edu/zelle/python/
 
Jim Mahoney | cs.bennington.college | September 2020 | MIT License

"""

from ipycanvas import Canvas
import random, time
import numpy as np
from numpy import pi, sqrt, sin, cos, abs
import matplotlib.pyplot as plt

def color_rgb(red, green, blue):
    """ Given three intensities red, green, blue, all from 0 to 255,
        returns the corresponding CSS color string e.g. '#ff00cc' """
    return f"#{red*256**2 + green*256 + blue:06x}"
assert color_rgb(255, 255, 255) == '#ffffff'  # tests
assert color_rgb(0, 64, 255)  == '#0040ff'
assert color_rgb(0, 0, 0) == '#000000'

def color_rgbt(red, green, blue, transparency):
    """ Given four intensities red, green, blue, transparency,
        all from 0 to 255, returns the corresponding CSS 
        color string e.g. '#ff00ccff' """
    return f"#{red*256**3 + green*256**2 + blue*256 + transparency:08x}"
assert color_rgbt(255, 255, 255, 255) == '#ffffffff'
assert color_rgbt(0, 64, 255, 128)  == '#0040ff80'
assert color_rgbt(0, 0, 0, 255) == '#000000ff'


class Drawing(Canvas):
    """ A drawing made of shapes. """

    defaults = {
        'background' : '#eeeeeeff',  # nearly white opaque 
        'border' : '#666666ff',      # grey opaque
        'border_width' : 2,          # pixels
        'cache_default': True,       # display all components at end 
        'sync_image_data' : True     # needed for get_image_data()
    }
        
    def __init__(self, width=500, height=500, **kwargs):
        # Examples : 
        #   Drawing(border=None)            # omit border
        #   Drawing(background='white')     # white rather than default 
        #   Drawing(800, 200)               # 800 pixels wide, 200 pixels high
        for key in Drawing.defaults.keys():
            if kwargs.get(key, None) == None:
                kwargs[key] = Drawing.defaults[key]
        kwargs['caching'] = kwargs.get('caching',
                                       Drawing.defaults['cache_default'])
        Canvas.__init__(self, width=width, height=height, **kwargs)
        for key in Drawing.defaults.keys():
            self.__dict__[key] = kwargs[key]
        self.width = width
        self.height = height
        self.caching = kwargs['caching']
        self.components = []
        #
        (self.xll, self.yll) = (0.0, 1.0 * height)
        (self.xur, self.yur) = (1.0 * width, 0.0)

    def set_coords(self, xll, yll, xur, yur):
        """ Set the drawing coordinate system
            where ll is 'lower left' and ur is 'upper right' """
        self.xll = xll
        self.yll = yll
        self.xur = xur
        self.yur = yur

    def _xy(self, x, y):
        """ convert drawing coords (x,y) to canvas coords (_x,_y)
            with  0 <= _x <= width , 0 <= _y <= height """
        _x = (x - self.xll) * self.width / (self.xur - self.xll)
        _y = (self.yur - y) * self.height / (self.yur - self.yll)
        return (_x, _y)
    def _size(self, xsize, ysize=None):
        """ convert drawing sizes to canvas _sizes ,  using x scale """
        _xsize = xsize * self.width / abs(self.xur - self.xll)
        if ysize != None:
            _ysize = ysize * self.height / abs(self.yur - self.yll)
            return (_xsize, _ysize)
        else:
            return _xsize

    # To override all the canvas drawing routines with a new cord system,
    # translating (x,y) to (_x, _y), would take a lot of wrappers ...
    # so at this point I'm just modifying the _render() methods of shapes.
    #def fill_rect(self, x, y, width, height=None): pass
    #def fill_rects(self, x, y, width, height=None): pass
    #def stroke_rect(self, x, y, width, height=None): pass
    #def stroke_rects(self, x, y, width, height=None): pass
    #def clear_rect(x, y, width, height=None)
    #def fill_arc(self, x, y, radius, theta0, theta1): pass
    #def fill_arcs(self, x, y, radius, theta0, theta1): pass
    #def stroke_arc(self, x, y, radius, theta0, theta1): pass
    #def stroke_arcs(self, x, y, radius, theta0, theta1): pass
    #def move_to(self, x, y): pass
    #def line_to(self, x, y): pass
    #def line_width(self, size): pass
    #def rect(self, x, y, width, height): pass
    #def arc(self, x, y, width, height, anticlockwise=False): pass
    #def draw_image(self, image, x=0, y=0, width=None, height=None ): pass
    # and the text and image routines ... ugh.
    
    def add(self, shape):
        """ Add a shape to this drawing. """
        # And remember this drawing in the shape.
        shape.drawing = self
        self.components.append(shape)

    def _myflush(self):
        """ flush if caching and reset """
        if self.caching:
            self.flush() # side-effect: sets caching=False
            self.caching = self.cache_default        
        
    def _init_render(self):
        """ Initalize drawing with default background color and border """
        self.save()
        self.clear()
        if self.background:
            self.fill_style = self.background
            self.fill_rect(0, 0, self.width, self.height)
        if self.border:
            self.line_width = self.border_width
            self.stroke_style = self.border
            self.stroke_rect(0, 0, self.width, self.height)
        self._myflush()
        self.restore()
        
    def render(self):
        """ Render this drawing and its components. """
        # This call alone doesn't make the drawing visible;
        # use .draw() or .show() or .display() to do that.
        self._init_render()
        for component in self.components:
            component.render()
        self._myflush()

    def display(self):
        """ Display a rendered drawing in a second jupyter notebook cell """
        # Pros: 
        #   * saves images in notebook, same as matplotlib plots.
        # Cons: 
        #   * won't work for animations or interective widgets
        #   * requires both render and display calls in two different cells. 
        # Example :
        #    ----- cell 1 -------------------
        #    |  d = Drawing(100, 100)
        #    |  d.add( Line( Point(10, 10), Point(80, 90), 'red')
        #    |  d.render()
        #    ---------------------------------
        #      <image, only visible after cell evaluation>
        #    ----- cell 2 ----------------------
        #    | d.display()
        #    ------------------------------------
        #      <image , saved in notebook, part of "download as HTML" >
        #
        # HMMM ...
        # If I evaluate the cells as above one at a time, this works fine.
        #
        # But if I instead restart the kernel and evaluate all cells from 
        # the notebook menu, the image data is not available when .display()
        # is called ... so I guess this is just too fragile and unreliable.
        #
        # It is also possible to save a drawing to a file with 
        # self.to_file('filename.png') however this too like display() 
        # requires that the image_data be available.
        #
        dpi = 300
        plt.figure(figsize=(self.width/dpi, self.height/dpi), dpi=dpi)
        ax = plt.axes([0,0,1,1], frameon=False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        plt.autoscale(tight=True)
        try:
            plt.imshow(self.get_image_data())
        except Exception as e:
            print("Display failed; " 
                  "image data not yet available. \n" 
                  "Draw or render first then try again in another cell.")

    def write_file(self, filename='drawing.png'):
        """ Write drawing to a .png file """
        # If the filename doesn't end in .png, append .png.
        if filename[-4:] != '.png':
            filename += '.png'
        try:
            self.to_file(filename)
        except Exception as e:
            print(f"Saving to '{filename}' failed; \n"
                   "image data not yet available. \n" 
                   "Draw or render first then try again in another cell.")
            
    def show(self):
        """ Show a drawing or animation once jupyter is ready """
        # Pros: 
        #   * all in one cell
        #   * allows for animations
        #     displaying components and modifications dynamically
        # Cons: 
        #   * errors fail silently in the callback handler
        #   * the displayed images is only visible after the cell is evaluated;
        #     it isn't saved in the notebook or in "download as HTML"
        # Example :
        #    ----- cell 1 -------------------
        #    |  d = Drawing(100, 100)
        #    |  d.add( Line( Point(10, 10), Point(80, 90), 'red') )
        #    |  d.show()
        #    ---------------------------------
        self.caching = False
        self.on_client_ready(lambda:self.render())
        return self
    
    def draw(self):
        """ Draw this drawing below the current jupyter notebook cell
            in the client-side browser window. """
        #
        # This is the recommended approach.
        #
        # Pros:
        #  * all in one cell
        #  * good for debugging, since error messages appear as expected
        #  * uses the typical ipycanvas approach
        # Cons:
        #  * the displayed images is only visible after the cell is evaluated,
        #    drawn with an HTML5 js canvas in the client-side browser window.
        #    And is therefore not in the server-side notebook itself and not
        #    in the in "download as HTML" representation of the notebook.
        # Example:
        #    ----- cell 1 -------------------
        #    |  d = Drawing(100, 100)
        #    |  d.add( Line( Point(10, 10), Point(80, 90), 'red') )
        #    |  d.draw()
        #    ---------------------------------
        self.render()
        return self

default_color = '#111111cc' # dark mostly opaque (default off-white background)
default_line_width = 2      # pixel width of outline or line

class Shape:
    """ A graphics component within a drawing """
    def __init__(self, x=0, y=0,
                 color=default_color, outline=None, line_width=default_line_width):
        # Zelle uses "fill" for what I'm calling "color" ... it's fill_color, eh?
        # And outline is actually outline_color. 
        self.x = x
        self.y = y
        self.color = color
        self.outline = outline
        self.line_width = line_width
    def clone(self):
        its_clone = copy.deepcopy(self)
        its_clone.drawing = None
        return its_clone
    def render(self):
        if self.drawing:
            self.drawing.save()
            self._render()
            self.drawing.restore()
    def _render(self):
        pass  # override this

def _average(values):
    """ Return average of a list of numbers """
    return sum(values)/len(values)

assert _average( (1, 2, 3) ) == 2, 'average of three integers'
assert _average( [10.0, 14.0] ) == 12.0, 'average of two floats'

def _is_number(x):
    """ True if x is numeric i.e. int or float """
    from numbers import Number
    return isinstance(x, Number)

assert _is_number(2) == True, 'integer is a number'
assert _is_number(3.2e-4) == True, 'float is a number'
assert _is_number('three') == False, 'string is not a number'

class Point(Shape):
    """ A 2D point with vector algebra. 
        (Usually not drawn but instead used to define Shapes.) """
    # implemented vector operations : 
    #   Point + Point    =>   Point
    #   Point - Point    =>   Point
    #   - Point          =>   Point
    #   Point * Point    =>   number   # dot product
    #   scalar * Point   =>   Point
    #   Point  * scalar  =>   Point
    #   Point == Point   =>   boolean
    def __init__(self, x, y, color=default_color):
        Shape.__init__(self, x=x, y=y, color=color)
    def __repr__(self):
        if self.color == default_color:
            its_color = ''
        else:
            its_color = ', color={self.color}'
        return f"Point({self.x}, {self.y}{its_color})"
    def _render(self):
        canvas = self.drawing
        canvas.fill_style = self.color
        (_x, _y) = canvas._xy(self.x, self.y) # convert to canvas coords
        canvas.fill_arc(_x, _y, 1, 0.0, 2*pi) # radius 1 pixel
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.color)
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.color)
    def __neg__(self):
        return Point(-self.x, -self.y, self.color)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __rmul__(self, other):
        return Point.__mul__(self, other)
    def __mul__(self, other):
        if _is_number(other):
            # scalar multiplication
            return Point(other * self.x, other * self.y, self.color)
        elif isinstance(other, Point):
            # dot product
            return self.x * other.x + self.y * other.y
        else:
            return NotImplemented

_point_a = Point(3, 4)
_point_b = Point(5.0, -1.0)
assert (_point_a + _point_b).x == 8.0, 'Point addition'
assert  _point_a * _point_b == 11.0, 'Point dot product'
assert _point_a * 2 == Point(6.0, 8.0), 'Point scalar product, point first'
assert 3 * _point_b == Point(15.0, -3.0), 'Point scalar product, scalar first'
        
class Circle(Shape):
    """ A circle defined by its center Point and radius """
    # The drawing.set_coords() allows the x and y axes to have their own scales,
    # which means that circles will turn into ellipses if they're different.
    def __init__(self, center=Point(20, 20), radius=10, color=default_color,
                 outline=None, line_width=default_line_width):
        Shape.__init__(self, x=center.x, y=center.y,
                       color=color, outline=outline, line_width=line_width)
        self.radius = radius
    def _render(self):
        canvas = self.drawing
        canvas.begin_path()
        (_x, _y) = canvas._xy(self.x, self.y) # convert to canvas coords
        (_xradius, _yradius) = canvas._size(self.radius, self.radius)
        #canvas.ellipse(_x, _y, _xradius, _yradius, 0.0, 0.0, 2*pi)
        # ellipse is in in web canvas ... not in ipycanvas ?
        # See github.com/martinRenou/ipycanvas/blob/master/ipycanvas/canvas.py
        canvas._send_canvas_command('ellipse',
                      (_x, _y, _xradius, _yradius, 0.0, 0.0, 2*pi))
        if self.color:
            canvas.fill_style = self.color
            canvas.fill()
        if self.outline:
            canvas.stroke_style = self.outline
            canvas.line_width = self.line_width
            canvas.stroke()
            
class Line(Shape):
    """ A straight line between two Points """
    def __init__(self, p0=Point(10,10), p1=Point(30,40),
                 color=default_color, line_width=default_line_width):
        Shape.__init__(self, x=(p0.x + p1.x)/2, y=(p0.y + p1.y)/2,
                       color=color, line_width=line_width)
        self.p0 = p0
        self.p1 = p1
    def _render(self):
        canvas = self.drawing
        canvas.begin_path()
        canvas.line_width = self.line_width
        canvas.stroke_style = self.color
        (_x0, _y0) = canvas._xy(self.p0.x, self.p0.y)
        (_x1, _y1) = canvas._xy(self.p1.x, self.p1.y)
        canvas.move_to(_x0, _y0)
        canvas.line_to(_x1, _y1)
        canvas.stroke()

class Polygon(Shape):
    def __init__(self, points,
                 color=default_color, outline=None, line_width=default_line_width):
        xs = list(p.x for p in points)
        ys = list(p.y for p in points)
        (x, y) = (_average(xs), _average(ys))
        Shape.__init__(self, x=x, y=y,
                       color=color, outline=outline, line_width=line_width)
        self.points = points
    def _trace(self):
        canvas = self.drawing
        if self.points:
            canvas.begin_path()
            (_x, _y) = canvas._xy(self.points[0].x, self.points[0].y)
            canvas.move_to(_x, _y)
            for p in self.points[1:]:
                (_x, _y) = canvas._xy(p.x, p.y)
                canvas.line_to(_x, _y)
            canvas.close_path()
    def _render(self):
        canvas = self.drawing
        self._trace()
        if self.color:
            canvas.fill_style = self.color                    
            canvas.fill()
        if self.outline:
            canvas.stroke_style = self.outline
            canvas.line_width = self.line_width
            canvas.stroke()

class Text(Shape):
    def __init__(self, position=Point(10,10), text="Hello.", 
                 face="24px serif", color=default_color):
        Shape.__init__(self, x=position.x, y=position.y, color=color)
        self.text = text
        self.face = face
        self.position = position
    def _render(self):
        canvas = self.drawing
        canvas.font = self.face
        canvas.fill_style = self.color
        (_x, _y) = canvas._xy(self.position.x, self.position.y)
        canvas.fill_text(self.text, _x, _y)
            
class Rectangle(Shape):
    """ An orthogonal box defined by two corner points. """
    def __init__(self, p0=Point(10,10), p1=Point(30,50), 
                 color=default_color, outline=None, line_width=default_line_width):
        Shape.__init__(self, (p0.x + p1.x)/2, (p0.y + p1.y)/2, 
                       color=color, outline=outline, line_width=line_width)
        self.p0 = p0
        self.p1 = p1
        self.rect_width = abs(p1.x - p0.x)
        self.rect_height = abs(p1.y - p0.y)
    def _render(self):
        canvas = self.drawing
        # The web canvas api needs the top left corner.
        (_x, _y) = canvas._xy(self.p0.x, self.p1.y)
        (_width, _height) = canvas._size(self.rect_width, self.rect_height)
        if self.color:
            canvas.fill_style = self.color
            canvas.fill_rect(_x, _y, _width, _height)
        if self.outline:
            canvas.stroke_style = self.outline
            canvas.line_width = self.line_width
            canvas.stroke_rect(_x, _y, _width, _height)
            
def _random_circle():
    """ Return random (x, y) within a circle at (0,0) with radius 1 """
    
    # I always have to think about how to justify the sqrt() in this algorithm.
    
    # The argument goes something like this.
    
    #  * The random() function gives a uniform distribution from 0 to 1.
    #  * Points chosen randomly in circular area are likely to have larger r,
    #    since rings of width dr grow in size linearly; more area at larger r
    #    so they are not distributed in a uniform distribution.
    #  * If our random() function gives us lets say a value x=0.25,
    #    then what that means is that 25% of the uniform points are
    #    below that, and 75% of the uniform points are above.  We need
    #    to find the corresponding r for c(r), the circular
    #    probability distribution, that has that same property that
    #    25% of the r values are smaller, and 75% are bigger.
    #  * So what we really need to think about are not u(x) and c(r), but
    #    U(x) and C(r), the cumulative probability distributions, with
    #    dU/dx=u(x)=x and dC/dr=c(r)=2*x.  In this case, these
    #    cumulative distributions are U(x) = x and C(r) = r**2.

    #  * Let's make the defintions explicit.
    #       x = random variable 0 <= x < 1 with uniform probability.
    #       r = random variable 0 <= r < 1 with circle radius probability.
    #       u(x) = "probability density of finding x between x and x+dx" = 1
    #       c(r) = "probability densiity of finding r between r and r+dr" = 2*r
    #       U(x) = "cumulative probability of finding x' from 0 to x' = x
    #       C(r) = "cumulative probability of finding r' from 0 to r' = r**2
    #  * So at a give value like that 25% point,
    #       U=0.25=C, r=sqrt(C)=sqrt(0.25)=0.5.
    #    In other words, 25% of the circle has r<0.5, 75% has r>0.5.
    #  * Therefore what we want is 
    #       C(r) = U(x)           same cumulative prob. at corresponding r, x
    #       r = C_inverse(U(x))   general formula for random variables r, x
    #       r = sqrt(x)           this case
    (r, theta) = (sqrt(random.random()), 2*pi*random.random())
    return (r*cos(theta), r*sin(theta))

def _normalize(x, y):
    """ return (x_norm, y_norm) with unit length in same direction as (x,y) """
    _length = sqrt(x*x + y*y)
    return (x/_length, y/_length)

class CrudeLine(Shape):
    """ A crude "hand-drawn" line between two points """
    #
    # Given line endpoints (start, end) and a "crudity" parameter,
    # draw a fairly-but-not-quite straight line from points near the ends.
    #
    # With crudity=0 this is just a straight line. As the crudity (in pixels)
    # grows, the endpoints get sloppier and and the line becomes more bowed.
    #
    # Based on the discussion at 
    #     shihn.ca/posts/2020/roughjs-algorithms/
    # See also 
    #     en.wikipedia.org/wiki/Bézier_curve
    #     developer.mozilla.org/en-US/docs/Web/API/\
    #        CanvasRenderingContext2D/bezierCurveTo)
    #
    # Thhis line (well, Bézier curve) is defined by four points :
    #     A  -------   B   ----  C  ------ D
    # where
    
    #   A is within a circle centered at the start point with radius=crudity
    #   B is a Bézier control point (i.e. not in the line),
    #     setting an A -> B tangent to the curve at A,
    #     placed (0.45 to 0.55) along length and (0.3 to 0.6) above the line,
    #   C is a similar Bézier control point,
    #     setting the C -> D tangent to the curve at D,
    #     placed (0.65 to 0.75) along length and again (0.3 to 0.6) above, and
    #   D is within a circle centered at the end point with radius=crudity.
    #
    def __init__(self, p0=Point(10,10), p1=Point(40,50), 
                 color=default_color, line_width=default_line_width, crudity=3):
        self.p0 = p0
        self.p1 = p1
        (_xa, _ya) = _random_circle()
        self.xa = xa = p0.x + _xa * crudity
        self.ya = ya = p0.y + _ya * crudity
        #
        (_x_para, _y_para) = _normalize(p1.x - p0.x, p1.y - p0.y) # parallel 
        _length = sqrt((p1.x - p0.x)**2 + (p1.y - p0.y)**2)
        (_x_perp, _y_perp) = (- _y_para, _x_para)                 # perpendic.
        #
        _b_para = 0.45 + 0.1 * random.random()
        _b_perp = 0.3 * (1 + random.random()) * crudity
        self.xb = p0.x + _b_para * _length * _x_para + _b_perp * _x_perp
        self.yb = p0.y + _b_para * _length * _y_para + _b_perp * _y_perp
        #
        _c_para = 0.65 + 0.1 * random.random()
        _c_perp = 0.3 * (1 + random.random()) * crudity
        self.xc = self.p0.x + _c_para * _length * _x_para + _c_perp * _x_perp
        self.yc = self.p0.y + _c_para * _length * _y_para + _c_perp * _y_perp
        #
        (_xd, _yd) = _random_circle()
        self.xd = xd = p1.x + _xd * crudity
        self.yd = yd = p1.y + _yd * crudity
        #
        Shape.__init__(self, x=(xa+xd)/2, y=(ya+yd/2), 
                       color=color, outline=None, line_width=line_width)
        self.crudity = crudity
    def _render(self):
        canvas = self.drawing
        canvas.begin_path()
        canvas.line_width = self.line_width
        canvas.stroke_style = self.color
        (_xa, _ya) = canvas._xy(self.xa, self.ya)
        (_xb, _yb) = canvas._xy(self.xb, self.yb)
        (_xc, _yc) = canvas._xy(self.xc, self.yc)
        (_xd, _yd) = canvas._xy(self.xd, self.yd)
        canvas.move_to(_xa, _ya)
        canvas.bezier_curve_to(_xb, _yb, _xc, _yc, _xd, _yd)
        canvas.stroke()
        #if False:
        #    # debugging by drawing its four bezier points
        #    for (x,y) in ((self.xa, self.ya), (self.xb, self.yb), 
        #                  (self.xc, self.yc), (self.xd, self.yd)):
        #        canvas.fill_style = 'red'
        #        canvas.fill_arc(x, y, 2, 0.0, 2*pi)

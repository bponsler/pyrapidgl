import sys
import math
import traceback

from PyQt4.QtCore import Qt, QPointF
from PyQt4.QtGui import QApplication, QImage, QColor, QPixmap
from PyQt4.QtOpenGL import QGLContext
from PyQt4.QtOpenGL import QGLWidget, QGLFormat, QGL

from OpenGL import GL, GLU


class RapidGLWindow(QGLWidget):
    # The background color for the world. This property should be a tuple
    # of three values (R, G, B) where each value is an integer in the
    # range [0, 255].
    BackgroundColor = (0, 0, 0)

    # The field of view for the camera
    FieldOfView = 45.0

    # The z values for the near and far perspective. Anything outside of
    # these z values will not be rendered.
    zNear = 1.0
    zFar = 100.0

    # Default camera position
    DefaultCameraX = 0
    DefaultCameraY = 10
    DefaultCameraZ = 0

    # Default camera rotation
    DefaultCameraRotateX = 0.0
    DefaultCameraRotateY = 0.0
    DefaultCameraRotateZ = 0.0

    # True to use default movement keys, False otherwise
    UseMovementKeys = True

    def __init__(self, *args, **kwargs):
        QGLWidget.__init__(self)
        self.__lastMousePos = None
        self.reset()

        self._onSetup(*args, **kwargs)

    ##### Protected functions #####

    def _getKeyCallbacks(self):
        return {}

    def _onSetup(self, *args, **kwargs):
        pass

    def _onQuit(self):
        pass

    def _onInitialize(self):
        pass

    def _onDraw(self):
        pass

    ##### Getters and setters #####

    def getCameraPosition(self):
        return self.__x, self.__y, self.__z

    def getCameraRotation(self):
        return self.__rotateX, self.__rotateY, self.__rotateZ

    ##### Utility functions #####

    def reset(self):
        # Keep track of the position of the camera
        self.__x = self.DefaultCameraX
        self.__y = self.DefaultCameraY
        self.__z = self.DefaultCameraZ

        # Set up the rotation values
        self.__rotateX = self.DefaultCameraRotateX
        self.__rotateY = self.DefaultCameraRotateY
        self.__rotateZ = self.DefaultCameraRotateZ

    def drawSphere(self, radius, lats, lons):
        '''Draw a sphere.

        * radius -- The radius for the sphere
        * lats -- The number of latitude slices
        * lons -- The number of longitude slices

        '''
        # Traverse through all of the latitude slices
        for i in range(lats + 1):
            # Get the z values for the latitude slices on
            # both sides of the current index
            z0, zr0 = self.__getLat(i - 1, radius, lats)
            z1, zr1 = self.__getLat(i, radius, lats)

            GL.glBegin(GL.GL_QUAD_STRIP)

            # Traverse all of the longitude slices
            for j in range(lons + 1):
                # Determine the current longitude angle 
                lonAngle = (2 * math.pi) * float(j - 1) / float(lons)

                # Calculate the x and y position for the longitude
                x = math.cos(lonAngle)
                y = math.sin(lonAngle)
    
                GL.glNormal3f(x * zr0, y * zr0, z0)
                GL.glVertex3f(x * zr0, y * zr0, z0)
                GL.glNormal3f(x * zr1, y * zr1, z1)
                GL.glVertex3f(x * zr1, y * zr1, z1)

            GL.glEnd()

    def createTexture(self, filename):
        '''Create a texture for the given filename.

        * filename -- The filename

        '''
        image = QPixmap(filename)

        self.makeCurrent()
        texId = self.bindTexture(image,
                                 GL.GL_TEXTURE_2D,
                                 GL.GL_RGBA,
                                 QGLContext.LinearFilteringBindOption)
        self.doneCurrent()

        return texId

    ##### GL base functions #####

    def initializeGL(self):
        '''Override the initializeGL function.'''
        GL.glEnable(GL.GL_DEPTH_TEST);
        self._onInitialize()

    def resizeGL(self, width, height):
        '''Override the resizeGL function.

        * width -- The new width
        * height -- The new height

        '''
        # Tell OpenGL how to convert from coordinates to pixel values
        GL.glViewport(0, 0, width, height)

        # Switch to setting the camera perspective
        GL.glMatrixMode(GL.GL_PROJECTION)
    
        # Set the camera perspective
        GL.glLoadIdentity()
        GLU.gluPerspective(self.FieldOfView,
                           float(width) / float(height),
                           self.zNear, self.zFar)

    def paintGL(self):
        '''Override the paintGL function.'''
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.__setGLSettings()
        self.__drawScene()
        self.__revertGLSettings()

    ##### Mouse event functions #####

    def mouseDoubleClickEvent(self, event):
        '''Handle the mouse double click event.

        * event -- The mouse double click event

        '''
        button = event.button()

        if button & Qt.LeftButton:
            self.reset()
            self.updateGL()

    def mousePressEvent(self, event):
        '''Handle the mouse press event.

        * event -- The mouse press event

        '''
        self.__lastMousePos = event.posF()

    def mouseMoveEvent(self, event):
        '''Handle the mouse move event.

        * event -- The mouse move event

        '''
        diff = (event.posF() - self.__lastMousePos) / 50.0
        self.__lastMousePos = event.posF()

        self.__x += diff.x()
        self.__y += diff.y()

        self.updateGL()

    def wheelEvent(self, event):
        '''Event handler override for mouse scrolls
        
        * event -- The wheel event

        '''
        # Normalize the delta to get the direction desired zoom (-1/+1)
        direction = event.delta() / abs(event.delta())

        # Zoom the opposite of the scroll direction
        self.__z -= direction

    ##### Key event functions #####

    def keyPressEvent(self, event):
        '''Handle the key press event.

        * event -- The key press event

        '''
        key = event.key()

        if key == Qt.Key_Escape:
            try:
                self._onQuit()
            except:
                traceback.print_exc()

            sys.exit(0)

        elif self.UseMovementKeys and key == Qt.Key_Left:
            self.__x += 1

        elif self.UseMovementKeys and key == Qt.Key_Right:
            self.__x -= 1

        elif self.UseMovementKeys and key == Qt.Key_Up:
            self.__y += 1

        elif self.UseMovementKeys and key == Qt.Key_Down:
            self.__y -= 1

        elif self.UseMovementKeys and key in [Qt.Key_Plus, Qt.Key_Equal]:
            self.__z += 1

        elif self.UseMovementKeys and key == Qt.Key_Minus:
            self.__z -= 1

        elif self.UseMovementKeys and key == Qt.Key_W:
            self.__rotateX += 1

        elif self.UseMovementKeys and key == Qt.Key_S:
            self.__rotateX -= 1

        elif self.UseMovementKeys and key == Qt.Key_A:
            self.__rotateY += 1

        elif self.UseMovementKeys and key == Qt.Key_D:
            self.__rotateY -= 1

        elif self.UseMovementKeys and key == Qt.Key_L:
            self.__rotateZ -= 1

        elif self.UseMovementKeys and key == Qt.Key_P:
            self.__rotateZ += 1

        else:
            # Look for a user defined key callback
            keyMap = self._getKeyCallbacks()

            callback = keyMap.get(key, None)
            if callback is not None:
                callback(event)

        self.updateGL()

    ##### Drawing functions #####

    def __drawScene(self):
        '''Draw the scene.'''
        # Switch to the drawing perspective
        GL.glMatrixMode(GL.GL_MODELVIEW)
        # Reset the drawing perspective
        GL.glLoadIdentity()

        # Set up the camera such that it is looking straight ahead
        GLU.gluLookAt(self.__x, self.__y, self.__z,
                      self.__x, self.__y, self.__z + 1,
                      0, 1, 0)

        GL.glRotatef(self.__rotateX, 1, 0, 0)
        GL.glRotatef(-self.__rotateY, 0, 1, 0)
        GL.glRotatef(self.__rotateZ, 0, 0, 1)

        # Allow subclasses to draw
        self._onDraw()

    ##### Private initialization functions #####

    def __setGLSettings(self):
        '''Set the GL settings for texture mapping.'''
        GL.glEnable(GL.GL_TEXTURE_2D)

        # Get the color percents for the background color and set the
        # clear color using those percentages
        colors = (self.BackgroundColor[0],
                  self.BackgroundColor[1],
                  self.BackgroundColor[2])
        colors = map(lambda color: float(color) / 255.0, colors)
        GL.glClearColor(colors[0], colors[1], colors[2], 0.0)
        
        # alpha blending to remove black artifacts in images
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, 
                           GL.GL_NEAREST)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, 
                           GL.GL_NEAREST)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glViewport(0, 0, self.width(), self.height())

    def __revertGLSettings(self):
        '''Reverts back the GL settings for normal QT rendering.'''
        GL.glDisable(GL.GL_TEXTURE_2D)

    ##### Private helper functions #####

    def __bound(self, minimum, value, maximum):
        '''Bound a value to a minimum and maximum value.

        * minimum -- The minimum value
        * value -- The value
        * maximum -- The maximum value

        '''
        return min(maximum, max(minimum, value))

    def __getLat(self, index, radius, numLats):
        '''Get the latitude z values for a sphere.

        * index -- The latitude index
        * radius -- The radius of the sphere
        * numLats -- The number of latitude slices
        '''
        latAngle = math.pi * (-0.5 + float(index) / float(numLats))
        z = radius * math.sin(latAngle)
        zr =  radius * math.cos(latAngle)

        return z, zr

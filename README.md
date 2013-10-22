pyrapidgl
=========

A Python module for rapidly creating and testing OpenGL applications.

For example:

```python
from pyrapidgl import RapidGLWindow, createWindow

from OpenGL import GL


class TestWindow(RapidGLWindow):
    def _onDraw(self):
        GL.glColor3f(1.0, 0.0, 1.0)

        GL.glBegin(GL.GL_POLYGON)
        GL.glVertex3f(0, 0, 0)
        GL.glVertex3f(0, 0, 10)
        GL.glVertex3f(10, 0, 10)
        GL.glVertex3f(10, 0, 0)
        GL.glEnd()

if __name__ == '__main__':
    createWindow(TestWindow, 800, 600)
```

Documentation will come soon.
import sys

from PyQt4.QtGui import QApplication

from OpenGL import GL, GLU

from rapidWindow import RapidGLWindow


def createWindow(windowClass, width, height, *args, **kwargs):
    app = QApplication(sys.argv)
    window = windowClass(*args, **kwargs)
    window.resize(width, height)
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    class TestWindow(RapidGLWindow):
        def _onDraw(self):
            GL.glColor3f(1.0, 0.0, 1.0)

            GL.glBegin(GL.GL_POLYGON)
            GL.glVertex3f(0, 0, 0)
            GL.glVertex3f(0, 0, 10)
            GL.glVertex3f(10, 0, 10)
            GL.glVertex3f(10, 0, 0)
            GL.glEnd()


    createWindow(TestWindow, 800, 600)

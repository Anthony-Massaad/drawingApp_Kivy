import kivy
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import Color, InstructionGroup, Ellipse, Line, Rectangle
from kivy.core.window import Window
from kivy.uix.popup import Popup
Window.clearcolor = (1, 1, 1, 1)

class TheScreenManager(ScreenManager):
    pass

class TheScreen(Screen):
    pass


class BottomCanvasLayout(Widget):

    def exitPopUp(self):
        self._popup.dismiss()

    def showSave(self):
        content = SaveDialog(save=self.save_press, cancel=self.exitPopUp)
        self._popup = Popup(title="Save file (Automatic png)", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def showLoad(self):
        content = LoadDialog(load=self.load_press, cancel=self.exitPopUp)
        self._popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def save_press(self, filename):
        if filename[-1] == '\\':
            temp = filename[:len(filename)-1]
            filename = temp
        self.parent.ids.the_canvas.export_to_png(str(filename)+'.png')
        self.exitPopUp()

    def load_press(self, filename):
        path = filename[0]
        self.parent.ids.the_canvas.load_image(path)
        self.exitPopUp()

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    filename = ObjectProperty(None)
    cancel = ObjectProperty(None)

class PaintBoard(Widget):
    def __init__(self, **kwargs):
        super(PaintBoard, self).__init__(**kwargs)
        self.drawingSize = 5
        self.drawingColor = [0, 0, 0]
        self.allowed_to_draw = True
        self.drawing = False
        Window.bind(mouse_pos=self.get_mouse_pos)
        self.undoList = []
        self.drawings = []

    def on_touch_up(self, touch):
        self.drawing = False
        return super(PaintBoard, self).on_touch_up(touch)

    def on_touch_down(self, touch):
        if self.allowed_to_draw:
            r, g, b = self.drawingColor
            self.object_shape = InstructionGroup()
            self.object_shape.add(Color(r / 255, g / 255, b / 255, 1, mode='rgba'))
            self.object_shape.add(Ellipse(pos=(touch.x - self.drawingSize*2 / 2, touch.y - self.drawingSize*2 / 2), size=(self.drawingSize*2, self.drawingSize*2)))
            self.drawings.append(self.object_shape)
            self.canvas.add(self.object_shape)
            self.parent.ids.buttonsLayout.undo.disabled = False
        return super(PaintBoard, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.allowed_to_draw:
            if self.drawing:
                self.points.append(touch.pos)
                self.object_shape.children[-1].points = self.points
            else:
                self.drawing = True
                self.points = [touch.pos]
                r, g, b = self.drawingColor
                self.object_shape = InstructionGroup()
                self.object_shape.add(Color(r / 255, g / 255, b / 255, 1, mode='rgba'))
                self.object_shape.add(Line(width=self.drawingSize))
                self.drawings.append(self.object_shape)
                self.canvas.add(self.object_shape)
                self.parent.ids.buttonsLayout.undo.disabled = False
        return super(PaintBoard, self).on_touch_move(touch)

    def get_mouse_pos(self, instance, pos):
        self.drawingSize = self.parent.ids.buttonsLayout.slider.value
        if 0 <= pos[1] < 64 + (self.drawingSize*2/2):
            self.allowed_to_draw = False
            return
        self.allowed_to_draw = True

    def change_color(self, r, g, b):
        self.drawingColor[0], self.drawingColor[1], self.drawingColor[2] = r, g, b

    def clear(self):
        self.canvas.clear()
        self.drawings.clear()
        self.undoList.clear()
        self.parent.ids.buttonsLayout.redo.disabled = True
        self.parent.ids.buttonsLayout.undo.disabled = True

    def undo_press(self):
        item = self.drawings.pop(-1)
        self.undoList.append(item)
        self.canvas.remove(item)
        self.parent.ids.buttonsLayout.redo.disabled = False
        if len(self.drawings) == 0:
            self.parent.ids.buttonsLayout.undo.disabled = True

    def redo_press(self):
        item = self.undoList.pop(-1)
        self.drawings.append(item)
        self.canvas.add(item)
        self.parent.ids.buttonsLayout.undo.disabled = False
        if len(self.undoList) == 0:
            self.parent.ids.buttonsLayout.redo.disabled = False

    def load_image(self, source):
        self.canvas.add(Rectangle(source=source, pos=self.pos, size=self.size))


kv = Builder.load_file("mydrawingkivyfile.kv")


class MyDrawingApp(App):
    def build(self):
        return kv


if __name__ == "__main__":
    MyDrawingApp().run()

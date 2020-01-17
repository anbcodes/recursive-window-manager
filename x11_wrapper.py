from Xlib.display import Display
from Xlib import X, XK

class Wrapper:
  def __init__(self):
    self.dpy = Display()
    self.drag_start_event = None
    self.drag_attr = None
    self.on_alt_drag_handler = None
    self.on_alt_click_handler = None
    self.keys = {}
    self.screen_width = self.dpy.screen().width_in_pixels
    self.screen_height = self.dpy.screen().height_in_pixels
    self.gc = self.dpy.screen().root.create_gc(
            foreground = self.dpy.screen().black_pixel,
            background = self.dpy.screen().white_pixel,
            )
    self.on(lambda ev: print(ev._data), XK.XK_F1, X.Mod1Mask)
    self.on(lambda ev: print(ev._data), XK.XK_a, X.Mod1Mask)

  
  def on(self, func, key, modifier1 = 0, modifier2 = 0):
    self.keys[(key, modifier1, modifier2)] = func

  def on_alt_drag(self, func):
    self.on_alt_drag_handler = func
  
  def on_alt_drag_end(self, func):
    self.on_alt_drag_end_handler = func

  def on_alt_click(self, func):
    self.on_alt_click_handler = func

  def connect_key_combinations(self):
    for key in self.keys.keys():
      self.dpy.screen().root.grab_key(self.dpy.keysym_to_keycode(key[0]), key[1]|key[2], 1, 
        X.GrabModeAsync, X.GrabModeAsync)

    # self.dpy.screen().root.grab_key(X.AnyKey, X.AnyModifier, 1, 
    #   X.GrabModeAsync, X.GrabModeAsync)    
    self.dpy.screen().root.grab_button(1, X.Mod1Mask, 1, X.ButtonPressMask|X.ButtonReleaseMask|X.PointerMotionMask,
      X.GrabModeAsync, X.GrabModeAsync, X.NONE, X.NONE)
    self.dpy.screen().root.grab_button(3, X.Mod1Mask, 1, X.ButtonPressMask|X.ButtonReleaseMask|X.PointerMotionMask,
      X.GrabModeAsync, X.GrabModeAsync, X.NONE, X.NONE)
  def run(self):
    self.connect_key_combinations()
    while 1:
      event = self.dpy.next_event()
      self.dpy.screen().root.fill_rectangle(self.gc, 0, 0, self.screen_width, self.screen_height)

      if event.type == X.KeyPress:
        for handler, func in self.keys.items():
          if self.dpy.keycode_to_keysym(event.detail, 0) == handler[0] and event.state == handler[1]|handler[2]:
            func(event)
        # event.detail
        # print('\n', '\n'.join(dir(event)))
        # for item, value in event.__dict__.items():
        #   print(item, value)
        print(event._data, event.detail, self.dpy.keycode_to_keysym(event.detail, 0), chr(event.detail), XK.XK_F1)
        if self.dpy.keycode_to_keysym(event.detail, 0) == XK.XK_F1 and event.child != X.NONE:
          self.handle_move_to_front(event)
      elif event.type == X.ButtonPress:
        self.handle_drag_or_resize_start(event)
        if self.on_alt_click_handler:
          self.on_alt_click_handler(event)
      
  
      elif event.type == X.MotionNotify and self.drag_start_event:
        if (self.on_alt_drag_handler):
          xdiff = event.root_x - self.drag_start_event.root_x
          ydiff = event.root_y - self.drag_start_event.root_y
          self.on_alt_drag_handler((xdiff, ydiff), self.drag_attr, self.drag_start_event, event)
        # if self.drag_start_event.detail == 1:
        #   self.handle_move(event)
        # elif self.drag_start_event.detail == 3:
        #   self.handle_resize(event)
      elif event.type == X.ButtonRelease:
        if (self.on_alt_drag_end_handler):
          self.on_alt_drag_end_handler(self.drag_start_event, event)
        self.drag_start_event = None
  
  def handle_move_to_front(self, event):
    event.child.configure(stack_mode = X.Above)

  def handle_drag_or_resize_start(self, event):
    if event.child != X.NONE:
      self.drag_attr = event.child.get_geometry()

    self.drag_start_event = event
  
  def handle_move(self, event):
    xdiff = event.root_x - self.drag_start_event.root_x
    ydiff = event.root_y - self.drag_start_event.root_y
    self.drag_start_event.child.configure(
      x = self.drag_attr.x + xdiff,
      y = self.drag_attr.y + ydiff)
  def handle_resize(self, event):
    xdiff = event.root_x - self.drag_start_event.root_x
    ydiff = event.root_y - self.drag_start_event.root_y
    self.drag_start_event.child.configure(
      width = max(1, self.drag_attr.width + xdiff),
      height = max(1, self.drag_attr.height + ydiff))

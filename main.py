#!/home/andrew/.virtualenvs/pyWinManger/bin/python3
from Xlib import X, XK
import x11_wrapper
from Tile import Tile
import os
class Main:
  def __init__(self):
    os.system('sh $HOME/code/py/pwm/xterm.sh')
    self.wrapper = x11_wrapper.Wrapper()
    self.tile = Tile([0, 0], [self.wrapper.screen_width, self.wrapper.screen_height], self.wrapper.dpy.screen())
    self.tile.main = True
    self.wrapper.on_alt_drag(self.drag_handler)
    self.drag_middle = False
    self.drag_middle_tile = None
    self.start = None
    self.wrapper.on_alt_drag_end(self.drag_end_handler)
    self.wrapper.on_alt_click(self.alt_click_handler)
    self.wrapper.on(self.convert_to_tile, XK.XK_t, X.Mod1Mask)

  def convert_to_tile(self, ev):
    tile, slot_index = self.tile.get_deep_slot_in_xy(ev.root_x, ev.root_y)
    slot_geometry = tile.slot_geometrys[slot_index]
    new_tile = Tile([slot_geometry[0], slot_geometry[1]], [slot_geometry[2], slot_geometry[3]], self.wrapper.dpy.screen())
    new_tile.add_to_slots(tile.slots[slot_index], (0, 1, 2, 3))
    tile.slots[slot_index] = new_tile

  def alt_click_handler(self, event):
    center_drag = self.tile.is_in_center_deep(event.root_x, event.root_y)
    if event.child == X.NONE and center_drag:
      self.start = event
      self.drag_middle = True
      self.drag_middle_tile = center_drag[0]
  def drag_handler(self, distance, org_dim, start_event, event):
    if self.drag_middle and self.drag_middle_tile:
      self.drag_middle_tile.on_drag([event.root_x, event.root_y])
    if event.child == X.NONE or not org_dim:
      return
    
    if event.child != start_event.child:
      return

    self.tile.pop_out(event.child)
    event.child.configure(x = org_dim.x + distance[0], y = org_dim.y + distance[1] )
  
  def drag_end_handler(self, start, event):
    self.drag_middle = False

    if event.child == X.NONE:
      return

    hotspot = self.tile.get_deepest_hotspot(event.root_x, event.root_y)
    if hotspot:
      hotspot[0].add_to_slots(start.child, hotspot[1])
    
    print('END')

  def run(self):
    self.wrapper.run()

main = Main()
main.run()
# dpy = Display()

# dpy.screen().root.grab_key(dpy.keysym_to_keycode(XK.string_to_keysym("F1")), X.Mod1Mask, 1,
#         X.GrabModeAsync, X.GrabModeAsync)
# dpy.screen().root.grab_button(1, X.Mod1Mask, 1, X.ButtonPressMask|X.ButtonReleaseMask|X.PointerMotionMask,
#         X.GrabModeAsync, X.GrabModeAsync, X.NONE, X.NONE)
# dpy.screen().root.grab_button(3, X.Mod1Mask, 1, X.ButtonPressMask|X.ButtonReleaseMask|X.PointerMotionMask,
#         X.GrabModeAsync, X.GrabModeAsync, X.NONE, X.NONE)

# start = None
# while 1:
#     ev = dpy.next_event()
#     if ev.type == X.KeyPress and ev.child != X.NONE:
#         ev.child.configure(stack_mode = X.Above)
#     elif ev.type == X.ButtonPress and ev.child != X.NONE:
#         attr = ev.child.get_geometry()
#         start = ev
#     elif ev.type == X.MotionNotify and start:
#         xdiff = ev.root_x - start.root_x
#         ydiff = ev.root_y - start.root_y
#         start.child.configure(
#             x = attr.x + (start.detail == 1 and xdiff or 0),
#             y = attr.y + (start.detail == 1 and ydiff or 0),
#             width = max(1, attr.width + (start.detail == 3 and xdiff or 0)),
#             height = max(1, attr.height + (start.detail == 3 and ydiff or 0)))
#     elif ev.type == X.ButtonRelease:
#         start = None

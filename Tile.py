from Xlib import X, XK

from Geometry import Geometry

class Tile:
  def __init__(self, pos, size, screen):
    self.slots = [None, None, None, None]
    self.screen = screen
    self.slot_geometrys = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    self.pos = pos
    self.size = size
    self.center_size = 10
    self.center = [pos[0] + size[0] // 2, pos[1] + size[1] // 2]
    self.hotspot_size = 100
    self.calculation_slot_sizes()
    self.main = False
    self.visible = True
    self.draw_bounds()

  def draw_bounds(self):
    colormap = self.screen.default_colormap
    blue = colormap.alloc_named_color("blue").pixel
    gc = self.screen.root.create_gc(
        foreground=blue,
        background=blue,
    )
    self.screen.root.rectangle(gc,
        self.pos[0], self.pos[1], self.pos[0] + self.size[0], self.pos[1] + self.size[1])

  def pop_out(self, window):
    for i, slot in enumerate(self.slots):
      if slot == window:
        self.slots[i] = None
      if slot and isinstance(slot, Tile):
        slot.pop_out(window)


  def add_to_slots(self, tile, slots):
    for x in range(len(self.slots)):
      if self.slots[x]:
        self.slots[x].configure(stack_mode = X.Above)
      if (self.slots[x] == tile):
        self.slots[x] = None
    for x in slots:
      self.slots[x] = tile
    self.update_tile_dimensions()
  
  def update_tile_dimensions(self):
    for i in range(len(self.slots)):
      slot = self.slots[i]
      if slot:
        org_index = self.slots.index(slot)
        if org_index != i:
          if i - org_index == 1:
            slot.configure(width=slot.get_geometry().width + self.slot_geometrys[i][2] + self.center_size)
          elif i - org_index == 2:
            slot.configure(height=slot.get_geometry().height + self.slot_geometrys[i][3] + self.center_size)
        else:
          slot.configure(
            x=self.slot_geometrys[i][0],
            y=self.slot_geometrys[i][1],
            width=self.slot_geometrys[i][2],
            height=self.slot_geometrys[i][3]
          )
    self.draw_bounds()
  
  def calculation_slot_sizes(self):
    self.slot_geometrys[0][0] = self.pos[0]
    self.slot_geometrys[0][1] = self.pos[1]
    self.slot_geometrys[0][2] = (self.center[0] - self.center_size) - self.slot_geometrys[0][0]
    self.slot_geometrys[0][3] = (self.center[1] - self.center_size) - self.slot_geometrys[0][1]

    self.slot_geometrys[1][0] = self.center[0] + self.center_size
    self.slot_geometrys[1][1] = self.pos[1]
    self.slot_geometrys[1][2] = (self.pos[0] + self.size[0]) - self.slot_geometrys[1][0]
    self.slot_geometrys[1][3] = (self.center[1] - self.center_size) - self.slot_geometrys[1][1]

    self.slot_geometrys[2][0] = self.pos[0]
    self.slot_geometrys[2][1] = self.center[1] + self.center_size
    self.slot_geometrys[2][2] = (self.center[0] - self.center_size) - self.slot_geometrys[2][0]
    self.slot_geometrys[2][3] = (self.pos[1] + self.size[1]) - self.slot_geometrys[2][1]

    self.slot_geometrys[3][0] = self.center[0] + self.center_size
    self.slot_geometrys[3][1] = self.center[1] + self.center_size
    self.slot_geometrys[3][2] = (self.pos[0] + self.size[0]) - self.slot_geometrys[3][0]
    self.slot_geometrys[3][3] = (self.pos[1] + self.size[1]) - self.slot_geometrys[3][1]


  def on_drag(self, new_pos):
    self.center = new_pos
    self.calculation_slot_sizes()
    self.update_tile_dimensions()
  
  def configure(self, x=None, y=None, width=None, height=None, stack_mode=None):
    center_x_percent = (self.center[0] - self.pos[0]) / self.size[0]
    center_y_percent = (self.center[1] - self.pos[1]) / self.size[1]

    if x is not None:
      self.pos[0] = x
    if y is not None:
      self.pos[1] = y
    if width is not None:
      self.size[0] = width
    if height is not None:
      self.size[1] = height
    if stack_mode is not None:
      for slot in self.slots:
        if slot:
          slot.configure(stack_mode = stack_mode)

    self.center[0] = round(center_x_percent * self.size[0] + self.pos[0])
    self.center[1] = round(center_y_percent * self.size[1] + self.pos[1])

    self.calculation_slot_sizes()
    self.update_tile_dimensions()
  
  def get_geometry(self):
    return Geometry(self.pos[0], self.pos[1], self.size[0], self.size[1])
  
  def in_slot_hotspot(self, x, y):
    min_distance = 10e10
    slots = ()
    px, py = self.pos
    w, h = self.size
    points = [
      (px, py), (px + w / 2, py), (px + w, py),
      (px, py + h / 2), (px + w, py + h / 2),
      (px, py + h), (px + w / 2, py + h), (px + w, py + h),
    ]
    points_to_slots = [
      (0,), (0, 1), (1,),
      (0, 2), (1, 3),
      (2,), (2, 3), (3,)
    ]
    for i, point in enumerate(points):
      distance = (point[0] - x) ** 2 + (point[1] - y) ** 2
      if distance < min_distance:
        min_distance = distance
        slots = points_to_slots[i]
    
    return slots

  def get_square(self, x, y, side):
    square = [None, None, None, None]

    square[0] = x
    square[1] = y
    square[2] = x + side
    square[3] = y + side

    return square
  
  def get_slot_in_xy(self, x, y):
    slot = None
    for i in range(len(self.slot_geometrys)):
      geometry = self.slot_geometrys[i]
      if x > geometry[0] and y > geometry[1] and x < geometry[2] + geometry[0] and y < geometry[3] + geometry[1]:
        slot = i
    
    return slot
  
  def get_deep_slot_in_xy(self, x, y):
    slot_index = self.get_slot_in_xy(x, y)
    if slot_index is None: return None
    slot = self.slots[slot_index]
    if isinstance(slot, Tile):
      return slot.get_deep_slot_in_xy(x, y)
    else:
      return (self, slot_index)
  
  def is_in_center(self, x, y):
    return x > self.center[0] - self.center_size \
      and y > self.center[1] - self.center_size \
      and x < self.center[0] + self.center_size \
      and y < self.center[1] + self.center_size

  def is_in_center_deep(self, x, y):
    slot_index = self.get_slot_in_xy(x, y)
    if slot_index is None:
      return (self, self.is_in_center(x, y))
    slot = self.slots[slot_index]
    if isinstance(slot, Tile):
      return slot.is_in_center_deep(x, y)
    else:
      return (self, self.is_in_center(x, y))

  def get_deepest_hotspot(self, x, y):
    slot_index = self.get_slot_in_xy(x, y)
    if slot_index is None: return None
    slot = self.slots[slot_index]
    if isinstance(slot, Tile):
      return slot.get_deepest_hotspot(x, y)
    else:
      return (self, self.in_slot_hotspot(x, y))

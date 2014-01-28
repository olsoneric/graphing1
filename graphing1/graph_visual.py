
# Temporary max until one is figured out
MAX_RECTS = 200


class GraphVisual(object):

    @staticmethod
    def get_pos_from_rect(rect):
        """Depending on the rect type used for the derived implementation,
        return the position.  Needed to return different 2d and 3d positions.
         """
        raise Exception("Unimplemented")

    @staticmethod
    def set_pos_on_obj(obj, rect, state):
        """Depending on the rect type used for the derived implementation,
        set the position.  Needed to set different 2d and 3d positions.
         """
        raise Exception("Unimplemented")

    def __init__(self, graph_layout, rect_size=None):
        self.graph_layout = graph_layout
        self.rects = {}
        self.id_to_label = {}
        self.rect_labels = {}

        if not rect_size:
            self.rect_size = (80, 80)
        else:
            self.rect_size = tuple(rect_size)

    def setup_node_visual(self, pos, size, imagefile):
        """Override in derived implementations.
        Create a texture or a similar object to render.
        """

        raise Exception("Unimplemented")

    def setup_label_visual(self, name, pos):
        """Override in derived implementations.
        Create a texture containing text or a similar object to render.
        """

        raise Exception("Unimplemented")
            #label = Text(name, pos=rect.pos)
            #precipice.add(label)

    def create_rects(self, rect_size):
        for node_id, position in self.graph_layout.positions.items():
            #image1 = RandomImage("image1", 12, 12)
            #rect = RectTextured(image1, (50, 50), (30, 30))

            self.create_rect(node_id, position, rect_size)
            """
            # If already have a rect, skip this one
            if node_id in self.rects:
                continue

            rect = RectTextured(
                "data/images/face.png", pos=position, size=(80, 80))
            precipice.add(rect)
            self.rects[node_id] = rect

            # Add label
            if self.id_to_label:
                self.assign_label(rect, node_id)
                """

    def create_rect(self, node_id, position, rect_size):

        # If already have a rect, skip this one
        if node_id in self.rects:
            return self.rects[node_id]

        #rect = RectTextured(
        #    "data/images/face.png", pos=position, size=(80, 80))
        #precipice.add(rect)
        rect = self.setup_node_visual(
            position, size=rect_size, imagefile="images/face.png")
        self.rects[node_id] = rect

        # Add label
        if self.id_to_label:
            self.assign_label(rect, node_id)

    def assign_label(self, rect, id_name):
        name = self.id_to_label.get(id_name, None)

        if name:
            #label = Text(name, pos=rect.pos)
            #precipice.add(label)
            #label = self.setup_label_visual(name, pos=rect.pos)
            #label = self.setup_label_visual(name, pos=rect.getPosRealPx())
            label = self.setup_label_visual(
                name, pos=self.get_pos_from_rect(rect))
            self.rect_labels[rect] = label

    def update_labels(self, label_dict):
        #print "UPDATE LABELS 1"
        self.id_to_label.update(label_dict)

        # Add labels if some don't exist
        for node_id, rect in self.rects.items():
            if rect in self.rect_labels:
                pass  # label.update # FIXME: update text without large memleak
            else:
                #print "ADDING LABELS5"
                self.assign_label(rect, node_id)

    def update(self, seconds, state):
        #print "GRAPH_VISUAL UPDATE, changed:", self.graph_layout.changed

        for node_id in self.graph_layout.changed:
            position = self.graph_layout.positions[node_id]
            rect = self.rects.get(node_id)
            if not rect:
                rect = self.create_rect(node_id, position, self.rect_size)
            else:
                #rect.set_pos(position)
                #rect.setPosRealPx(*position)
                self.set_pos_on_obj(rect, position, state)

            label = self.rect_labels.get(rect)
            if label:
                #label.set_pos(position)
                #label.setPosRealPx(*position)
                self.set_pos_on_obj(label, position, state)

    def collidepoint(self, pos):
        print "FIXME: make collide_point more optimal with bin"
        for node_id, rect in self.rects.items():
            if rect.collidepoint(pos):
                return node_id
        return None


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

    def __init__(self, graph_layout, rect_size=None, imagefile=None):
        self.graph_layout = graph_layout
        self.rects = {}
        self.id_to_label = {}
        self.rect_labels = {}

        if imagefile:
            self.imagefile = imagefile
        else:
            self.imagefile = "images/face.png"

        if not rect_size:
            self.rect_size = (80, 80)
        else:
            self.rect_size = tuple(rect_size)

        self.lines_to_create = []

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
            position, size=rect_size, imagefile=self.imagefile)
        self.rects[node_id] = rect

        # Add label
        if self.id_to_label:
            self.assign_label(rect, node_id)

        return rect

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

    def create_lines_to_children(self):
        """
        Create lines for the tuples in self.lines_to_create.


        self.lines_to_create contains tuples of nodes.
        This will call setup_line_visual(node_obj1, node_obj2)
        """

        remaining_lines_to_create = []
        for (node_rect, child_id) in self.lines_to_create:
            child_rect = self.rects.get(child_id)
            if child_rect:
                self.setup_line_visual(node_rect, child_rect)
            else:
                # Child visual doesn't exit yet, create one, and
                # parent will try again next iteration.
                self._create_node(child_id)
                # Keep track of this tuple to try again.
                remaining_lines_to_create.append((node_rect, child_rect))

        self.lines_to_create = remaining_lines_to_create

    def _create_node(self, node_id, position=None):

        # If position is not provided yet, raise exception, layout should
        # have created positions for all nodes by now.
        if not position:
            #position = self.graph_layout.positions.get(node_id, (0, 0))
            raise Exception("No pos.  Create initial layout before visuals.")

        rect = self.create_rect(node_id, position, self.rect_size)

        # Will add lines - children may not exist, so store for later.
        print "STORING:", rect
        for child_id in self.graph_layout.connections[node_id]:
            self.lines_to_create.append((rect, child_id))

        return rect

    def update(self, seconds, state):
        """
        Update the positions of the nodes.

        If visuals for the nodes do not exist yet, create them.
        """

        # TODO: remove state arg if possible

        #print "GRAPH_VISUAL UPDATE, changed:", self.graph_layout.changed

        for node_id in self.graph_layout.changed:
            position = self.graph_layout.positions[node_id]
            rect = self.rects.get(node_id)
            if not rect:
                rect = self._create_node(node_id, position)
            else:
                #rect.set_pos(position)
                #rect.setPosRealPx(*position)
                self.set_pos_on_obj(rect, position, state)

            label = self.rect_labels.get(rect)
            if label:
                #label.set_pos(position)
                #label.setPosRealPx(*position)
                self.set_pos_on_obj(label, position, state)

        if self.lines_to_create:
            self.create_lines_to_children()

    def collidepoint(self, pos):
        print "FIXME: make collide_point more optimal with bin"
        for node_id, rect in self.rects.items():
            if rect.collidepoint(pos):
                return node_id
        return None

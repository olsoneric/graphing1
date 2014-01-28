
from pedemath.vec3 import Vec3

from matter.rect3d import Rect3d

from graphing1.graph_visual import GraphVisual


class GraphMatter3d(GraphVisual):
    """Not really a visual, but a base state representation.

    "GraphVisual" was based on 2D, this class attempts to create
    only the base state (pos, size) in 3d.
    The rendering visuals will be applied by the WorldView.
    """

    # TODO: rethink overall api to make easy to use

    @staticmethod
    def get_pos_from_rect(rect):
        """Depending on the rect type used for the derived implementation
        return the position.  Needed to return different 2d and 3d positions.
         """
        # Should be from matter/rect3d.py for now (maybe move to math lib)
        return rect.pos

    @staticmethod
    def set_pos_on_obj(obj, pos, state):
        """Depending on the rect type used for the derived implementation,
        set the position.  Needed to set different 2d and 3d positions.
         """
        if len(pos) == 2:
            # Convert to 3d
            print "SETTING NEW POS:", obj.pos, "->", pos
            obj.pos.set(pos[0], pos[1], -2)
        else:
            obj.pos.set(*pos)

    def __init__(self, graph_layout, world, rect_size=None):
        """Basic initialization, store layout and world."""

        super(GraphMatter3d, self).__init__(graph_layout)

        # Something to add objects to
        self.world = world

        # Make a 3d rect_size be default
        if not rect_size:
            self.rect_size = (1.0, 1.0, 1.0)
        else:
            self.rect_size = tuple(rect_size)

    def setup_node(self, pos, size, imagefile):
        print "ADDING OBJ"

        if len(pos) == 2:
            pos = (pos[0], pos[1], 0.0)

        rect = Rect3d(pos, size)
            #imagefile, pos, size, alpha=True)
        print "SETUP WORLD at:", rect.pos
        self.world.add(rect)
        return rect

    setup_node_visual = setup_node

    def setup_label(self, name, pos):
        """Override in derived implementations.
        Create a texture containing text or a similar object to render.
        """

        class Nop:
            def __init__(self):
                self.pos = Vec3(0, 0, 0)

        # TODO: make 3d text
        #label = ShowText(name, pos=pos)
        label = Nop()
        #self.world.add(label)
        return label

    setup_label_visual = setup_label

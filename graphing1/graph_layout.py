
import math
import random

from pedemath.vec2 import Vec2
from pedemath.vec3 import Vec3

from pedemath.rect import Rect
from pedemath.rect3 import Rect3


def random_point(rect_range):
    return Vec2(
        random.randrange(rect_range.x, rect_range.x + rect_range.width),
        random.randrange(rect_range.y, rect_range.y + rect_range.height))


def random_point_3d(rect_range):
    return Vec3(
        random.randrange(rect_range.x, rect_range.x + rect_range.width),
        random.randrange(rect_range.y, rect_range.y + rect_range.height),
        random.randrange(rect_range.z, rect_range.z + rect_range.depth))


class GraphLayout(object):

    def __init__(self, connections=None, region=None, three_d=False):

        if connections is None:
            self.connections = {}
        else:
            self.connections = dict(connections)

        self.positions = {}
        self.changed = set()
        self.pending_changed_structure = set()
        self.changed_structure = set()
        self.frame = 1
        # Physics-like nodes
        self.vels = {}
        self.three_d = three_d

        if region:
            self.region = region
        else:
            self.region = Rect(0, 0, 600, 500)

        self.initial_max_dist = 10
        self.closer_max_dist = 2.0
        self.num_frames_for_init = 20

    def layout(self):
        """Call once to initialize the layout."""

        for node, children in self.connections.items():
            self._add_node_connections_layout(node, children)

    def add_connections(self, new_connections):
        """
        Expects an adjancency dict.

        New connections are added to existing connection lists.
        """
        # print "ADD_CONNS:", new_connections

        for node, children in new_connections.items():
            self.add_node_children(node, children)

        """
        for node, children in new_connections.items():
            # print "NODE:", node, "CHILDREN:", children, "CURRENT:", self.connections[node]
            for child in children:
                # print "BEFORE:", self.connections[node]
                if child not in self.connections[node]:
                    self.connections[node].append(child)
                # print "AFTER:", self.connections[node]

        for node, children in new_connections.items():
            # Create position and vel for nodes
            self._add_node_connections_layout(node, children)

            # print "Adding:", node, children
            # Mark as changed to ensure visual links are added/removed.
            # Include the full current list of nodes
            all_children = self.connections[node]
            # print "  Adding expect:", node, all_children
            self.pending_changed_structure.add((node, tuple(all_children)))
            """

    def add_node_children(self, node, children):
        """A single node alternative to add_connections."""

        for child in children:
            if child not in self.connections[node]:
                self.connections[node].append(child)

        # Create position and vel for nodes
        self._add_node_connections_layout(node, children)

        # Mark as changed to ensure visual links are added/removed.
        # Include the full current list of nodes
        all_children = self.connections[node]
        # print "  Adding expect:", node, all_children
        self.pending_changed_structure.add((node, tuple(all_children)))

    def set_connections(self, new_connections):
        """
        Expects an adjancency dict.

        New connections replace existing connection lists.
        """
        for node, children in new_connections.items():
            self.connections[node] = list(children)

        for node, children in new_connections.items():
            self._set_node_connections(node, children)

            # Mark as changed to ensure links are drawn
            self.pending_changed_structure.add((node, tuple(children)))

    def _add_node_connections_layout(self, node, children):
        """Spatially layout the nodes.

        If node doesn't exist, create a random position for it.
        """
        if node not in self.positions:
            if self.three_d:
                self.positions[node] = random_point_3d(self.region)
                self.vels[node] = Vec3(0, 0, 0)
            else:
                self.positions[node] = random_point(self.region)
                self.vels[node] = Vec2(0, 0)
        for child in children:
            if child not in self.positions:
                if self.three_d:
                    self.positions[child] = random_point_3d(self.region)
                    #self.positions[child] = self.region.center_v3()
                    self.vels[child] = Vec3(0, 0, 0)
                else:
                    self.positions[child] = random_point(self.region)
                    #self.positions[child] = self.region.center_v3()
                    self.vels[child] = Vec2(0, 0)

    def get_pos(self, node):
        return self.positions[node]

    def update(self, seconds):
        # Changed nodes have been updated/drawn, so clear them now.
        self.changed.clear()

        # Clear old stucture changes
        self.changed_structure.clear()
        # Start any pending structure changes so visuals can process them.
        self.changed_structure.update(self.pending_changed_structure)
        # Clear pending changes
        self.pending_changed_structure.clear()
        """
        for node in self.positions:
            self.positions[node] = (random.randrange(500),
                                    random.randrange(500))
            self.changed.add(node)
        """
        if self.three_d:
            self.recalc3d()
        else:
            self.recalc()
        # FIXME: detect actual change in positions instead of assuming
        # everything changed.
        for node in self.positions:
            self.changed.add(node)

    def recalc(self):
        # Starting working from: http://stevehanov.ca/blog/index.php?id=65
        #   TODO: Add optimizations
        # canvas
        #width = 600
        #height = 600

        # K is related to how long the edges should be.
        #k = 400.0
        # Approximate earlier calculation of k
        k = min(self.region.width, self.region.height) / 3 * 2

        # C limits the speed of the movement. Things become slower over time.
        C = math.log(self.frame + 1) * 100
        self.frame += 1

        # calculate repulsive forces
        for v_node_id in self.positions.keys():

            v_pos = self.positions[v_node_id]
            # Initialize velocity to none.
            self.vels[v_node_id] = Vec2(0, 0)

            # for each other node, calculate the repulsive force and adjust the
            # velocity in the direction of repulsion.
            for u_node_id in self.positions.keys():

                if (v_node_id == u_node_id):
                    continue

                # D is short hand for the difference vector between the
                # positions of the two vertices
                u_pos = self.positions[u_node_id]
                #print "COMPARING:", v_node_id, u_node_id, v_pos, u_pos
                d_x = v_pos.x - u_pos.x
                d_y = v_pos.y - u_pos.y
                #print "dx, dy:", d_x, d_y
                dist = math.pow(d_x * d_x + d_y * d_y, 0.5)  # distance
                #print "DIST:", dist
                if (0 == dist):
                    continue
                mul = k * k / (dist * dist * C)

                self.vels[v_node_id] += Vec2(d_x * mul, d_y * mul)
                #v_vel.x += d_x * mul
                #v_vel.y += d_y * mul

        # calculate attractive forces
        for v_node_id, targets in self.connections.items():
            for u_node_id in targets:

                v_pos = self.positions[v_node_id]
                u_pos = self.positions[u_node_id]
                # each edge is an ordered pair of vertices .v and .u
                dx = v_pos.x - u_pos.x
                dy = v_pos.y - u_pos.y
                dist = math.pow(dx * dx + dy * dy, 0.5)  # distance.
                if (0 == dist):
                    continue

                mul = dist * dist / k / C
                dxmul = dx * mul
                dymul = dy * mul
                # attract both nodes towards eachother.
                self.vels[v_node_id].x -= dxmul
                self.vels[v_node_id].y -= dymul
                self.vels[u_node_id].x += dxmul
                self.vels[u_node_id].y += dymul

        # Here we go through each node and actually move it in the given
        #  direction.
        #for ( var vindex = 1; vindex < this.graph.nodes.length; vindex++ )
        for v_node_id in self.positions.keys():

            v_pos = self.positions[v_node_id]
            v_vel = self.vels[v_node_id]
            dist = v_vel.x * v_vel.x + v_vel.y * v_vel.y
            max_dist = self.initial_max_dist

            # After the first 20 frames, require nodes to be closer
            # to each other to affect each other.
            if self.frame > self.num_frames_for_init:
                max_dist = self.closer_max_dist

            # Only affect a node if it is closer than max_dist.
            if (dist > max_dist * max_dist):
                dist = math.pow(dist, 0.5)
                v_vel.x *= max_dist / dist
                v_vel.y *= max_dist / dist

            #v.x += v.vx
            #v.y += v.vy
            self.positions[v_node_id] = self.positions[v_node_id] + v_vel
            #print v_node_id, "NEWPOS:", self.positions[v_node_id]

    def recalc3d(self):
        # Starting working from: http://stevehanov.ca/blog/index.php?id=65
        # canvas
        #width = 600
        #height = 600

        # K is related to how long the edges should be.
        #k = 400.0
        # Approximate earlier calculation of k
        k = min(self.region.width, self.region.height) / 3 * 2

        # C limits the speed of the movement. Things become slower over time.
        C = math.log(self.frame + 1) * 100
        self.frame += 1

        # calculate repulsive forces
        for v_node_id in self.positions.keys():

            v_pos = self.positions[v_node_id]
            # Initialize velocity to none.
            self.vels[v_node_id] = Vec3(0, 0, 0)

            # for each other node, calculate the repulsive force and adjust the
            # velocity in the direction of repulsion.
            for u_node_id in self.positions.keys():

                if (v_node_id == u_node_id):
                    continue

                # D is short hand for the difference vector between the
                # positions of the two vertices
                u_pos = self.positions[u_node_id]
                #print "COMPARING:", v_node_id, u_node_id, v_pos, u_pos
                d_x = v_pos.x - u_pos.x
                d_y = v_pos.y - u_pos.y
                d_z = v_pos.z - u_pos.z
                #print "dx, dy:", d_x, d_y
                #dist = math.pow(d_x * d_x + d_y * d_y, 0.5)  # distance
                dist = math.pow(d_x * d_x + d_y * d_y + d_z * d_z, 0.5)
                #print "DIST:", dist
                if (0 == dist):
                    continue
                mul = k * k / (dist * dist * C)

                #self.vels[v_node_id] += Vec2(d_x * mul, d_y * mul)
                self.vels[v_node_id] += Vec3(d_x * mul, d_y * mul, d_z * mul)
                #v_vel.x += d_x * mul
                #v_vel.y += d_y * mul

        # calculate attractive forces
        for v_node_id, targets in self.connections.items():
            for u_node_id in targets:

                v_pos = self.positions[v_node_id]
                u_pos = self.positions[u_node_id]
                # each edge is an ordered pair of vertices .v and .u
                dx = v_pos.x - u_pos.x
                dy = v_pos.y - u_pos.y
                dz = v_pos.z - u_pos.z
                #dist = math.pow(dx * dx + dy * dy, 0.5)  # distance.
                dist = math.pow(dx * dx + dy * dy + dz * dz, 0.5)  # distance.
                if (0 == dist):
                    continue

                mul = dist * dist / k / C
                dxmul = dx * mul
                dymul = dy * mul
                dzmul = dz * mul
                # attract both nodes towards eachother.
                self.vels[v_node_id].x -= dxmul
                self.vels[v_node_id].y -= dymul
                self.vels[v_node_id].z -= dzmul
                self.vels[u_node_id].x += dxmul
                self.vels[u_node_id].y += dymul
                self.vels[u_node_id].z += dzmul

        # Here we go through each node and actually move it in the given
        #  direction.
        #for ( var vindex = 1; vindex < this.graph.nodes.length; vindex++ )
        for v_node_id in self.positions.keys():

            v_pos = self.positions[v_node_id]
            v_vel = self.vels[v_node_id]
            #dist = v_vel.x * v_vel.x + v_vel.y * v_vel.y
            dist = v_vel.x * v_vel.x + v_vel.y * v_vel.y + v_vel.z * v_vel.z
            max_dist = self.initial_max_dist

            # After the first 20 frames, require nodes to be closer
            # to each other to affect each other.
            if self.frame > self.num_frames_for_init:
                max_dist = self.closer_max_dist

            if (dist > max_dist * max_dist):
                dist = math.pow(dist, 0.5)
                v_vel.x *= max_dist / dist
                v_vel.y *= max_dist / dist
                v_vel.z *= max_dist / dist

            #v.x += v.vx
            #v.y += v.vy
            self.positions[v_node_id] = self.positions[v_node_id] + v_vel
            #print v_node_id, "NEWPOS:", self.positions[v_node_id]

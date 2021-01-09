import sys

import pygame
import pygame.display as pydisplay
import pygame.mouse as pymouse
import pygame.draw as pydraw
from pygame.locals import *
from main import *

pygame.init()

"""Globals"""

button_unselected = (255, 255, 255)
not_selected_color = (0, 0, 255)
selected_color = (255, 0, 0)

selected_algorithm = ""  # used for determining which algorithm to use
start = 0  # default starting node
# add_node_mode = 0 --> adding edges
# add_node_mode = 1 --> adding nodes
# add_node_mode = 2 --> deleting nodes <-- this has been removed
# add_node_mode = 3 --> deleting edges
# add_node_mode = 4 --> select starting node
add_node_mode = 1  # differentiate between adding nodes or edges

screen = pydisplay.set_mode((1400, 800))  # display surface for graph creation
graph_screen = pygame.Rect((120, 0, 1400, 800))
font = pygame.font.Font(None, 28)  # font to use

# used to add edges
primary = -1
secondary = -1
node_name = 0  # used to name nodes


class Node:
    """
    Class to represent nodes

    Attributes
    ----------
    name : int
        name of the node
    colour : tuple
        colour of node in the form of (r, g, b)
    position : tuple
        position of node in the form of (x, y)
    state : int
        decides whether or not node has been selected

    Methods
    -------
    is_selected()
        changes the state and colour of node to being selected

    not_selected()
        changes the state and colour of node to being not selected

    draw()
        draws the node on pygame screen
    """

    def __init__(self, name, colour, position, state):
        """
        Parameters
        ----------
        name : int
            Name of the node
        colour : tuple
            Triplet of integers in the form of (r, g, b)
        position : tuple
            Position of node in the form of (x, y)
        state : int
            Decides whether or not node has been selected
            True means it is selected, False means unselected
        """
        self.name = name
        self.colour = colour
        self.position = position
        self.state = state

    def is_selected(self):
        """
        Changes the state and colour of node to being selected
        """
        self.state = 1
        self.colour = selected_color

    def not_selected(self):
        """
        Changes the state and colour of node to being not selected
        """
        self.state = 0
        self.colour = not_selected_color

    def draw(self):
        """
        Draws the node on pygame screen
        """
        if self.state != -1:
            pydraw.circle(screen, self.colour, self.position, 10)


class Edge:
    """
    Class to represent edges. Each edge is between u and v.

    Attributes
    ----------
    u : Node
        Node object. Vertex in edge u--v.
    v: Node
        Node object. Vertex in edge u--v.
    colour : tuple
        Triplet of integers in the form of (r, g, b)
    weight : float
        Euclidean distance between the coordinates of nodes u and v

    Methods
    -------
    get_edge()
        Returns the edge object

    get_edge_data()
        Returns the edge as a tuple with ints and floats

    is_selected()
        Changes colour to be selected

    not_selected()
        Changes colour to not be selected

    draw()
        Draws the edge on the pygame screen
    """

    def __init__(self, u, v, colour):
        """
        Parameters
        ----------
        u : Node
            one of the nodes that the edge will be between
        v : Node
            one of the nodes that the edge will be between
        colour : tuple
            colour of edge in the form of (r, g, b)
        """
        self.u = u
        self.v = v
        self.colour = colour
        x1, y1 = self.u.position
        x2, y2 = self.v.position
        self.weight = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        self.edge = (self.u, self.v, self.weight)

    def get_edge(self):
        """
        Returns the edge object
        """
        return self.edge

    def get_edge_data(self):
        """
        Returns the edge as a tuple with ints and floats
        """
        return self.u.name, self.v.name, self.weight

    def is_selected(self):
        """
        changes colour to be selected
        """
        self.colour = selected_color

    def not_selected(self):
        """
        changes colour to not be selected
        """
        self.colour = not_selected_color

    def draw(self):
        """
        draws the edge on the pygame screen
        """
        pydraw.line(screen, self.colour, self.u.position, self.v.position, 2)


class Graph:
    """
    Class to represent a graph

    Attributes
    ----------
    graph : dict
        Adjacency list in the form of a python dictionary with keys as nodes and values as lists
        containing neighbors in the form (distance, node)

    edge_list : list
        List of all edges in the graph as triplets (u, v, weight)

    Methods
    -------
    add_node(node)
        Adds a node to the graph by creating a key for it in the adjacency list

    add_bi_edge(edge)
        Adds an edge by updating the adjacency list and also appending it to edge_list

    del_edge(edge)
        Deletes the edge from edge_list and updates the adjacency list

    get_graph()
        Returns the adjacency list with node objects

    get_edges()
        Returns edge_list but with ints and floats instead of edge objects

    get_positions()
        Returns a dictionary with node names as keys and positions as values

    draw()
        draws the graph by calling draw functions for all nodes and edges in the graph
    """

    def __init__(self):
        self.graph = {}
        self.edge_list = []

    def add_node(self, node):
        """
        Adds a node to the graph by creating a key for it in the dictionary

        Parameters
        ----------
        node : Node
            The node object that needs to be added to the graph
        """
        self.graph[node] = []

    def add_bi_edge(self, edge):
        """
        Adds an edge by updating the adjacency list and also appending it to edge_list

        Parameters
        ----------
        edge : Edge
            Edge object
        """
        self.graph[edge.u].append((edge.v, edge.weight))
        self.graph[edge.v].append((edge.u, edge.weight))

        self.edge_list.append(edge)
        self.edge_list = list(set(self.edge_list))  # insure no duplicates

    def del_edge(self, edge):
        """
        Deletes the edge from edge_list and updates the adjacency list

        Parameters
        ----------
        edge : Edge
            Edge object that is being removed
        """
        self.edge_list.remove(edge)
        self.graph[edge.u].remove((edge.v, edge.weight))
        self.graph[edge.v].remove((edge.u, edge.weight))

    def get_graph(self):
        """
        Returns the adjacency list with all node objects
        """
        return self.graph

    def get_nodes(self):
        """
        Return the graph in adjacency list form with ints and floats excluding nodes with state equal to -1

        Returns
        -------
        nodes : dict
            Adjacency list in the form of a python dictionary with nodes as keys and lists of edges as values
        """
        nodes = {}
        for node in self.graph:
            if node.state != -1:
                nodes[node.name] = set()
                for adjacent in self.graph[node]:
                    if adjacent[0].state != -1:
                        nodes[node.name].add((adjacent[0].name, adjacent[1]))
        return nodes

    def get_edges(self):
        """
        Returns edge_list with ints and floats instead of edge objects
        """
        # (v, u, weight) and (u, v, weight) will not be treated as the same
        edges = []
        for edge in self.edge_list:
            edges.append((edge.u.name, edge.v.name, edge.weight))
        return list(set(edges))

    def get_positions(self):
        """
        Returns a dictionary with node names as keys and positions as values
        Ignores nodes with state of -1

        Returns
        -------
        pos : dict
            Keys are nodes, values are positions in the form (x, y)
        """
        pos = {}
        for node in self.graph:
            if node.name not in pos.keys() and node.state != -1:
                pos[node.name] = node.position
        return pos

    def not_within_min(self, mouse_pos):
        """
        Checks if the mouse click was within a certain distance from a node

        Parameters
        ----------
        mouse_pos : tuple
            Coordinates of mouse click

        Returns
        -------
        not_within : boolean
            True if mouse click was far enough away (> min_distance) from a node, false otherwise
        """
        not_within = True
        min_distance = 20
        x_mpos, y_mpos = mouse_pos[0], mouse_pos[1]
        for node in self.graph:
            if node.state != -1:
                x_node, y_node = node.position
                distance = ((x_node - x_mpos) ** 2 + (y_node - y_mpos) ** 2) ** .5
                if distance < min_distance:
                    not_within = False
                    if add_node_mode != 1:
                        node.is_selected()  # set node as being selected
        return not_within

    def draw(self):
        """
        Draws the graph by calling draw functions for all nodes and edges in the graph
        """
        for node in self.graph:
            node.draw()
        for edge in self.edge_list:
            edge.draw()


my_graph = Graph()  # create our graph


class Button(pygame.Rect):
    """
    Class to represent Buttons that inherits for Rect class in pygame

    Attributes
    ----------
    x : int
        x-coordinate of top left corner of button

    y : int
        y-coordinate of top left corner of button

    width : int
        Width of the button

    height : int
        Height of the button

    text : str
        String that is displayed on the button and is used to identify the button

    colour : tuple
        Colour of the button in the form of (r, g, b)

    shown : int
        Determines if the button is displayed or not

    Methods
    -------
    draw()
        Draws the button on the pygame screen

    is_clicked(mouse_pos)
        Determines if a button was clicked or not, handles what happens if a certain button is clicked
    """

    def __init__(self, x, y, width, height, text, colour, shown):
        """
        Parameters
        ----------
        x : int
            x co-ordinate of top left corner of button
        y : int
            y co-ordinate of top left corner of button
        width : int
            width of the button
        height : int
            height of the button
        text : str
            string that is displayed on the button and is used to identify the button
        colour : tuple
            colour of the button in the form of (r, g, b)
        shown : int
            determines if the button is displayed or not
        """
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.text = text
        self.colour = colour
        self.shown = shown

    def draw(self):
        """
        Draws the button on the screen if it is being shown
        """
        if self.shown:
            button_text = font.render(self.text, True, (0, 0, 0))
            width = button_text.get_width()
            height = button_text.get_height()
            pygame.draw.rect(screen, self.colour, self)
            screen.blit(button_text, (self.x - (width - self.width) / 2, self.y - (height - self.height) / 2))

    def is_clicked(self, mouse_pos):
        """
        Returns whether or not a button was clicked on, True if it was, False otherwise
        Also handles what happens if certain buttons are clicked

        Parameters
        ----------
        mouse_pos : tuple
            Position of mouse click in form of (x, y)
        """

        global add_node_mode, selected_algorithm
        algo_buttons = ["Bfs", "Dfs", "Dijkstra", "Kruskal"]
        if self.collidepoint(mouse_pos):  # different things happen if different buttons are clicked
            if self.text == "Add Edge":
                add_node_mode = 0
            elif self.text == "Add Node":
                add_node_mode = 1
            elif self.text == "Del Node":
                add_node_mode = 2
            elif self.text == "Del Edge":
                add_node_mode = 3

            elif self.text == "Selection":  # open selection menu
                bfs_mode.shown = 1
                dfs_mode.shown = 1
                dij_mode.shown = 1
                kru_mode.shown = 1

            elif self.text in algo_buttons:  # if one of the algorithms is selected
                selected_algorithm = self.text
                # change add_node_mode and shown prompt
                add_node_mode = 4
                select_start_prompt.shown = 1

            elif self.text == "Select Start node":  # enables selection of start node
                add_node_mode = 4

            elif self.text == "Run":  # Run button is responsible for animating the algorithms
                positions = my_graph.get_positions()
                nodes = [node for node in my_graph.get_nodes().keys()]
                edges = my_graph.get_edges()
                create_networkx_graph(positions, nodes, edges)
                fig, ax = plt.subplots(figsize=(14, 7))
                if selected_algorithm == "":
                    print("UH OH")
                elif selected_algorithm == "Bfs":
                    ani_mst = mpa.FuncAnimation(fig, update_bfs, fargs=(start,), interval=1000)
                elif selected_algorithm == "Dfs":
                    ani_mst = mpa.FuncAnimation(fig, update_dfs, fargs=(start,), interval=1000)
                elif selected_algorithm == "Dijkstra":
                    ani_mst = mpa.FuncAnimation(fig, update_dijk, fargs=(start,), interval=1000)
                elif selected_algorithm == "Kruskal":
                    ani_mst = mpa.FuncAnimation(fig, update_mst, interval=1000)
                ax.invert_yaxis()
                fig.tight_layout()
                plt.show()

            self.colour = selected_color
            return True
        self.colour = button_unselected
        return False


"""Create buttons"""
add_node = Button(10, 10, 100, 50, "Add Node", button_unselected, 1)
add_edge = Button(10, 70, 100, 50, "Add Edge", button_unselected, 1)
del_edge = Button(10, 190, 100, 50, "Del Edge", button_unselected, 1)
select_algorithm = Button(10, 250, 100, 50, "Selection", button_unselected, 1)
bfs_mode = Button(10, 310, 100, 50, "Bfs", button_unselected, 0)
dfs_mode = Button(10, 370, 100, 50, "Dfs", button_unselected, 0)
dij_mode = Button(10, 430, 100, 50, "Dijkstra", button_unselected, 0)
kru_mode = Button(10, 490, 100, 50, "Kruskal", button_unselected, 0)
run_visual = Button(10, 740, 100, 50, "Run", button_unselected, 1)
select_start_prompt = Button(10, 680, 200, 50, "Select Start node", button_unselected, 0)
buttons = [add_node, add_edge, del_edge, select_algorithm, bfs_mode, dfs_mode, dij_mode, kru_mode, run_visual,
           select_start_prompt]  # list of all buttons


def main():
    """
    The main function. The driving function for Pygame,
    and the one which pieces functions and classes together to run the program.
    """
    global primary, secondary, node_name, start
    pydisplay.init()
    pydisplay.set_caption("Create your graph")
    while True:  # will always be running
        pygame.draw.rect(screen, (192, 192, 192), graph_screen)  # draw background for graph screen
        for event in pygame.event.get():
            if event.type in (QUIT, KEYDOWN):  # exit screen check
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:  # button click check
                for button in buttons:  # check if a button is clicked
                    button.is_clicked(event.pos)
                mouse_pos = pymouse.get_pos()

                # adding nodes -> must be far enough away, on screen, correct mode
                if my_graph.not_within_min(mouse_pos) and graph_screen.collidepoint(mouse_pos) and add_node_mode == 1:
                    new_node = Node(node_name, not_selected_color, mouse_pos, 0)
                    my_graph.add_node(new_node)
                    node_name += 1

                # adding edges -> a node must be selected and correct mode
                if not my_graph.not_within_min(mouse_pos) and not add_node_mode:
                    for node in my_graph.get_graph():
                        if primary == -1 and node.state == 1:  # if no primary node has been selected
                            primary = node
                        elif primary != -1 and node.state == 1 and primary != node:  # cannot make a edge with itself
                            secondary = node
                        if primary != -1 and secondary != -1:  # add the edge and reset primary and secondary
                            new_edge = Edge(primary, secondary, not_selected_color)
                            if new_edge.get_edge_data() not in my_graph.get_edges():  # no duplicate edges allowed
                                my_graph.add_bi_edge(new_edge)
                            primary.not_selected()
                            secondary.not_selected()
                            primary = -1
                            secondary = -1

                # deleting nodes -> correct mode, and node selected
                if add_node_mode == 2 and not my_graph.not_within_min(mouse_pos):
                    for node in my_graph.get_graph():  # find which node was selected
                        if node.state == 1:
                            my_graph.del_node(node)

                # deleting edges -> correct mode, edge selected NEEDS FIXING
                if add_node_mode == 3 and not my_graph.not_within_min(mouse_pos):
                    for node in my_graph.get_graph():
                        if primary == -1 and node.state == 1:  # if no primary node has been selected
                            primary = node
                        elif primary != -1 and node.state == 1 and primary != node:  # cannot make a edge with itself
                            secondary = node
                        if primary != -1 and secondary != -1:  # add the edge and reset primary and secondary
                            for edge in my_graph.edge_list:
                                if (edge.u is primary and edge.v is secondary) or (
                                        edge.v is primary and edge.u is secondary):
                                    my_graph.del_edge(edge)
                            primary.not_selected()
                            secondary.not_selected()
                            primary = -1
                            secondary = -1

                if add_node_mode == 4 and not my_graph.not_within_min(mouse_pos):
                    num_selected = 0  # make sure only one start node can be selected at a time
                    for node in my_graph.get_graph():
                        if node.state == 1:
                            start = node.name
                        node.not_selected()
                    for node in my_graph.get_graph():
                        if node.name == start:
                            node.colour = selected_color

        for button in buttons:  # draw all buttons
            button.draw()
        my_graph.draw()
        pydisplay.update()


main()

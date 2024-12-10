from __future__ import annotations  # Allows forward references for type hints (required for Python 3.7+)


# The 'Node' class represents a generic node in a tree structure (possibly a B-tree or B+ tree).
class Node:
    # A class variable to keep track of unique identifiers for nodes across all instances.
    uidCounter = 0

    # Constructor to initialize a Node object.
    # The order parameter specifies the maximum number of keys the node can hold.
    def __init__(self, order):
        # The order of the node, often used to limit the number of keys/values it can hold.
        self.order = order
        # Pointer to the parent node. Initially, it's set to None (this node doesn't have a parent yet).
        self.parent: Node = None
        # List of keys stored in this node.
        self.keys = []
        # List of values associated with the keys. This can be data or pointers to child nodes.
        self.values = []

        # Increment the unique identifier counter and assign the current node a unique ID.
        Node.uidCounter += 1
        self.uid = self.uidCounter

    # Splitting a node into two nodes. This method is used when a node overflows.
    # It creates two new nodes (left and right) and redistributes the keys and values between them.
    def split(self) -> Node:
        # Create two new child nodes (left and right) with the same order.
        left = Node(self.order)
        right = Node(self.order)
        # Find the middle index to split the node's keys and values.
        mid = int(self.order // 2)

        # Set the parent of the new nodes to be the current node.
        left.parent = right.parent = self

        # Split the keys and values at the middle index and assign them to the left and right nodes.
        left.keys = self.keys[:mid]
        left.values = self.values[:mid + 1]

        right.keys = self.keys[mid + 1:]
        right.values = self.values[mid + 1:]

        # Set the current node's keys and values to only contain the middle key.
        self.values = [left, right]
        self.keys = [self.keys[mid]]

        # Reassign the parent of the children of the left and right nodes.
        for child in left.values:
            if isinstance(child, Node):
                child.parent = left
        for child in right.values:
            if isinstance(child, Node):
                child.parent = right

        # Return the current node, which now represents the root of the two newly split nodes.
        return self 

    # Return the number of keys in the node.
    def getSize(self) -> int:
        return len(self.keys)

    # Check if the node is empty (contains no keys).
    def isEmpty(self) -> bool:
        return len(self.keys) == 0

    # Check if the node is full (has reached its maximum capacity, one less than its order).
    def isFull(self) -> bool:
        return len(self.keys) == self.order - 1

    # Check if the node is nearly underflowing (has fewer than half of the maximum keys).
    def isNearlyUnderflow(self) -> bool: 
        return len(self.keys) <= floor(self.order / 2)

    # Check if the node is underflowing (has fewer than half of the maximum keys minus one).
    def isUnderflow(self) -> bool: 
        return len(self.keys) <= floor(self.order / 2) - 1

    # Check if the node is the root (i.e., it has no parent).
    def isRoot(self) -> bool:
        return self.parent is None


# The 'LeafNode' class represents a leaf node in a B-tree or B+ tree.
# It extends from the 'Node' class, with additional properties and methods specific to leaf nodes.
class LeafNode(Node):
    # Constructor to initialize a LeafNode, inheriting from Node.
    def __init__(self, order):
        super().__init__(order)

        # Pointers to the previous and next leaf nodes in the sequence (used in B+ trees).
        self.prevLeaf: LeafNode = None
        self.nextLeaf: LeafNode = None

    # Method to add a key-value pair to the leaf node.
    def add(self, key, value):
        # If the node is empty, just add the key and value.
        if not self.keys:
            self.keys.append(key)
            self.values.append([value])
            return

        # Iterate through the keys to find the appropriate place for the new key-value pair.
        for i, item in enumerate(self.keys):
            # If the key already exists, append the value to the existing key's values.
            if key == item: 
                self.values[i].append(value)
                break

            # If the key is smaller than the current key, insert it before this key.
            elif key < item: 
                self.keys = self.keys[:i] + [key] + self.keys[i:]
                self.values = self.values[:i] + [[value]] + self.values[i:]
                break

            # If we have reached the end of the keys, append the new key and value.
            elif i + 1 == len(self.keys):
                self.keys.append(key)
                self.values.append([value])
                break

    # Method to split a leaf node when it becomes full.
    # It creates a new leaf node and distributes the keys and values between the original and new leaf.
    def split(self) -> Node: 
        # Create a new top node and a new leaf node.
        top = Node(self.order)
        right = LeafNode(self.order)
        # Find the middle index to split the keys and values.
        mid = int(self.order // 2)

        # Set the parent of both the new leaf and the top node to the same parent.
        self.parent = right.parent = top

        # Assign the keys and values of the right leaf to the second half of the current keys and values.
        right.keys = self.keys[mid:]
        right.values = self.values[mid:]
        # Link the right leaf to the previous and next leaf nodes in the sequence.
        right.prevLeaf = self
        right.nextLeaf = self.nextLeaf

        # Set the top node's key to be the first key in the right leaf.
        top.keys = [right.keys[0]]
        # Set the top node's values to point to both the current leaf and the new right leaf.
        top.values = [self, right]

        # Truncate the current leaf's keys and values to only contain the first half.
        self.keys = self.keys[:mid]
        self.values = self.values[:mid]
        # Update the nextLeaf pointer to point to the new right leaf.
        self.nextLeaf = right

        # Return the top node which is now the parent of the two leaf nodes.
        return top


class BPlusTree(object):
    # Constructor for initializing the BPlusTree.
    # Takes an optional order parameter which defines the maximum number of keys per node.
    def __init__(self, order=5):
        self.root: Node = LeafNode(order)  # Initialize the root as a LeafNode.
        self.order: int = order  # Set the order of the BPlus Tree.

    # Static method to find the appropriate node and index for a given key.
    # This is used for traversing through internal nodes to find the correct position for key insertion.
    @staticmethod
    def _find(node: Node, key):
        # Traverse through the node's keys and compare with the given key.
        for i, item in enumerate(node.keys):
            if key < item:
                # If key is smaller, return the appropriate child node and index.
                return node.values[i], i
            elif i + 1 == len(node.keys):
                # If key is larger than all existing keys, return the last child node and index.
                return node.values[i + 1], i + 1

    # Static method to merge a child node into its parent node after splitting.
    # This updates the parent's keys and values based on the first key of the child node.
    @staticmethod
    def _mergeUp(parent: Node, child: Node, index):
        # Remove the child node from the parent's values list.
        parent.values.pop(index)
        pivot = child.keys[0]  # Get the pivot key from the child node.

        # Update the parent node's references to child nodes.
        for c in child.values:
            if isinstance(c, Node):
                c.parent = parent

        # Find the correct position in the parent node to insert the pivot key.
        for i, item in enumerate(parent.keys):
            if pivot < item:
                # Insert the pivot key and merge child values accordingly.
                parent.keys = parent.keys[:i] + [pivot] + parent.keys[i:]
                parent.values = parent.values[:i] + child.values + parent.values[i:]
                break
            elif i + 1 == len(parent.keys):
                # If pivot key is larger than all, append it to the parent's keys and values.
                parent.keys += [pivot]
                parent.values += child.values
                break

    # Method to insert a key-value pair into the BPlusTree.
    # This method handles splitting and merging nodes if necessary.
    def insert(self, key, value):
        node = self.root

        # Traverse down the tree to find the leaf node where the key should be inserted.
        while not isinstance(node, LeafNode):
            node, index = self._find(node, key)

        # Add the key-value pair to the leaf node.
        node.add(key, value)

        # If the leaf node is full, split it and propagate the split upwards.
        while len(node.keys) == node.order:
            if not node.isRoot():
                parent = node.parent
                node = node.split()
                jnk, index = self._find(parent, node.keys[0])
                self._mergeUp(parent, node, index)
                node = parent
            else:
                node = node.split()
                self.root = node

    # Method to retrieve the value(s) associated with a key.
    def retrieve(self, key):
        node = self.root

        # Traverse down the tree to the leaf node containing the key.
        while not isinstance(node, LeafNode):
            node, index = self._find(node, key)

        # Return the corresponding value if the key is found.
        for i, item in enumerate(node.keys):
            if key == item:
                return node.values[i]

        # Return None if the key is not found.
        return None

    # Static method to borrow a key-value pair from the left sibling.
    # This operation is performed when a node has too few keys and needs to borrow from its left sibling.
    @staticmethod
    def _borrowLeft(node: Node, sibling: Node, parentIndex):
        if isinstance(node, LeafNode):
            # Borrow the last key-value pair from the left sibling.
            key = sibling.keys.pop(-1)
            data = sibling.values.pop(-1)
            node.keys.insert(0, key)
            node.values.insert(0, data)

            # Update the parent's key that separates the two nodes.
            node.parent.keys[parentIndex - 1] = key
        else:
            # Borrow the rightmost key from the parent and the leftmost key from the sibling.
            parent_key = node.parent.keys.pop(-1)
            sibling_key = sibling.keys.pop(-1)
            data: Node = sibling.values.pop(-1)
            data.parent = node

            # Update the parent node and add the borrowed data.
            node.parent.keys.insert(0, sibling_key)
            node.keys.insert(0, parent_key)
            node.values.insert(0, data)

    # Static method to borrow a key-value pair from the right sibling.
    # This operation is performed when a node has too few keys and needs to borrow from its right sibling.
    @staticmethod
    def _borrowRight(node: LeafNode, sibling: LeafNode, parentIndex):
        if isinstance(node, LeafNode):
            # Borrow the first key-value pair from the right sibling.
            key = sibling.keys.pop(0)
            data = sibling.values.pop(0)
            node.keys.append(key)
            node.values.append(data)
            node.parent.keys[parentIndex] = sibling.keys[0]
        else:
            # Borrow the leftmost key from the parent and the rightmost key from the sibling.
            parent_key = node.parent.keys.pop(0)
            sibling_key = sibling.keys.pop(0)
            data: Node = sibling.values.pop(0)
            data.parent = node

            # Update the parent node and add the borrowed data.
            node.parent.keys.append(sibling_key)
            node.keys.append(parent_key)
            node.values.append(data)

    # Static method to merge two nodes when a key is deleted.
    # This is used to maintain tree balance after deletion.
    @staticmethod
    def _mergeOnDelete(l_node: Node, r_node: Node):
        parent = l_node.parent

        # Find the parent node and remove the key separating the two nodes.
        jnk, index = BPlusTree._find(parent, l_node.keys[0]) 
        parent_key = parent.keys.pop(index)
        parent.values.pop(index)
        parent.values[index] = l_node

        # Merge the left and right nodes.
        if isinstance(l_node, LeafNode) and isinstance(r_node, LeafNode):
            l_node.nextLeaf = r_node.nextLeaf  # For leaf nodes, update next leaf pointer.
        else:
            l_node.keys.append(parent_key)
            # Update parent pointers for any child nodes.
            for r_node_child in r_node.values:
                r_node_child.parent = l_node

        # Combine keys and values of the two nodes.
        l_node.keys += r_node.keys
        l_node.values += r_node.values

    # Static method to get the previous sibling of a node.
    # This is used to access the left sibling of a node in case a borrow or merge operation is needed.
    @staticmethod
    def getPrevSibling(node: Node) -> Node:
        if node.isRoot() or not node.keys:
            return None
        jnk, index = BPlusTree._find(node.parent, node.keys[0])
        return node.parent.values[index - 1] if index - 1 >= 0 else None

    # Static method to get the next sibling of a node.
    # This is used to access the right sibling of a node in case a borrow or merge operation is needed.
    @staticmethod
    def getNextSibling(node: Node) -> Node:
        if node.isRoot() or not node.keys:
            return None
        jnk, index = BPlusTree._find(node.parent, node.keys[0])

        return node.parent.values[index + 1] if index + 1 < len(node.parent.values) else None

    # Method to get the leftmost leaf node.
    # This is useful for finding the smallest key in the BPlusTree.
    def getLeftmostLeaf(self):
        if not self.root:
            return None

        node = self.root
        # Traverse down to the leftmost leaf node.
        while not isinstance(node, LeafNode):
            node = node.values[0]

        return node

    # Method to get the rightmost leaf node.
    # This is useful for finding the largest key in the BPlusTree.
    def getRightmostLeaf(self):
        if not self.root:
            return None

        node = self.root
        # Traverse down to the rightmost leaf node.
        while not isinstance(node, LeafNode):
            node = node.values[-1]

    # Static method to insert an item between elements of a list.
    # This is used for interspersing elements (e.g., inserting separators between keys).
    @staticmethod
    def intersperse(lst, item):
        result = [item] * (len(lst) * 2)
        result[0::2] = lst
        return result


from graphviz import Digraph  # Importing the Digraph class from the graphviz library to create visualizations.

def read_numbers_from_file(file_path):
    """
    Reads a file containing a comma-separated list of numbers,
    converts them into integers, and returns them as a list.

    Parameters:
        file_path (str): The path to the file containing the numbers.

    Returns:
        list[int]: A list of integers parsed from the file.
    """
    with open(file_path, 'r') as file:  # Open the file in read mode.
        data = file.read()  # Read the entire content of the file.
    return list(map(int, data.strip().split(',')))  # Split the string by commas, strip leading/trailing whitespace, convert to integers, and return as a list.

def visualize_bplus_tree_graphviz(tree):
    """
    Visualizes a B+ Tree using Graphviz by creating a graphical representation of the tree structure.
    
    This function recursively traverses the tree, adds nodes and edges to a Graphviz Digraph, 
    and renders the tree as a PNG image.
    
    Parameters:
        tree (BPlusTree): The B+ Tree to be visualized.
    """
    
    def add_nodes_and_edges(node, graph, parent_id=None):
        """
        Recursively adds nodes and edges to the Graphviz Digraph, representing the B+ Tree.

        Parameters:
            node (Node): The current node being processed.
            graph (Digraph): The Graphviz Digraph object to which nodes and edges are added.
            parent_id (str, optional): The ID of the parent node (used to create edges between parent and child nodes).
        """
        if not node:  # If the node is None, do nothing and return.
            return
        node_id = id(node)  # Generate a unique ID for the node using the `id()` function.
        label = '|'.join(map(str, node.keys))  # Convert the keys of the node to a string and join them with '|'.

        # Add the node to the graph with the unique node ID. Set its label to the node's keys, 
        # and customize its appearance based on whether it's a leaf or internal node.
        graph.node(str(node_id), label=label, shape='rectangle', style='filled', fillcolor='lightgreen' if isinstance(node, LeafNode) else 'lightblue')
        
        # If the node has a parent, create an edge from the parent to the current node.
        if parent_id is not None:
            graph.edge(str(parent_id), str(node_id))
        
        # If the current node is not a leaf, recurse through its child nodes and add them to the graph.
        if not isinstance(node, LeafNode):
            for child in node.values:
                add_nodes_and_edges(child, graph, node_id)

    # Initialize a Digraph object for Graphviz with the name 'B+ Tree', 
    # specify the format as 'png', and set the layout engine to 'dot'.
    dot = Digraph(comment='B+ Tree', format='png', engine='dot')
    
    # Start the recursive process to add nodes and edges, beginning with the root of the tree.
    add_nodes_and_edges(tree.root, dot)

    # Render the graph to a PNG file named 'bplus_tree_visualization'.
    dot.render('bplus_tree_visualization')

    # View the generated visualization using the default viewer.
    dot.view()

if __name__ == '__main__':
    # Create an instance of the BPlusTree with an order of 3.
    bpt = BPlusTree(order=3)

    # Read the list of numbers from the file 'numbers.txt'.
    numbers = read_numbers_from_file('numbers.txt')
    
    # Print the list of numbers to the console (for debugging or verification purposes).
    # print(numbers)
    
    # Insert each number into the BPlusTree.
    for num in numbers:
        bpt.insert(num, num)

    # Visualize the BPlusTree structure using Graphviz after all numbers have been inserted.
    visualize_bplus_tree_graphviz(bpt)

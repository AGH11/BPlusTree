# B+ Tree Implementation

## Overview of B+ Tree

A **B+ Tree** is a self-balancing, tree data structure that maintains sorted data and allows for efficient insertion, deletion, and search operations. It is an extension of the B-tree, where all values are stored in leaf nodes, and internal nodes only store keys for navigation. B+ Trees are commonly used in databases and file systems due to their ability to handle large datasets with minimal disk I/O.

### Key Features of B+ Trees:
1. **Balanced Structure**: B+ trees ensure that the height of the tree remains balanced, meaning each path from the root to the leaves has the same length.
2. **Efficient Searching**: Since internal nodes only store keys for navigation, searching is faster.
3. **Leaf Node Linked List**: In B+ trees, all leaf nodes are linked to form a linked list for easy traversal of all records.
4. **Range Queries**: B+ trees excel in range queries due to the ordered nature of the leaf nodes.

### How B+ Tree Works:
- **Nodes**: There are two types of nodes in a B+ tree:
  - **Internal Nodes**: Store keys to guide searches.
  - **Leaf Nodes**: Store actual data or pointers to the data.
  
- **Inserting Data**: Data is inserted into the appropriate leaf node, and when a node becomes full, it splits into two, propagating the split upwards if necessary.
  
- **Searching**: To find a record, you traverse from the root to the appropriate leaf node using the keys stored in the internal nodes.
  
- **Deleting Data**: Deletion involves removing the key from the leaf node, and rebalancing the tree if necessary.

## Features of the Code

This implementation of the **B+ Tree** is a general-purpose data structure that supports efficient insertion, searching, and deletion operations. It features both **internal nodes** for index storage and **leaf nodes** for data storage, with **splitting** and **merging** capabilities to maintain balance.

### Classes:

1. **Node Class**:
   - Represents a generic tree node, either internal or leaf.
   - Manages key-value pairs and child nodes.
   - Handles splitting and merging operations when the node exceeds or falls below its capacity.

2. **LeafNode Class**:
   - Extends the Node class and represents a leaf node in the B+ Tree.
   - Stores actual data and has pointers to the previous and next leaf nodes for efficient range queries.
   - Implements the `add` method to insert key-value pairs and the `split` method to handle node overflow.

3. **BPlusTree Class**:
   - The main class representing the B+ Tree.
   - Includes methods for inserting, retrieving, splitting, and merging nodes.
   - Implements methods to handle rebalancing and traversal of the tree.

### Key Methods:
- **insert**: Adds a key-value pair to the tree. It splits nodes as necessary and propagates splits upwards to maintain the tree’s balance.
- **retrieve**: Searches for a key and retrieves its associated value.
- **split**: Splits a node into two nodes when it becomes full.
- **_mergeUp**: Merges a child node into its parent node after splitting.
- **_borrowLeft / _borrowRight**: These methods help balance the tree by borrowing keys from neighboring siblings.
- **_mergeOnDelete**: Merges nodes when a key is deleted.
- **getLeftmostLeaf**: Retrieves the leftmost leaf node, which is useful for performing range queries.


### Explanation of Key Methods:

- **split()**: This method is called when a node overflows. It creates two new nodes, redistributes the keys between them, and updates the parent node.
  
- **_find()**: A static method that helps in traversing the tree to find the correct node for inserting a new key. It compares the given key with the keys in the node and returns the corresponding child node and the index for insertion.

- **_mergeUp()**: A static method that merges a child node into its parent node after a split. This ensures that the parent nodes are updated with the new split structure.

- **_borrowLeft() and _borrowRight()**: These methods allow for borrowing keys from neighboring nodes when a node has too few keys. They help maintain balance by redistributing keys from siblings.

### Performance:
- **Time Complexity**:
  - **Insertion**: O(log n) due to the balanced nature of the B+ tree.
  - **Search**: O(log n) since we only need to traverse internal nodes.
  - **Deletion**: O(log n) as the tree may need to be rebalanced after deletion.

## Additional Features

- **Linked List of Leaf Nodes**: The leaf nodes in this implementation are linked together, making range queries efficient by simply traversing the linked list.
  
- **Automatic Rebalancing**: The B+ Tree automatically handles splits and merges to ensure that the tree remains balanced after insertions and deletions.

## Conclusion

This B+ Tree implementation is a powerful tool for efficiently storing and searching large datasets. With features like automatic balancing, range query support, and efficient insertions/deletions, it can be used in a wide variety of applications, especially in databases and filesystems.

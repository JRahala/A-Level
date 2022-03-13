   
""" Node class for Trie """
from re import search
class TrieNode:
    def __init__(self):
        self.value = set()
        self.children = {}

""" Class containing Trie functions and root node """
class Trie:
    def __init__(self):
        self.root_node = TrieNode()

    # insert new value into trie with filters 
    def insert(self, new_value, filters):
        # start from the root of the trie
        current_node = self.root_node
        # iterate through all filters (alphabetically)
        filters = sorted(filters)
        for current_filter in filters:
            # does a trie node exist, with the filter?
            if current_filter in current_node.children:
                current_node = current_node.children[current_filter]
            # else create a new node
            else:
                current_node.children[current_filter] = TrieNode()
                current_node = current_node.children[current_filter]
        # add new_value to current_node
        current_node.value.add(new_value)

    # return list(trie nodes) with filters and more
    def dirty_search(self, filters):
        # start from the root of the trie
        current_node = self.root_node
        # iterate through filters (reversed alphabetically)
        remaining_filters = list(sorted(filters, reverse=True))
        
        # recusive_search
        def dfs(node):

            if node == None: 
                return []

            search_results = list()

            if remaining_filters == list():
                for value in node.value:
                    search_results.append(value)
                for key in node.children:
                    search_results = search_results + dfs(node.children[key])

            else:
                # search all children where current filter before or equal alphabetically to first search filters
                for key in node.children:
                    if key <= remaining_filters[-1]:
                        used_filter = remaining_filters.pop()
                        search_results = search_results + dfs(node.children[key])
                        remaining_filters.append(used_filter)
                    else:
                        break
                
            return search_results

        return dfs(current_node)


    # return list(trie nodes) with exactly filters
    def search(self, filters):
        # start from the root of the trie
        current_node = self.root_node
        # iterate through all filters (alphabetically)
        filters = sorted(filters)
        for current_filter in filters:
            # does a trie node exist, with the filter?
            if current_filter in current_node.children:
                current_node = current_node.children[current_filter]
            # else return empty list
            else:
                return []

        # dfs search for all nodes below current node
        def dfs(node):
            # add values of current node
            search_results = list(node.value)
            # search child nodes
            for key in node.children:
                search_results += dfs(node.children[key])
            return search_results

        return dfs(current_node)

    # delete value given value and filters
    def delete(self, value, filters):
        # start from the root of the trie
        current_node = self.root_node
        # iterate through all filters (alphabetically)
        filters = sorted(filters)
        for current_filter in filters:
            # does a trie node exist, with the filter?
            if current_filter in current_node.children:
                current_node = current_node.children[current_filter]
            # else return None
            else:
                return None
        # remove value from current_node.value
        current_node.value.discard(value)
        return None

    # peek at the structure using recursive depth first search
    def peek(self):
        def dfs(node, layer):
            # print values at current node
            print("-" * layer * 10, end="")
            print([value for value in node.value])
            # search child nodes
            for key in node.children:
                dfs(node.children[key], layer + 1)
        # start serch at root node
        dfs(self.root_node, 1)
    
""" Stack Node data structure """
class StackNode:
    def __init__(self, value = None, next_node = None):
        self.value = value
        self.next_node = next_node

""" Stack data structure """
class Stack:
    def __init__(self):
        self.head = None

    # check if stack is empty
    def is_empty(self):
        return self.head == None

    # add new stack node to stack
    def push(self, value):
        # create new stack node
        new_node = StackNode(value)
        # check if stack is empty
        if not self.is_empty():
            # current head point to new_node
            new_node.next_node = self.head
        # replace head with new_node
        self.head = new_node
        return None

    # remove last item from the stack
    def pop(self):
        # if stack is empty, return None
        if self.is_empty():
            return None
        # save value in current_head
        last_value = self.head.value
        # set next element to new head
        self.head = self.head.next_node
        # return latest value
        return last_value

    # create an array of all the values in the stack in order (latest -> earliest)
    def array_copy(self):
        # array to store all the values within the stack
        copied = []
        # while stack not empty add elements to the copied
        current_node = self.head
        while current_node != None:
            copied.append(current_node.value)
            current_node = current_node.next_node
        return copied

    # display all nodes held within the stack
    def display(self):
        # iterate through all stack nodes starting at the head
        current_node = self.head
        while current_node != None:
            # print the node value
            print(current_node.value)
            # iterate to the next_node
            current_node = current_node.next_node
        return None

# only run following tests, when file is executed
if __name__ == "__main__":

    # create Trie
    example_trie = Trie()
    example_trie.insert("A B C", ("A", "B", "C"))
    example_trie.insert("B C", ("B", "C"))

    results = example_trie.dirty_search(list())
    print(results)
from collections import OrderedDict


def get_value_by_tree_path(element: dict, tree_path: str):
    """This function gets value from a dict using a string path separated with points.
    e. g.
        using the following dict:
            person = {'person': {'surname': 'blabla', 'age': 25}}
        to get the surname:
            _get_value_by_tree_path(person, 'person.surname')

    Args:
        element (dict): Element to get values using tree path
        tree_path (str): String separated with points representing the tree path
    Returns:
        recovered value using tree_path
    """
    element = element.copy()
    tree_path = tree_path.split('.')

    for tree_node in tree_path:
        element = element[tree_node]
    return element


def add_value_by_tree_path(element: OrderedDict, tree_path: str, value: object) -> None:
    """Add values in dictionary using path separated with points
    Args:
        element (OrderedDict): Element where value is inserted (in-place)
        tree_path (str): String separated with points representing the tree path
        value (object): Value to be inserted
    Returns:
        None
    """
    tree_path = tree_path.split('.')

    _pelement = element
    _element_index = -1
    for tree_node in tree_path:
        # walking through tree nodes
        if tree_node not in _pelement:
            if isinstance(_pelement, list):
                for index in range(0, len(_pelement)):
                    for key in _pelement[index]:
                        if _pelement[index][key] == tree_node:
                            _element_index = index
                            break
                # if no key in returned from search, add a new element in last position
                if _element_index == -1:
                    _pelement.append(OrderedDict())
            else:
                _pelement[tree_node] = OrderedDict()

            # check if is the last element
            if tree_node == tree_path[-1]:
                if isinstance(_pelement, list):
                    _pelement[_element_index] = value
                else:
                    _pelement[tree_node] = value
        if isinstance(_pelement, list):
            _pelement = _pelement[_element_index]
        else:
            _pelement = _pelement[tree_node]

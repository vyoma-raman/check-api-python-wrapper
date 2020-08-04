import time
def strip(query_response):
    """
    :str query_response: the dictionary that you want to flatten into a list
    :return: a list of nodes
    """
    nodes = []
    for key, value in query_response.items():
        if key == "edges":
            for node in value:
                nodes.append(node)
        elif isinstance(value, list):
            for item in value:
                nodes.extend(strip(item))
        else:
            nodes.extend(strip(value))
    return nodes

def pivot_dict(nodes, key, values):
    """
    :list nodes: list of nodes - each node is a dictionary
    :str key: the key to pivot on
    :str or list values: the new values of the dictionary
    :return: new dictionary
    """
    new_dict = {}
    for node in nodes:
        node = node["node"]
        new_values = None
        if isinstance(values, list):
            new_values = []
            for k, v in node.items():
                if k in values:
                    new_values.append(v)
        else:
            new_values = node[values]
        new_dict[node[key]] = new_values
    return new_dict

def epoch_to_datetime(epoch):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(epoch)))

import plotly.graph_objects as go
import random
import networkx as nx
import os
from collections import deque

from twitterRequests import *

def get_user_list(username):
    file_path = 'data/user_list/' + username + '.json'
    data = []
    if os.path.isfile(file_path):
        with open(file_path) as json_file:
            data = json.load(json_file)
    else:
        data = get_list(username, 'friends')
        if len(data) > 0:
            with open(file_path, 'w') as outfile:
                json.dump(data, outfile)

    return data

def get_ids_list(username):
    file_path = 'data/ids/' + username + '.json'
    data = []
    if os.path.isfile(file_path):
        with open(file_path) as json_file:
            data = json.load(json_file)
    else:
        data, rate_limit = get_ids(username, 'friends')
        print(rate_limit)
        if not rate_limit:
            with open(file_path, 'w') as outfile:
                json.dump(data, outfile)

    return data

def mount_graph():
    user = input('Whats your Twitter username? ')
    friends = get_user_list(user)
    verified = []
    for friend in friends:
        if friend['verified']:
            verified.append(friend)

    for famous in verified:
        friends.remove(famous)

    return create_graph(friends, user)

def create_graph(vec, user):

    G = nx.Graph()

    for i in range(0,len(vec)):
        G.add_node(i, name=vec[i]['name'], id=vec[i]['id'], username=vec[i]['screen_name'], visited=False)

    nodes = G.nodes(data=True)
    for out_node in nodes:
        username = str(out_node[1]['username'])
        print(username)
        related_friends = get_ids_list(username)
        for node in nodes:
            for friend_id in related_friends:
                if(friend_id == node[1]['id']):
                    G.add_edge(out_node[0], node[0], layer=0, traveled=False)

    title = 'Grafo de quem ' + user + ' segue no Twitter'
    return show_graph(G, title)

def show_graph(G, text, colors = [], path = []):

    pos = nx.fruchterman_reingold_layout(G)

    edge_x = []
    edge_y = []
    for e in G.edges():
        if e[0] not in path and e[1] not in path:
            edge_x.extend([pos[e[0]][0], pos[e[1]][0], None])
            edge_y.extend([pos[e[0]][1], pos[e[1]][1], None])

    p_edge_x = []
    p_edge_y = []
    for i in range(0,len(path) - 1):
        edge = (path[i],path[i+1])
        p_edge_x.extend([pos[edge[0]][0], pos[edge[1]][0], None])
        p_edge_y.extend([pos[edge[0]][1], pos[edge[1]][1], None])

    edge_trace1 = go.Scatter(
            x=p_edge_x, y=p_edge_y,
            line=dict(width=1, color='#0F0'),
            hoverinfo='none',
            mode='lines')

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x =[pos[k][0] for k in range(len(pos))]
    node_y=[pos[k][1] for k in range(len(pos))]

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=colors,
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(G.nodes[node]['name'] + ' \n@' + G.nodes[node]['username'])

    if len(colors) > 0:
        node_trace.marker.color = colors
    else:
        node_trace.marker.color = node_adjacencies

    node_trace.text = node_text
    fig = go.Figure(data=[edge_trace, edge_trace1, node_trace],
                    layout=go.Layout(
                title='<b>'+text+'</b>',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    annotations=[dict(
                        text="Feito por Alexandre Miguel e Gabriela Guedes",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002)],
                    xaxis=dict(showgrid=False, zeroline=False,
                            showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.show()
    return G

def search_path(from_user, to_user, G):
    return nx.shortest_path(G, from_user, to_user)

def get_user_graph_id(username, G):
    for i in range(0, len(G)):
        if G.nodes[i]['username'] == username:
            return i
    return -1

def breadth_first_search(username):
    nodes = G.nodes(data=True)
    origin = get_user_graph_id(username, G)
    size = len(nodes)
    path = []
    if (origin != -1):
        nodes[origin]['visited'] = True
        path = list(G.adj[origin])
        for init_pos in path:
            nodes[init_pos]['visited'] = True
            G.edges[origin, init_pos]['traveled'] = True
            G.edges[origin, init_pos]['layer'] = 1
        for pos in path:
            neighbours = list(G.adj[pos])
            for n_pos in neighbours:
                if(nodes[n_pos]['visited']):
                    if(G.edges[origin, init_pos]['layer'] == 0):
                        G.edges[origin, init_pos]['layer'] = 2
                else:
                    path.append(n_pos)
                    nodes[n_pos]['visited'] = True
                    G.edges[pos, n_pos]['traveled'] = True
                    G.edges[pos, n_pos]['layer'] = 1
    node_colors = []
    for n in range(size):
        if(n == origin):
            node_colors.append("blue")
        elif(nodes[n]['visited'] == True):
            node_colors.append("red")
        else:
            node_colors.append("green")
    
    return node_colors

def show_options():
    os.system('clear')
    print('========== MENU ==========')
    print('1 - Do BFS from one user to all it can reach')
    print('2 - Do BFS from one user to another')
    print('3 - Exit')

def menu(G):
    show_options()
    op = input('\noption: ')

    if op == '1':
        usr3 = input('\nPerform Breadth First Search from user (use name without @): ')
        node_colors = breadth_first_search(usr3)
        title = 'Busca por Largura começando em ' + usr3
        show_graph(G, title , node_colors)
        menu(G)

    elif op == '2':
        print('\nFind the shortest path between two users:')
        usr1 = input('From: ')
        usr2 = input('To: ')
        id1 = get_user_graph_id(usr1, G)
        id2 = get_user_graph_id(usr2, G)
        if(not (id1 == -1) and  not (id2 == -1)):
            path = nx.shortest_path(G, id1, id2)
            print('\nShortest path:')
            for id in path:
                print(G.nodes[id]['name'])

            node_colors = ["blue" if n in path else "red" for n in G.nodes()]
            title = 'Menor caminho entre ' + G.nodes[id1]['name'] + ' e ' + G.nodes[id2]['name']
            show_graph(G, title , node_colors, path)
        else:
            input('Username not found. Press ENTER to return.')

        menu(G)

    elif op == '3':
        exit

    else:
        input('Option not found. Press ENTER to return.')
        menu(G)



if __name__ == "__main__":
    create_barear_token()
    G = mount_graph()
    menu(G)

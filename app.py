import streamlit as st
import pandas as pd
from collections import defaultdict

@st.cache_data
def load_routes():
    df = pd.read_excel("frontier_flights_list.xlsx", sheet_name = "single_destination_coded")  
    graph = defaultdict(list)
    for _, row in df.iterrows():
        graph[row["origin"]].append(row["destination"])
    return graph


def build_reverse_graph(graph):
    reversed_graph = defaultdict(list)
    for origin, destinations in graph.items():
        for dest in destinations:
            reversed_graph[dest].append(origin)
    return reversed_graph


def bfs_destinations(graph, start, max_layovers):
    visited = set()
    queue = [(start, 0)]
    while queue:
        current, layovers = queue.pop(0)
        if layovers > max_layovers:
            continue
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, layovers + 1))
    visited.discard(start)
    return visited


def round_trip_destinations(graph, start, max_outbound, max_return, reverse_graph):
    outbound = bfs_destinations(graph, start, max_outbound)
    round_trip = set()
    for dest in outbound:
        returnable = bfs_destinations(reverse_graph, dest, max_return)
        if start in returnable:
            round_trip.add(dest)
    return round_trip

def shared_round_trip_destinations(graph, origins, max_outbound, max_return):
    reverse_graph = build_reverse_graph(graph)
    all_reachable = [
        round_trip_destinations(graph, origin, max_outbound, max_return, reverse_graph)
        for origin in origins
    ]
    return set.intersection(*all_reachable) if all_reachable else set()



st.title("Frontier Go Wild Trip Finder")

flight_graph = load_routes()

airport_list = sorted(list(flight_graph.keys()))
origins = st.multiselect("Select up to 5 origin airports:", airport_list, max_selections=5)
outbound = st.slider("Max Outbound Layovers", 0, 2, 1)
return_trip = st.slider("Max Return Layovers", 0, 2, 1)

if st.button("Find Shared Round-Trip Destinations"):
    if not origins:
        st.warning("Please select at least one starting airport.")
    else:
        result = shared_round_trip_destinations(flight_graph, origins, outbound, return_trip)
        if result:
            st.success(f"{len(result)} shared round-trip destinations found:")
            st.write(sorted(result))
        else:
            st.info("No shared round-trip destinations found with these constraints.")

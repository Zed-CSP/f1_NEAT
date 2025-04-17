import graphviz
import matplotlib.pyplot as plt
import numpy as np
from neat.nn import FeedForwardNetwork

class NetworkVisualizer:
    def __init__(self, save_dir='network_visualizations'):
        self.save_dir = save_dir
        import os
        os.makedirs(save_dir, exist_ok=True)

    def visualize_topology(self, genome, generation, config):
        """Visualize the neural network topology using graphviz."""
        dot = graphviz.Digraph(comment=f'Neural Network Topology - Generation {generation}')
        dot.attr(rankdir='LR')  # Left to right layout
        dot.attr('node', shape='circle', style='filled', fontname='Arial')
        dot.attr('edge', fontname='Arial')

        # Get all node IDs from both nodes and connections
        node_ids = set(genome.nodes.keys())
        for conn in genome.connections.values():
            if conn.enabled:
                node_ids.add(conn.key[0])
                node_ids.add(conn.key[1])

        # Add nodes
        for node_id in node_ids:
            # Correctly identify node types based on NEAT implementation
            if node_id < 0:  # Input nodes (negative IDs)
                color = "lightblue"
                label = f"Input {abs(node_id)}"
            elif node_id <= 3:  # Output nodes (0-3)
                # Map output nodes to their functions
                output_functions = {
                    0: "Turn Left",
                    1: "Turn Right",
                    2: "Brake",
                    3: "Accelerate"
                }
                color = "lightgreen"
                label = output_functions[node_id]
            else:  # Hidden nodes (4 and above)
                color = "lightgray"
                label = f"Hidden {node_id}"

            # Add node
            dot.node(str(node_id), label, fillcolor=color)

        # Add connections
        for conn in genome.connections.values():
            if conn.enabled:
                # Add edge with weight
                dot.edge(str(conn.key[0]), 
                        str(conn.key[1]), 
                        label=f'{conn.weight:.2f}',
                        color='blue' if conn.weight > 0 else 'red',
                        penwidth=str(abs(conn.weight)))

        # Save the visualization
        dot.render(f'{self.save_dir}/topology_gen_{generation}', format='png', cleanup=True)
        return f'{self.save_dir}/topology_gen_{generation}.png'

    def visualize_weights(self, genome, generation):
        """Visualize the weight matrix using matplotlib."""
        # This function is kept for compatibility but doesn't do anything
        return None

    def visualize_network(self, genome, generation, config):
        """Create network visualization."""
        topology_path = self.visualize_topology(genome, generation, config)
        return topology_path, None 
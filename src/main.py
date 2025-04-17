import neat
import pygame
import sys
from simulation.simulation import run_simulation
from rendering.renderer import Renderer
from visualization.network_visualizer import NetworkVisualizer

if __name__ == "__main__":
    # Initialize renderer and visualizer
    renderer = Renderer()
    visualizer = NetworkVisualizer()
    
    # Load Config
    config_path = "./config/config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                              neat.DefaultReproduction,
                              neat.DefaultSpeciesSet,
                              neat.DefaultStagnation,
                              config_path)

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    def eval_genomes(genomes, config):
        # Run the simulation
        run_simulation(genomes, config, renderer)
        
        # Find the best genome in this generation
        best_genome = max(genomes, key=lambda x: x[1].fitness)[1]
        
        # Visualize the best network
        visualizer.visualize_network(best_genome, renderer.current_generation, config)
    
    # Run Simulation For A Maximum of 1000 Generations
    population.run(eval_genomes, 1000)
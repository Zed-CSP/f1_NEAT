import neat
import pygame
import sys
from simulation.simulation import run_simulation
from rendering.renderer import Renderer

if __name__ == "__main__":
    # Initialize renderer once
    renderer = Renderer()
    
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
    
    # Run Simulation For A Maximum of 1000 Generations
    population.run(lambda genomes, config: run_simulation(genomes, config, renderer), 1000)
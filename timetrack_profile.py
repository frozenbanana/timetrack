import cProfile
import pstats
from timetrack.cli import cli

print("Start")
with cProfile.Profile() as profiler:
    cli(['status'])
    print("Done 2")
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats()
    print("Done")

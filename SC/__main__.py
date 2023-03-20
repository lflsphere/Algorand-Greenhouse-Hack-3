from pathlib import Path

from lab import my_lab

print("Compiling Beaker smart contracts...")
my_lab.distill(
    output_dir=(Path(__file__).parent / "artifacts"),
)

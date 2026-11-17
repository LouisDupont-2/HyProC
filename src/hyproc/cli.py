"""Command-line entry point for HyProC."""

import argparse
from datetime import datetime
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hyproc", description="Run a HyProC simulation or open the desktop application."
    )
    subcommands = parser.add_subparsers(dest="command")
    command = subcommands.add_parser("simulate", help="Run a saved simulation without opening the GUI.")
    command.add_argument("simulation", type=Path, help="Saved HyProC simulation JSON.")
    command.add_argument("--output", type=Path, required=True, help="Path for the resulting simulation JSON.")
    command.add_argument("--srim-path", default="", help="SRIM installation directory when the file uses SRIM.")
    args = parser.parse_args(argv)
    if args.command is None:
        from .UI import main as open_desktop

        open_desktop()
        return 0

    from .simulation import simulate
    from .simulation_io import load_simulation, save_simulation

    try:
        if args.simulation.resolve() == args.output.resolve():
            raise ValueError("Choose an output file different from the input simulation.")
        simulation = load_simulation(args.simulation)
        result = simulate(simulation, srim_path=args.srim_path)
        simulation["simulated_curve"] = {"energy": result.energy, "yield": result.yield_values}
        simulation["saved_at"] = datetime.now().isoformat(timespec="seconds")
        save_simulation(args.output, simulation)
    except (OSError, AttributeError, IndexError, KeyError, TypeError, ValueError) as error:
        command.exit(1, f"hyproc simulate: {error}\n")
    print(f"Simulation saved to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

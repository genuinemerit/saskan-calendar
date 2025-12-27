# Experiments CLI quick reference

All commands run via Poetry:

- `poetry run saskan-experiments --help` – list top-level commands.
- `poetry run saskan-experiments geo` – simple distance demo.
- `poetry run saskan-experiments graph` – simple shortest-path demo.
- `poetry run saskan-experiments saskan-sim [OPTIONS]` – run the Saskan Lands simulation.

`saskan-sim` options (Typer auto-docs also show these):

- `--steps INTEGER` – number of ticks to run (default 8).
- `--seed INTEGER` – set for reproducible runs.
- `--scenario TEXT` – named preset to set the seed (e.g., `baseline`, `northern-expansion`, `coastal-boom`, `great-migration`).
- `--tick-unit TEXT` – label for a tick (`year`, `season`, `generation`, etc.; default `year`).
- `--tick-length FLOAT` – length of one tick in the chosen unit (default 1.0).
- `--snapshot-every INTEGER` – write JSON snapshots every N steps (0 disables).
- `--snapshot-dir PATH` – directory for snapshots (default `data/experiments/saskan`; created if missing).

Examples:

- `poetry run saskan-experiments saskan-sim --steps 5 --seed 123`
- `poetry run saskan-experiments saskan-sim --scenario baseline --snapshot-every 2`
- `poetry run saskan-experiments saskan-sim --tick-unit season --tick-length 0.25`
- `poetry run saskan-experiments saskan-map --scenario great-migration --steps 30 --seed 4040`
- `poetry run saskan-experiments saskan-plot --scenario great-migration --steps 30 --seed 4040` (requires `matplotlib`; saves PNG)

Snapshots (when enabled) are JSON files named `step_XXXX.json` with meta/config/state/events.

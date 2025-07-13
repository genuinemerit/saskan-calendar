import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class SynthPlugin:
    name: str
    path: str
    type: str  # e.g., "VST2", "VST3", "LV2", "AU"
    categories: List[str] = field(default_factory=list)
    is_installed: bool = True


def discover_synth_plugins_unix(base_dirs: List[str] = None) -> List[SynthPlugin]:
    """
    Scans standard *nix directories for synth plugin files.
    Currently supports VST2, VST3, and LV2 formats.
    """
    if base_dirs is None:
        base_dirs = [
            os.path.expanduser("~/.vst"),
            os.path.expanduser("~/.vst3"),
            os.path.expanduser("~/.lv2"),
            "/usr/lib/vst",
            "/usr/local/lib/vst",
            "/usr/lib/vst3",
            "/usr/local/lib/vst3",
            "/usr/lib/lv2",
            "/usr/local/lib/lv2",
        ]

    found_plugins = []
    seen_paths = set()

    for base_dir in base_dirs:
        if not os.path.isdir(base_dir):
            continue
        for root, _, files in os.walk(base_dir):
            for f in files:
                if f.endswith((".so", ".dll", ".dylib")) or base_dir.endswith("lv2"):
                    full_path = os.path.join(root, f)
                    if full_path in seen_paths:
                        continue
                    seen_paths.add(full_path)
                    plugin_type = (
                        "VST3"
                        if "/vst3" in root
                        else "VST2" if "/vst" in root else "LV2"
                    )
                    found_plugins.append(
                        SynthPlugin(
                            name=os.path.splitext(f)[0],
                            path=full_path,
                            type=plugin_type,
                        )
                    )

    return found_plugins


if __name__ == "__main__":
    plugins = discover_synth_plugins_unix()
    for plugin in plugins:
        print(f"{plugin.name} | {plugin.type} | {plugin.path}")

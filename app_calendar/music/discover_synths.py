import os
from dataclasses import dataclass, field
from typing import List


import os
import platform
from dataclasses import dataclass, field
from typing import List

@dataclass
class SynthPlugin:
    name: str
    path: str
    type: str  # e.g., "VST2", "VST3", "LV2", "AU"
    categories: List[str] = field(default_factory=list)
    is_installed: bool = True

def get_default_plugin_dirs() -> List[str]:
    system = platform.system()
    if system == "Linux":
        return [
            os.path.expanduser("~/.vst"),
            os.path.expanduser("~/.vst3"),
            os.path.expanduser("~/.lv2"),
            "/usr/lib/vst",
            "/usr/local/lib/vst",
            "/usr/lib/vst3",
            "/usr/local/lib/vst3",
            "/usr/lib/lv2",
            "/usr/local/lib/lv2"
        ]
    elif system == "Darwin":  # macOS
        return [
            "/Library/Audio/Plug-Ins/VST",
            "/Library/Audio/Plug-Ins/VST3",
            "/Library/Audio/Plug-Ins/Components",  # AU
            os.path.expanduser("~/Library/Audio/Plug-Ins/VST"),
            os.path.expanduser("~/Library/Audio/Plug-Ins/VST3"),
            os.path.expanduser("~/Library/Audio/Plug-Ins/Components")
        ]
    elif system == "Windows":
        return [
            os.path.expandvars("%PROGRAMFILES%\\VSTPlugins"),
            os.path.expandvars("%PROGRAMFILES%\\Steinberg\\VSTPlugins"),
            os.path.expandvars("%PROGRAMFILES%\\Common Files\\VST2"),
            os.path.expandvars("%PROGRAMFILES%\\Common Files\\VST3")
        ]
    else:
        return []

def discover_synth_plugins(base_dirs: List[str] = None) -> List[SynthPlugin]:
    if base_dirs is None:
        base_dirs = get_default_plugin_dirs()

    found_plugins = []
    seen_paths = set()

    for base_dir in base_dirs:
        if not os.path.isdir(base_dir):
            continue
        for root, _, files in os.walk(base_dir):
            for f in files:
                if f.endswith(('.so', '.dll', '.dylib')) or any(base_dir.endswith(tag) for tag in ['lv2', 'Components']):
                    full_path = os.path.join(root, f)
                    if full_path in seen_paths:
                        continue
                    seen_paths.add(full_path)
                    if "/vst3" in root or "\\VST3" in root:
                        plugin_type = "VST3"
                    elif "/vst" in root or "\\VST" in root:
                        plugin_type = "VST2"
                    elif "lv2" in root:
                        plugin_type = "LV2"
                    elif "Components" in root:
                        plugin_type = "AU"
                    else:
                        plugin_type = "Unknown"
                    found_plugins.append(SynthPlugin(
                        name=os.path.splitext(f)[0],
                        path=full_path,
                        type=plugin_type
                    ))

    return found_plugins

if __name__ == "__main__":
    plugins = discover_synth_plugins()
    for plugin in plugins:
        print(f"{plugin.name} | {plugin.type} | {plugin.path}")

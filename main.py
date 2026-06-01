from pathlib import Path
import sys


if __name__ == "__main__":
    src_path = Path(__file__).resolve().parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from lcs.cli import main

    main(command_name="python main.py")

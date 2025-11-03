#!/usr/bin/env python3
import argparse
import subprocess
import time
from pathlib import Path

IODEPTH = [1, 4, 16, 32, 64]
SCRIPT_DIR = Path("./scripts")


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("device")
    parser.add_argument("-o", dest="output_dir", type=Path)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    output_dir: Path = args.output_dir
    output_dir.mkdir(exist_ok=True, parents=True)

    start = time.time()

    for depth in IODEPTH:
        print("depth", depth)

        # RANDOM WRITES
        runfio(
            args.device,
            depth,
            SCRIPT_DIR / "rand-write.fio",
            output_dir / f"rand_w_{args.device}_{depth}iodepth_1threads",
        )

        # RANDOM READS
        runfio(
            args.device,
            depth,
            SCRIPT_DIR / "rand-read.fio",
            output_dir / f"rand_r_{args.device}_{depth}iodepth_1threads",
        )

        # SEQUENTIAL WRITES
        runfio(
            args.device,
            depth,
            SCRIPT_DIR / "write.fio",
            output_dir / f"seq_w_{args.device}_{depth}iodepth",
        )

        # SEQUENTIAL READS
        runfio(
            args.device,
            depth,
            SCRIPT_DIR / "read.fio",
            output_dir / f"seq_r_{args.device}_{depth}iodepth",
        )

        # Generate plots
        subprocess.run(
            [
                "./plotall.sh",
                str(output_dir),
                args.device,
                "1",
                *map(str, IODEPTH),
            ],
            check=True,
        )

    end_time = time.time()
    elapsed = int(end_time - start)

    h = elapsed // 3600
    m = (elapsed % 3600) // 60
    s = elapsed % 60

    print("\n\n  Overall time elapsed: {}h:{}m:{}s".format(h, m, s))


def runfio(device: str, depth: int, script: Path, output_dir: Path):
    if output_dir.exists():
        return

    cmd = [ 
        "./runfio.sh",
        "-d", device,
        "-n", "1",
        "-i", str(depth),
        "-f", str(script),
        "-o", str(output_dir),
    ]  # fmt: skip
    print(" ".join(cmd))

    subprocess.run(
        cmd,
        check=True,
    )


if __name__ == "__main__":
    main()

"""Download archived waveforms and station metadata for the windows in config.toml.

Usage: python scripts/download_archive.py [dataset ...]
With no arguments, downloads every [archive.*] dataset plus StationXML.
Writes to <data.dir>/<dataset>/<NET>.<STA>.mseed and <data.dir>/stations/<NET>.xml.
Existing files are skipped, so the script is safe to re-run.
"""
import sys
import tomllib
from pathlib import Path

from obspy import UTCDateTime
from obspy.clients.fdsn import Client

ROOT = Path(__file__).resolve().parent.parent
cfg = tomllib.loads((ROOT / "config.toml").read_text())
src = cfg["source"]
data_dir = Path(cfg["data"]["dir"]).expanduser()
client = Client(cfg["fdsn"]["client"])


def download_stations():
    out = data_dir / "stations" / f"{src['network']}.xml"
    if out.exists():
        print(f"skip  {out} (exists)")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    inv = client.get_stations(
        network=src["network"],
        station=",".join(src["stations"]),
        location=src["location"] or "--",
        channel=src["channels"],
        level="response",
    )
    inv.write(str(out), format="STATIONXML")
    print(f"wrote {out}")


def download_dataset(name):
    win = cfg["archive"][name]
    start, end = UTCDateTime(win["start"]), UTCDateTime(win["end"])
    for sta in src["stations"]:
        out = data_dir / name / f"{src['network']}.{sta}.mseed"
        if out.exists():
            print(f"skip  {out} (exists)")
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        print(f"fetch {src['network']}.{sta} {src['channels']} {start} -> {end} ...", flush=True)
        st = client.get_waveforms(
            network=src["network"],
            station=sta,
            location=src["location"] or "--",
            channel=src["channels"],
            starttime=start,
            endtime=end,
        )
        st.write(str(out), format="MSEED")
        print(f"wrote {out}  ({out.stat().st_size / 1e6:.1f} MB)")
        for tr in st:
            print(f"      {tr.id} {tr.stats.starttime} -> {tr.stats.endtime} {tr.stats.npts} samples")


if __name__ == "__main__":
    names = sys.argv[1:] or list(cfg["archive"])
    unknown = [n for n in names if n not in cfg["archive"]]
    if unknown:
        sys.exit(f"unknown dataset(s): {unknown}. Known: {list(cfg['archive'])}")
    download_stations()
    for n in names:
        download_dataset(n)

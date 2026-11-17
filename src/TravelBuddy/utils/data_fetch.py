####### RUN WITH python src/fetch_data.py
from TravelBuddy.utils.paths import DATA
import io
import pathlib
import zipfile
import requests

STEM = "On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)"
MIRROR = "https://cs.oswego.edu/~mmorse3/travel-buddy-data/"
BTS_BASE = "https://transtats.bts.gov/PREZIP/"

FILES = {
    "2025_OCTOBER": "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_10.zip",
    "2026_JANUARY": "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2026_1.zip",
    "2026_APRIL": "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2026_4.zip",
    "2026_JULY": "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2026_7.zip",
}


def download(label, bts_url):
    """Return (kind, bytes) where kind is 'csv' or 'zip'."""
    try:
        r = requests.get(BTS_BASE + bts_url, timeout=900)
        r.raise_for_status()
        print("  from mirror")
        return "csv", r.content
    except Exception as e:
        print(f"  mirror unavailable ({type(e).__name__}), using BTS, this is slow as sin")
        r = requests.get(bts_url, timeout=900)
        r.raise_for_status()
        return "zip", r.content


def main():
    DATA.mkdir(exist_ok=True)

    for label, bts_url in FILES.items():
        target = DATA / f"{STEM}_{label}.csv"

        if target.exists():
            print(f"{label}: already have it ({target.stat().st_size / 1e6:.0f} MB)")
            continue

        print(f"{label}: downloading")
        _, blob = download(label, bts_url)

        if blob[:2] == b"PK":                         # a zip... whatever the src called it
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                names = [n for n in z.namelist() if n.lower().endswith(".csv")]
                if not names:
                    raise SystemExit(f"{label}: no CSV inside archive")
                target.write_bytes(z.read(names[0]))
        else:
            target.write_bytes(blob)

        size = target.stat().st_size
        if size < 1_000_000:
            target.unlink()
            raise SystemExit(f"{label}: only {size} bytes. Bad download, file remove")

        print(f"  -> {target.name}  ({size / 1e6:.0f} MB)")

    print("\nDone. Next: python -m TravelBuddy.utils.make_arcs")


if __name__ == "__main__":
    main()

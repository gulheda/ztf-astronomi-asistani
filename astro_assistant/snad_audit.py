"""Inspect a bounded sample of the public SNAD archives; no training."""
import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

SOURCES = {
    "artefact": ("Artefacts.zip", 33051444, "66c2e35ad0a3284842b5374211043098"),
    "nominal": ("Nominals.zip", 32707445, "d4b993aa502d844d64f9734141b801ca"),
}


def inspect_archive(path, sample_size=6, depth=0):
    import numpy as np
    from astropy.io import fits
    samples = []
    with ZipFile(path) as archive:
        members = archive.infolist()
        if len(members) > 10000 or sum(m.file_size for m in members) > 512_000_000:
            raise ValueError("Archive exceeds declared inspection limits")
        candidates = sorted((m for m in members if m.filename.lower().endswith(".fits")), key=lambda m:m.filename)
        if not candidates:
            nested = [m for m in members if m.filename.lower().endswith(".zip")]
            if depth >= 1 or not nested or len(nested)>4:
                raise ValueError("Unsupported or excessive nested archive layout")
            children = {}
            for member in nested:
                if member.file_size > 64_000_000:
                    raise ValueError("Nested archive exceeds limit")
                children[member.filename] = inspect_archive(io.BytesIO(archive.read(member)), sample_size, depth+1)
            return dict(member_count=len(members), first_paths=[m.filename for m in members[:12]],
                fits_count=sum(c["fits_count"] for c in children.values()), nested_archives=children, sample_only=True)
        # Bounded deterministic spread, covering both image sizes when present.
        indices = sorted(set(round(i*(len(candidates)-1)/max(1,sample_size-1)) for i in range(sample_size)))
        for i in indices:
            member = candidates[i]
            if member.file_size > 1_000_000:
                raise ValueError("FITS sample exceeds 1 MB")
            payload = archive.read(member)  # no archive paths are extracted
            with fits.open(io.BytesIO(payload), memmap=False) as hdus:
                header = hdus[0].header
                if header.get("NAXIS") != 2 or any(not 1 <= header.get(k,0) <= 128 for k in ("NAXIS1","NAXIS2")):
                    raise ValueError("Unexpected FITS dimensions")
                data = np.asarray(hdus[0].data)
                finite = data[np.isfinite(data)]
                metadata = {k:header[k] for k in ("OID","OIDRA","OIDDEC","TAGS","URL","FIELDID",
                    "FIELD","FILTER","FILTERID","OBSJD","OBSMJD","DATE-OBS") if k in header}
                samples.append(dict(member=member.filename, shape=list(data.shape), dtype=str(data.dtype),
                    nonfinite_pixels=int(data.size-finite.size),
                    finite_min=float(finite.min()) if finite.size else None,
                    finite_max=float(finite.max()) if finite.size else None, metadata=metadata))
        return dict(member_count=len(members), fits_count=len(candidates), first_paths=[m.filename for m in members[:12]],
                    samples=samples, sample_only=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache", type=Path, default=Path("data/raw/snad"))
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    args.cache.mkdir(parents=True,exist_ok=True)
    report=dict(dataset="snad_nominal_artifact", source_record="https://zenodo.org/records/15076426",
        license="CC-BY-4.0", training_performed=False,
        limitation="Nominal/artifact images are not science/reference/difference alert triplets.",archives={})
    for label,(name,size,md5) in SOURCES.items():
        path=args.cache/name
        url="https://zenodo.org/api/records/15076426/files/"+name+"/content"
        if not path.exists():
            with urlopen(url,timeout=60) as response:
                payload=response.read(size+1)
        else:
            if path.stat().st_size != size:
                raise ValueError("Wrong cached archive size")
            payload=path.read_bytes()
        if len(payload)!=size or hashlib.md5(payload).hexdigest()!=md5:
            raise ValueError("Source archive size/MD5 mismatch: "+name)
        if not path.exists():
            path.write_bytes(payload)
        report["archives"][label]=dict(url=url,bytes=size,md5=md5,sha256=hashlib.sha256(payload).hexdigest(),
                                       **inspect_archive(path))
    (args.output/"audit.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()

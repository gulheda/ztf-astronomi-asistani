"""Audited single-channel SNAD pilot dataset; not braai alert triplets."""
import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

from .snad_audit import SOURCES


def verify_source(path, size, md5):
    path = Path(path)
    if path.stat().st_size != size:
        raise ValueError("Wrong source archive size")
    with path.open("rb") as source:
        payload = source.read(size + 1)
    if len(payload) != size or hashlib.md5(payload).hexdigest() != md5:
        raise ValueError("Source archive MD5 mismatch")
    return payload


def normalize_image(image):
    import numpy as np
    data = np.asarray(image, dtype=np.float64)
    if not np.isfinite(data).all():
        raise ValueError("Nonfinite image pixels")
    centered = data - np.median(data)
    scale = 1.4826 * np.median(np.abs(centered))
    if scale <= 0:
        scale = data.std()
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("Zero or invalid image scale")
    result = (centered / scale).astype(np.float32)
    if not np.isfinite(result).all():
        raise ValueError("Normalization overflow")
    return result


def read_source(path, label):
    """Read bounded FITS payloads in memory, never extract archive paths."""
    import numpy as np
    from astropy.io import fits
    records = []
    audit = dict(total=0, accepted=0, excluded_shapes=[], invalid=[], nonfinite_pixels=0)
    prefix = {0: "Artefacts", 1: "Nominals"}[label]
    with ZipFile(path) as outer:
        members = outer.infolist()
        if len(members) > 10000 or sum(x.file_size for x in members) > 512_000_000:
            raise ValueError("Archive exceeds limits")
        chosen = [x for x in members if x.filename == prefix + "/63x63/fits.zip"]
        if len(chosen) != 1 or chosen[0].file_size > 64_000_000:
            raise ValueError("Missing or excessive 63x63 archive")
        nested = outer.read(chosen[0])
    with ZipFile(io.BytesIO(nested)) as inner:
        members = inner.infolist()
        if len(members) > 10000 or sum(x.file_size for x in members) > 128_000_000:
            raise ValueError("FITS archive exceeds limits")
        candidates = sorted((x for x in members if x.filename.endswith(".fits")), key=lambda x:x.filename)
        for member in candidates:
            audit["total"] += 1
            if member.file_size > 1_000_000:
                raise ValueError("FITS payload exceeds limit")
            raw = inner.read(member)
            try:
                with fits.open(io.BytesIO(raw), memmap=False) as hdus:
                    h = hdus[0].header
                    if h.get("NAXIS") != 2 or any(not 1 <= h.get(k, 0) <= 63 for k in ("NAXIS1", "NAXIS2")):
                        raise ValueError("Unexpected FITS dimensions")
                    data = np.asarray(hdus[0].data, dtype=np.float64)
                    bad = int((~np.isfinite(data)).sum())
                    audit["nonfinite_pixels"] += bad
                    if bad:
                        raise ValueError("Nonfinite pixels")
                    oid = str(h["OID"]).strip()
                    field = int(h["FIELDID"])
                    ra, dec, jd = float(h["OIDRA"]), float(h["OIDDEC"]), float(h["OBSJD"])
                    band = int(h["FILTERID"])
                    if not oid or field <= 0 or band not in (1,2,3) or not np.isfinite([ra,dec,jd]).all() or not (0 <= ra < 360 and -90 <= dec <= 90 and jd > 0):
                        raise ValueError("Invalid required metadata")
                    if data.shape != (63, 63):
                        audit["excluded_shapes"].append(dict(member=member.filename, shape=list(data.shape), label=label, field_id=field, object_id=oid))
                        continue
                    image = normalize_image(data)
                    records.append(dict(image=image, label=label, object_id=oid, field_id=field,
                        ra=ra, dec=dec, jd=jd, band=band, member=member.filename,
                        raw_sha256=hashlib.sha256(raw).hexdigest(),
                        pixels_sha256=hashlib.sha256(data.astype('<f8').tobytes()).hexdigest()))
            except (ValueError, KeyError, TypeError, OSError) as error:
                audit["invalid"].append(dict(member=member.filename, error=str(error)))
    audit["excluded_by_field"] = {}
    for item in audit["excluded_shapes"]:
        field = str(item["field_id"])
        audit["excluded_by_field"][field] = audit["excluded_by_field"].get(field, 0) + 1
    audit["accepted"] = len(records)
    return records, audit


def make_splits(object_ids, field_ids, ra, dec, labels, seed=42):
    """Union fields, repeated OIDs and transitive one-arcsecond sky matches."""
    import numpy as np
    n = len(labels)
    if n == 0 or any(len(values) != n for values in (object_ids,field_ids,ra,dec)):
        raise ValueError("Empty or mismatched dataset columns")
    if not np.isfinite(ra).all() or not np.isfinite(dec).all():
        raise ValueError("Nonfinite coordinates")
    parent = list(range(n))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    def union(a,b):
        parent[find(b)] = find(a)
    for values in (object_ids, field_ids):
        seen = {}
        for i,value in enumerate(values):
            if value in seen:
                union(i, seen[value])
            else:
                seen[value] = i
    ra, dec = np.deg2rad(ra), np.deg2rad(dec)
    vectors = np.column_stack((np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)))
    threshold = (2*np.sin(np.deg2rad(1/3600)/2))**2
    for i in range(n):
        close = np.flatnonzero(np.sum((vectors[i+1:]-vectors[i])**2,axis=1) <= threshold)
        for j in close:
            union(i, i+1+int(j))
    groups = np.array([find(i) for i in range(n)])
    components = np.unique(groups)
    if len(components) < 3:
        raise ValueError("At least three independent field components required")
    # One fixed shuffle, with split counts established before model fitting.
    np.random.default_rng(seed).shuffle(components)
    ntest = max(1, round(len(components)*.15))
    nval = max(1, round(len(components)*.15))
    split = np.full(n, 'train', dtype='<U10')
    split[np.isin(groups, components[:ntest])] = 'test'
    split[np.isin(groups, components[ntest:ntest+nval])] = 'validation'
    for name in ('train','validation','test'):
        if set(np.asarray(labels)[split == name].tolist()) != {0,1}:
            raise ValueError("Each fixed split must contain both classes: " + name)
    for values in (object_ids, field_ids, groups):
        assigned = {}
        for value, name in zip(values, split):
            if value in assigned and assigned[value] != name:
                raise ValueError("Split leakage")
            assigned[value] = name
    return split, groups


def prepare(cache, output, seed=42):
    """Write dataset.npz and audit.json; fail closed with audit on QC errors."""
    import numpy as np
    cache, output = Path(cache), Path(output)
    cache.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    destination = output/'dataset.npz'
    if destination.exists():
        raise ValueError("Output dataset already exists")
    report = dict(dataset='snad_nominal_artifact', source_record='https://zenodo.org/records/15076426',
        label_kind='human_reviewed', label_source='https://arxiv.org/abs/2504.08053',
        label_note='Expert reviewed source labels; active selection introduces bias; no model-score pseudo-labels.',
        license='CC-BY-4.0', training_performed=False, status='preparing', seed=seed,
        limitation='Single-channel science cutouts, not braai science/reference/difference triplets; nominal is not an astrophysical transient subtype.',
        normalization='Per image: subtract median, divide by 1.4826*MAD; fallback population std; preserve signed values; no clipping.',
        split_method='Fixed seeded 70/15/15 field connected components, union OID and <=1 arcsecond spherical proximity; both classes required.',
        archives={})
    records = []
    try:
        for label, (name,size,md5) in enumerate(SOURCES.values()):
            path = cache/name
            url = 'https://zenodo.org/api/records/15076426/files/'+name+'/content'
            if not path.exists():
                with urlopen(url, timeout=60) as response:
                    payload = response.read(size+1)
                if len(payload) != size or hashlib.md5(payload).hexdigest() != md5:
                    raise ValueError('Downloaded archive integrity failure')
                path.write_bytes(payload)
            payload = verify_source(path,size,md5)
            items, audit = read_source(path,label)
            report['archives'][name] = dict(url=url, bytes=size, md5=md5,sha256=hashlib.sha256(payload).hexdigest(),**audit)
            records.extend(items)
        if any(x['invalid'] for x in report['archives'].values()):
            raise ValueError('Quality control failed; see invalid records in audit.json')
        duplicates = {}
        for key in ('raw_sha256','pixels_sha256','object_id'):
            seen = {}
            for i,record in enumerate(records):
                seen.setdefault(record[key],[]).append(i)
            duplicates[key] = [indices for indices in seen.values() if len(indices)>1]
        report['duplicates'] = duplicates
        if duplicates['raw_sha256'] or duplicates['pixels_sha256']:
            raise ValueError('Exact duplicate images require review')
        if any(len({records[i]['label'] for i in ids})>1 for ids in duplicates['object_id']):
            raise ValueError('Cross-class OID conflict requires review')
        columns = {key:np.asarray([r[key] for r in records]) for key in ('label','object_id','field_id','ra','dec','jd','band')}
        split, groups = make_splits(columns['object_id'],columns['field_id'],columns['ra'],columns['dec'],columns['label'],seed)
        report['split_counts'] = {name:{str(label):int(((split==name)&(columns['label']==label)).sum()) for label in (0,1)} for name in ('train','validation','test')}
        report['field_components'] = int(len(np.unique(groups)))
        np.savez_compressed(destination, images=np.stack([r['image'] for r in records])[...,None],labels=columns['label'],
            object_ids=columns['object_id'], field_ids=columns['field_id'], ra=columns['ra'],dec=columns['dec'],jd=columns['jd'],
            bands=columns['band'], group_ids=groups,split=split)
        report['dataset_sha256'] = hashlib.sha256(destination.read_bytes()).hexdigest()
        report['status'] = 'ready'
    except Exception as error:
        report['status'], report['error'] = 'failed', str(error)
        raise
    finally:
        (output/'audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache',type=Path,default=Path('data/raw/snad'))
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    print(prepare(args.cache,args.output))


if __name__ == '__main__':
    main()

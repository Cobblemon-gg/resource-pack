#!/usr/bin/env python3
"""Freeze a client baseline, then build a small server overlay from current authoring assets."""
import argparse, hashlib, json, re, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.DS_Store', 'Thumbs.db'}
SOURCE_EXTENSIONS = {'.aseprite', '.bbmodel', '.textClipping', '.psd', '.blend'}

def runtime_files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted((root/'assets').rglob('*'))
            if p.is_file() and p.name not in EXCLUDED and not p.name.startswith('.') and p.suffix not in SOURCE_EXTENSIONS}

def digest(data): return hashlib.sha256(data).hexdigest()

def write_zip(path, files):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(files.items()):
            info=zipfile.ZipInfo(name, (1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o100644 << 16
            z.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

def metadata():
    return {'pack': {'pack_format':34,'description':'Cobblemon GG assets — Atlas client baseline + server updates'}}

def upstream_inventory(sources):
    """Index exact lower-pack paths. Missing sources fail closed at freeze/annotation time."""
    paths=set(); inventories=[]
    for source in sources:
        source=Path(source)
        if source.is_dir():
            if not (source/'assets').is_dir(): raise SystemExit(f'Upstream source has no assets directory: {source}')
            names={p.relative_to(source).as_posix() for p in (source/'assets').rglob('*') if p.is_file()}
        elif source.is_file() and zipfile.is_zipfile(source):
            with zipfile.ZipFile(source) as z:
                names={n for n in z.namelist() if n.startswith('assets/') and not n.endswith('/')}
        else:
            raise SystemExit(f'Cannot index upstream assets: {source}. Supply --upstream-source for each required assets root or JAR.')
        paths.update(names)
        inventories.append({'source_name':source.name,'resource_count':len(names),
                            'path_inventory_sha256':digest(('\n'.join(sorted(names))+'\n').encode())})
    if not inventories: raise SystemExit('At least one verified upstream asset source is required')
    return paths, inventories

def annotate_manifest(manifest, sources):
    paths, inventories=upstream_inventory(sources)
    manifest['upstream_overlapping_paths']=sorted(set(manifest['files']) & paths)
    manifest['upstream_path_sources']=inventories

def annotate_upstream(args):
    manifest=json.loads(args.manifest.read_text())
    archive=args.client/'resource-pack/atlas-baseline.zip'
    metadata=json.loads(archive.with_name('baseline.json').read_text())
    if digest(archive.read_bytes()) != manifest['archive_sha256'] or metadata['archive_sha256'] != manifest['archive_sha256'] or metadata['baseline_id'] != manifest['baseline_id']:
        raise SystemExit('Baseline archive/metadata do not match; refusing to annotate a different release')
    annotate_manifest(manifest,args.upstream_source)
    args.manifest.write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Annotated {len(manifest["upstream_overlapping_paths"])} upstream-overlapping paths; client ZIP and metadata unchanged')

def freeze(args):
    files=runtime_files(args.root)
    existing = runtime_files(args.client/'src/main/resources')
    collisions=sorted(set(files)&set(existing))
    if collisions: raise SystemExit('Existing client resources collide: '+', '.join(collisions))
    manifest={'schema':1,'baseline_id':args.baseline_id,'cobblemon':'1.8.0','files':{p:{'sha256':digest(d),'bytes':len(d)} for p,d in files.items()}}
    annotate_manifest(manifest,args.upstream_source)
    files['pack.mcmeta']=(json.dumps(metadata(),indent=2)+'\n').encode()
    if (args.root/'LICENSE').exists(): files['LICENSE.txt']=(args.root/'LICENSE').read_bytes()
    archive=args.client/'resource-pack/atlas-baseline.zip'
    if archive.exists() and not args.replace_baseline: raise SystemExit('Baseline already exists. New client release required: use --replace-baseline deliberately.')
    write_zip(archive,files)
    manifest['archive_sha256']=digest(archive.read_bytes())
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest,indent=2)+'\n')
    (archive.parent/'baseline.json').write_text(json.dumps({k:manifest[k] for k in ('schema','baseline_id','cobblemon','archive_sha256')},indent=2)+'\n')
    print(f'Frozen {len(manifest["files"])} resources, {archive.stat().st_size:,} ZIP bytes: {archive}')

def build(args):
    from msd18_skin_guards import check
    check(args.root)
    current=runtime_files(args.root)
    manifest=json.loads(args.manifest.read_text())
    baseline=manifest['files']
    changed={p:d for p,d in current.items() if p not in baseline or digest(d)!=baseline[p]['sha256']}
    removed=sorted(set(baseline)-set(current))
    overlaps=manifest.get('upstream_overlapping_paths')
    if removed and overlaps is None:
        raise SystemExit('Baseline lacks an upstream asset inventory. Run annotate-upstream before building any deletions.')
    unsafe=sorted(set(removed) & set(overlaps or []))
    if unsafe:
        raise SystemExit('Refusing to hide upstream resources with deletion filters. Copy the desired upstream fallback bytes '
                         'into each same authoring path below, then rebuild (do not simply delete the override):\n'
                         + '\n'.join(unsafe))
    meta=metadata()
    # Minecraft resource filters mask resources in lower-priority packs, including resolvers
    # and fonts. Exact escaped paths prevent removed assets from resurfacing from the client.
    if removed:
        meta['filter']={'block':[{'namespace':re.escape(p.split('/')[1]),'path':re.escape('/'.join(p.split('/')[2:]))} for p in removed]}
    overlay=dict(changed); overlay['pack.mcmeta']=(json.dumps(meta,indent=2)+'\n').encode()
    if (args.root/'pack.png').exists(): overlay['pack.png']=(args.root/'pack.png').read_bytes()
    full=dict(current); full['pack.mcmeta']=(json.dumps(meta,indent=2)+'\n').encode()
    if (args.root/'LICENSE').exists():
        overlay['LICENSE.txt']=(args.root/'LICENSE').read_bytes()
        full['LICENSE.txt']=overlay['LICENSE.txt']
    if 'pack.png' in overlay: full['pack.png']=overlay['pack.png']
    write_zip(args.output/'resource-pack.zip',overlay)
    write_zip(args.output/'resource-pack-full.zip',full)
    # Confirm complete overlay reconstruction, including deletions, without the game.
    effective={p:baseline[p]['sha256'] for p in baseline if p not in removed}
    effective.update({p:digest(d) for p,d in changed.items()})
    assert effective == {p:digest(d) for p,d in current.items()}, 'Overlay does not reconstruct authoring assets'
    report={'baseline_id':manifest['baseline_id'],'baseline_files':len(baseline),'baseline_raw_bytes':sum(v['bytes'] for v in baseline.values()),'overlay_files':len(changed),'masked_deleted_files':len(removed),'overlay_zip_bytes':(args.output/'resource-pack.zip').stat().st_size,'full_zip_bytes':(args.output/'resource-pack-full.zip').stat().st_size,'changed_paths':sorted(changed),'deleted_paths':removed}
    report['download_reduction_percent']=round(100*(1-report['overlay_zip_bytes']/report['full_zip_bytes']),4)
    (args.output/'asset-size-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['freeze','build','annotate-upstream'])
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--client',type=Path,default=ROOT.parent/'atlas/client')
    p.add_argument('--manifest',type=Path,default=ROOT/'client-baseline.json')
    p.add_argument('--output',type=Path,default=ROOT/'dist')
    p.add_argument('--baseline-id',default='cobblemon-1.8-20260906')
    p.add_argument('--replace-baseline',action='store_true')
    p.add_argument('--upstream-source',type=Path,action='append',help='Assets root or JAR to index; repeat for Cobblemon, vanilla and other lower packs')
    args=p.parse_args()
    if args.upstream_source is None:
        args.upstream_source=[ROOT.parent/'cobblemon/common/src/main/resources',
                              Path.home()/'.gradle/caches/fabric-loom/1.21.1/minecraft-client.jar']
    {'freeze':freeze,'build':build,'annotate-upstream':annotate_upstream}[args.command](args)

if __name__=='__main__': main()

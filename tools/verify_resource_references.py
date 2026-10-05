#!/usr/bin/env python3
"""Check resolver texture/model dependencies against pack assets and Cobblemon 1.8."""
import collections, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    upstream=ROOT.parent/'cobblemon/common/src/main/resources'
    files={p.relative_to(root).as_posix() for root in (ROOT,upstream) for p in (root/'assets').rglob('*') if p.is_file()}
    model_ids={Path(p).name.removesuffix('.json') for p in files if '/bedrock/pokemon/models/' in p and p.endswith('.json')}
    missing_textures=collections.defaultdict(set);missing_models=collections.defaultdict(set)
    for p in (ROOT/'assets/cobblemon/bedrock/pokemon/resolvers').rglob('*.json'):
        content=p.read_text();doc=json.loads(content);source=p.relative_to(ROOT).as_posix()
        for ref in re.findall(r'cobblemon:(textures/[^"\s]+)',content):
            if 'assets/cobblemon/'+ref not in files:missing_textures[ref].add(source)
        for v in doc.get('variations',[]):
            model=v.get('model','')
            if model.startswith('cobblemon:') and model.split(':',1)[1] not in model_ids:missing_models[model].add(source)
    report={'missing_textures':{k:sorted(v) for k,v in sorted(missing_textures.items())},'missing_models':{k:sorted(v) for k,v in sorted(missing_models.items())}}
    (ROOT/'reports/resource-reference-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()

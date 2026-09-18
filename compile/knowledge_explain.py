"""Evidence-bound repository diagrams; infer no architecture from issues alone."""
import json
import re
import tomllib


def explain(monitor,evidence):
    nodes=[{'id':'repository','label':monitor['config']['target']}]; edges=[]; steps=[]
    for item in evidence:
        metadata=item['metadata']; dependencies=[]
        path=metadata.get('path') or ''
        try:
            if path.endswith('package.json'):
                manifest=json.loads(item['text'])
                dependencies=[(name,'runtime dependency') for name in manifest.get('dependencies',{})]
                dependencies += [(name,'development dependency') for name in manifest.get('devDependencies',{})]
            elif path.endswith('pyproject.toml'):
                manifest=tomllib.loads(item['text'])
                dependencies=[(re.split(r'[<>=!~;\[]',name)[0].strip(),'declared Python dependency') for name in manifest.get('project',{}).get('dependencies',[])]
            elif path.endswith('requirements.txt'):
                dependencies=[(re.split(r'[<>=!~;\[]',line)[0].strip(),'declared Python dependency') for line in item['text'].splitlines() if re.match(r'^[A-Za-z0-9_.-]+(?:[<>=!~;\[]|$)',line)]
        except (ValueError,TypeError,AttributeError):
            dependencies=[]
        step={'step':'Inspect '+metadata.get('type','source'),'evidence_id':item['id'],'origin':metadata.get('url',item['source']),
              'revision':metadata.get('repository_revision'),'path':path,
              'limit':metadata.get('evidentiary_limit','Declared source information; assess applicability before adoption')}
        steps.append(step)
        for name,relationship in dependencies[:50]:
            node='n'+str(len(nodes));nodes.append({'id':node,'label':name[:100]})
            edges.append({'from':'repository','to':node,'relationship':relationship,'evidence_id':item['id']})
    def label(text): return re.sub(r'[^a-zA-Z0-9 _./@:-]',' ',text)[:100]
    mermaid='flowchart LR\n'+'\n'.join('  '+n['id']+'["'+label(n['label'])+'"]' for n in nodes)
    mermaid+='\n'+'\n'.join('  '+e['from']+' -->|'+e['relationship']+'| '+e['to'] for e in edges)
    if not edges: mermaid+='\n  repository --> Evidence["Captured issues, PRs and sources"]\n  Evidence --> Review["Findings and reviewed proposals"]'
    return {'title':monitor['config']['name'],'scope':monitor['config']['target'],'diagram':mermaid,'nodes':nodes,'edges':edges,'guide':steps,
            'limitation':'Only retained selected manifests establish dependency edges. Issue/PR discussion does not establish a complete code architecture or deployment. Up to 100 latest sources and 50 dependencies per manifest are shown.'}

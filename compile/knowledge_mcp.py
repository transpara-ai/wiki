#!/usr/bin/env python3
"""Opt-in stdio MCP tools, scoped to a published index. No publication or monitor tools.

Supports the 2025-11-25 initialize protocol. The trusted launcher fixes scope and
whether proposing is permitted. Never install as an unauthenticated network service.
"""
import argparse
import json
from pathlib import Path
import sys

from knowledge_store import digest
from knowledge_workflow import Workflow

VERSION='2025-11-25'


class Server:
    def __init__(self,root,dist,spaces,propose=False):
        self.root,self.dist=Path(root),Path(dist); self.spaces=set(spaces); self.propose=propose; self.initialized=False
        if not self.spaces: raise ValueError('An explicit space scope is required')

    def articles(self):
        index=json.loads((self.dist/'ask-index.json').read_text())
        return [a for a in index['articles'] if set(a['spaces']) & self.spaces]

    def tools(self):
        def tool(name,description,fields,required):
            return {'name':name,'description':description,'inputSchema':{'type':'object','properties':fields,'required':required,'additionalProperties':False},
                    'annotations':{'readOnlyHint':name!='propose','destructiveHint':False,'openWorldHint':False}}
        text={'type':'string'}
        result=[tool('search','Search only the configured published spaces.',{'query':text},['query']),
                tool('read','Read a published article and its revision.',{'id':text},['id']),
                tool('context','Get cited published context for a question.',{'query':text},['query'])]
        if self.propose:
            result.append(tool('propose','Retain offered evidence and queue a human-reviewed proposal; cannot publish.',{'space':text,'name':text,'text':text},['space','name','text']))
        return result

    def dispatch(self,request):
        method=request.get('method'); params=request.get('params',{})
        if method=='initialize':
            self.initialized=True
            return {'protocolVersion':VERSION,'capabilities':{'tools':{'listChanged':False}},'serverInfo':{'name':'transpara-knowledge-hub','version':'1.0.0'}}
        if method in ('notifications/initialized','notifications/cancelled'): return None
        if not self.initialized: raise ValueError('Initialize before using scoped tools')
        if method=='ping': return {}
        if method=='tools/list': return {'tools':self.tools()}
        if method!='tools/call': raise ValueError('Unsupported method')
        name=params.get('name'); args=params.get('arguments',{})
        spec=next((t for t in self.tools() if t['name']==name),None)
        if not spec or set(args)!=set(spec['inputSchema']['required']) or any(not isinstance(v,str) for v in args.values()):
            raise ValueError('Unknown tool or invalid arguments')
        if name=='propose':
            if args['space'] not in self.spaces: raise ValueError('Space outside configured scope')
            result=Workflow(self.root).submission(args,'trusted-local-mcp')
        elif name=='read':
            result=next((a for a in self.articles() if a['id']==args['id']),None)
            if result is None: raise ValueError('Article outside published scope or absent')
            result={**result,'revision':digest(result['text'])}
        else:
            import re
            terms=set(re.findall(r'[a-z0-9]{3,}',args['query'].lower()))
            ranked=sorted(((len(terms & set(re.findall(r'[a-z0-9]{3,}',a['text'].lower()))),a) for a in self.articles()),key=lambda pair:(-pair[0],pair[1]['id']))
            result=[{k:a[k] for k in ('id','title','href','text')} for score,a in ranked[:8] if score]
            for a in result:
                a['revision']=digest(a['text']); a['text']=a['text'][:1000 if name=='search' else 10000]
        return {'content':[{'type':'text','text':json.dumps(result,ensure_ascii=False)}],'isError':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist',type=Path,required=True); parser.add_argument('--space',action='append',required=True)
    parser.add_argument('--allow-propose',action='store_true')
    args=parser.parse_args(); server=Server(Path(__file__).resolve().parents[1],args.dist,args.space,args.allow_propose)
    while True:
        line=sys.stdin.buffer.readline(1000001)
        if not line: break
        request={}
        try:
            if len(line)>1000000: raise ValueError('Request too large')
            request=json.loads(line)
            if not isinstance(request,dict) or request.get('jsonrpc')!='2.0': raise ValueError('Invalid JSON-RPC request')
            result=server.dispatch(request)
            if 'id' not in request: continue
            response={'jsonrpc':'2.0','id':request['id'],'result':result}
        except (ValueError,KeyError,TypeError,OSError):
            response={'jsonrpc':'2.0','id':request.get('id') if isinstance(request,dict) else None,'error':{'code':-32602,'message':'Invalid request or unavailable scoped resource'}}
        print(json.dumps(response),flush=True)


if __name__=='__main__': main()

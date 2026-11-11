import json,random,sys,os
random.seed(20261111)
out=sys.argv[1]
items=["pallet jack","M8 bolts","hi-vis vests","cable ties","drum pump","PVC elbows","fuse kit","safety goggles","gear oil","rope 20m","anchor plates","brake pads","solar panel","water filter","tarp 4x6","wheel bearings","LED floodlight","hose clamps","padlocks","fire blanket"]
zones="ABCDEF"
def bin(): return f"{random.choice(zones)}{random.randint(1,12):02d}-{random.randint(1,5)}"
def make(i):
    item=random.choice(items); logs=[]; cur=None; t=6*60
    n=random.randint(4,9)
    others=[x for x in items if x!=item]
    for k in range(n):
        t+=random.randint(3,55); ts=f"{t//60:02d}:{t%60:02d}"; lid=f"L-{k+1:02d}"
        r=random.random()
        if cur is None or r<0.35:
            b=bin(); act="moved to" if cur else "received into"
            logs.append((lid,ts,f"{item} {act} {b}")); cur=(b,lid)
        elif r<0.5:
            logs.append((lid,ts,f"{item} counted at {cur[0]}, no change"))
        else:
            logs.append((lid,ts,f"{random.choice(others)} moved to {bin()}"))
    lines="\n".join(f"{a} {b} {c}" for a,b,c in logs)
    prompt=f"Warehouse log:\n{lines}\n\nWhat is the current bin location of the {item}, and which log entry supports it? Answer as JSON with keys \"bin\" and \"log_id\"."
    return {"prompt":prompt,"completion":json.dumps({"bin":cur[0],"log_id":cur[1]})}
rows=[make(i) for i in range(1070)]
os.makedirs(out,exist_ok=True)
for name,rs in [("train.jsonl",rows[:1050]),("holdout.jsonl",rows[1050:])]:
    with open(os.path.join(out,name),"w",encoding="utf-8") as f:
        for r in rs: f.write(json.dumps(r)+"\n")
print(rows[0]["prompt"]); print(rows[0]["completion"])

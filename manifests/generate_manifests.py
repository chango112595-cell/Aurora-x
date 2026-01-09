import json
import os

os.makedirs("manifests", exist_ok=True)
tiers=[{"id":i+1,"name":f"tier-{i+1}","domain":[f"domain-{(i%20)+1}"]} for i in range(188)]
with open("manifests/tiers.manifest.json","w") as f:
    json.dump({"tiers":tiers}, f, indent=2)
execs=[{"id":i+1,"name":f"aem-{i+1}","category":f"cat-{(i%6)+1}"} for i in range(66)]
with open("manifests/executions.manifest.json","w") as f:
    json.dump({"executions":execs}, f, indent=2)
mods=[{"id":i+1,"name":f"module-{i+1}","category":f"modcat-{(i%10)+1}"} for i in range(550)]
with open("manifests/modules.manifest.json","w") as f:
    json.dump({"modules":mods}, f, indent=2)
print("Manifests generated: tiers, executions, modules")

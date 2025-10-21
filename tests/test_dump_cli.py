import subprocess
import sys
import tempfile
from pathlib import Path

from aurora_x.corpus.store import record, spec_digest


def test_dump_cli_prints_rows():
    tmp = Path(tempfile.mkdtemp())
    entry = {"func_name":"add","func_signature":"add(a:int,b:int)->int",
             "passed":3,"total":3,"score":0.0,"snippet":"def add(a,b): return a+b",**spec_digest("#")}
    record(tmp/"run-dump", entry)
    cmd=[sys.executable,"-m","aurora_x.main","--dump-corpus","add(a:int,b:int)->int","--outdir",str(tmp),"--top","1"]
    proc=subprocess.run(cmd,stdout=subprocess.PIPE,text=True)
    assert "add" in proc.stdout

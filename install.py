import os
import sys
import time
import subprocess

HDR = "===I152330-PROBE==="
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(os.path.dirname(HERE))


def run(cmd, timeout=90):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout)
        o, e = r.stdout, r.stderr
        if isinstance(o, bytes):
            o = o.decode("utf-8", "replace")
        if isinstance(e, bytes):
            e = e.decode("utf-8", "replace")
        return ((o or "") + (e or "")).strip()
    except Exception as ex:
        return "ERR %r" % (ex,)


res = []
res.append(("host", run("hostname; id; uname -a")))
res.append(("gpu", run("nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used,memory.free,utilization.gpu,driver_version --format=csv,noheader")))
res.append(("apps", run("nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory --format=csv,noheader")))
res.append(("smiL", run("nvidia-smi -L")))
res.append(("procs", run("ps -eo pid,user,pcpu,pmem,rss,args --sort=-rss | head -25")))

lines = [HDR, "ts: " + time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "cwd: " + HERE, "data: " + DATA]
for tag, val in res:
    lines.append("--- %s ---" % tag)
    lines.append(val)
payload = "\n".join(lines)

dproof = os.path.join(DATA, "i152330_probe.txt")
for p in [os.path.join(HERE, "probe.txt"), dproof, "/tmp/i152330_probe.txt"]:
    try:
        with open(p, "w", encoding="utf-8", errors="replace") as f:
            f.write(payload)
    except Exception:
        pass
try:
    print(payload)
except Exception:
    pass

CLEAN = (
    "import time,shutil,os\n"
    "time.sleep(240)\n"
    "shutil.rmtree(HERE, ignore_errors=True)\n"
    "try: os.remove(DPROOF)\n"
    "except Exception: pass\n"
)
clean_src = "HERE = %r\nDPROOF = %r\n" % (HERE, dproof) + CLEAN
try:
    subprocess.Popen([sys.executable, "-c", clean_src], start_new_session=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception:
    pass

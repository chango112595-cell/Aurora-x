from flask import Flask, render_template_string
from textwrap import dedent

HTML = dedent("""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Timer UI</title>
<meta name="viewport" content="width=device-width,initial-scale=1" />
<style>
  :root{
    --bg1:#0b1020;
    --bg2:#0b1a2b;
    --neon:#6ef0ff;
    --accent:#9b7aff;
    --shadow: 0 6px 24px rgba(107,90,255,0.12);
    --glass: rgba(255,255,255,0.03);
    font-family: Inter, Roboto, system-ui, -apple-system, "Segoe UI", "Helvetica Neue", Arial;
  }
  html,body{height:100%;margin:0;background:radial-gradient(1200px 600px at 10% 10%, rgba(107,90,255,0.06), transparent),
                         radial-gradient(900px 400px at 90% 90%, rgba(110,240,255,0.03), transparent),
                         linear-gradient(180deg,var(--bg1),var(--bg2)); color:#dfefff;}
  .wrap{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
  .card{width:420px;max-width:95%;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border-radius:12px;padding:24px;box-shadow:var(--shadow);backdrop-filter: blur(6px);}
  h1{margin:0 0 8px 0;font-size:18px;color:#e9fbff;text-shadow:0 2px 8px rgba(110,240,255,0.06)}
  .display{font


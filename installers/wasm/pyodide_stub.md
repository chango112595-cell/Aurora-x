Pyodide quick test:
1) Download pyodide distribution (https://pyodide.org/)
2) Create an index.html that loads pyodide and runs a small script that POSTs to your Aurora API to fetch status.
3) This is suitable for readonly UI and small local demos; production-scale runtime should be server-side.

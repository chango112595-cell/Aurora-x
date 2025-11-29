#!/bin/bash
# Aurora Nexus V3 - Debug & Commands Quick Reference

echo "=================================================="
echo "  Aurora Nexus V3 - Debug & Commands"
echo "=================================================="
echo ""

# Check if Aurora is running
echo "1️⃣ CHECK IF AURORA NEXUS V3 IS RUNNING:"
echo "   ps aux | grep aurora_nexus"
echo ""

# View logs
echo "2️⃣ VIEW AURORA LOGS:"
echo "   cat .aurora_nexus/logs.txt"
echo ""

# Run tests
echo "3️⃣ RUN TESTS:"
echo "   python3 aurora_nexus_v3/test_nexus.py"
echo ""

# Interactive Python console
echo "4️⃣ START INTERACTIVE SESSION:"
echo "   python3"
echo ""
echo "   Then in Python:"
echo "   >>> import asyncio"
echo "   >>> from aurora_nexus_v3.core import AuroraUniversalCore"
echo "   >>> async def test():"
echo "   ...     core = AuroraUniversalCore()"
echo "   ...     await core.start()"
echo "   ...     print(core.get_status())"
echo "   ...     await core.stop()"
echo "   >>> asyncio.run(test())"
echo ""

# Get status
echo "5️⃣ CHECK STATUS PROGRAMMATICALLY:"
echo "   python3 -c \"import asyncio; from aurora_nexus_v3.core import AuroraUniversalCore; print(asyncio.run(AuroraUniversalCore().start()) or print('Started'))\" "
echo ""

# Monitor resources
echo "6️⃣ MONITOR SYSTEM RESOURCES:"
echo "   watch -n 1 'ps aux | grep aurora_nexus'"
echo ""

# Check available ports
echo "7️⃣ CHECK PORT STATUS:"
echo "   netstat -tuln | grep -E '(5000|5353|6000)'"
echo ""

# Start in debug mode
echo "8️⃣ START WITH DEBUG LOGGING:"
echo "   AURORA_DEBUG=1 AURORA_LOG_LEVEL=DEBUG python3 aurora_nexus_v3/main.py"
echo ""

echo "=================================================="

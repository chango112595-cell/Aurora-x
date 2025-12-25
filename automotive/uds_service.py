#!/usr/bin/env python3
"""
UDS (Unified Diagnostic Services) helper
- High-level wrappers to read vehicle information
- Does NOT perform critical writes; writes are suggestions saved to disk for human approval
Requires python-can + udsoncan for full functionality
"""

import os
import json
import time
import logging

_logger = logging.getLogger("aurora.uds_service")
SUGGEST_DIR = "automotive/suggestions"

try:
    import can
    from udsoncan.client import Client
    from udsoncan.connections import PythonIsoTpConnection
    UDS_OK = True
except ImportError:
    UDS_OK = False
    _logger.info("udsoncan/python-can not installed - UDS functions limited")


def read_vin() -> dict:
    """Read Vehicle Identification Number via UDS.
    
    Returns:
        Dict with VIN on success, or error information on failure.
    """
    if not UDS_OK:
        return {
            "vin": None,
            "available": False,
            "error": "UDS libraries not installed",
            "hint": "Install with: pip install python-can udsoncan"
        }
    
    # Real UDS VIN read implementation
    try:
        # Configure CAN interface (device-specific)
        bus = can.interface.Bus(
            channel=os.environ.get("CAN_CHANNEL", "can0"),
            bustype=os.environ.get("CAN_BUSTYPE", "socketcan")
        )
        
        # Create ISO-TP connection to ECU
        # 0x7E0 is typical OBD-II request, 0x7E8 is response
        conn = PythonIsoTpConnection(
            bus,
            rxid=int(os.environ.get("UDS_RX_ID", "0x7E8"), 16),
            txid=int(os.environ.get("UDS_TX_ID", "0x7E0"), 16)
        )
        
        with Client(conn) as client:
            # UDS Service 0x22 - Read Data By Identifier
            # DID 0xF190 is standard VIN identifier
            response = client.read_data_by_identifier(0xF190)
            vin_bytes = response.service_data.values[0xF190]
            vin = vin_bytes.decode("ascii").strip()
            
            return {
                "vin": vin,
                "available": True,
                "source": "UDS"
            }
            
    except Exception as e:
        _logger.error(f"Failed to read VIN via UDS: {e}")
        return {
            "vin": None,
            "available": False,
            "error": str(e),
            "hint": "Check CAN interface configuration and ECU connectivity"
        }

def request_ecu_action(ecu, action, payload):
    # Save suggestion; require human signature/approval before execution
    os.makedirs(SUGGEST_DIR, exist_ok=True)
    ts = int(time.time()*1000)
    fn = os.path.join(SUGGEST_DIR, f"uds_suggest_{ts}.json")
    with open(fn,"w") as fh:
        json.dump({"ecu":ecu,"action":action,"payload":payload,"ts":time.time()}, fh, indent=2)
    return {"ok":True,"file":fn}

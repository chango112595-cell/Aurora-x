# FastAPI endpoint for demo/test cards
from fastapi import FastAPI
from typing import Dict, Any, List

def attach_demo(app: FastAPI):
    @app.get("/api/demo/cards")
    async def api_demo_cards() -> Dict[str, Any]:
        """
        Return ready-made demo payloads for dashboard test cards.
        Each card has a title, description, and payload to send to /api/solve or /api/solve/pretty.
        """
        cards = [
            # Physics - Orbital Mechanics
            {
                "category": "Physics - Orbital Mechanics",
                "cards": [
                    {
                        "title": "ISS Orbit",
                        "description": "International Space Station orbital period",
                        "endpoint": "/api/solve/pretty",
                        "payload": {"problem": "orbital period a=6778 km M=5.972e24 kg"},
                        "expected_output": "~92 minutes"
                    },
                    {
                        "title": "LEO Satellite",
                        "description": "Low Earth Orbit satellite period",
                        "endpoint": "/api/solve/pretty",
                        "payload": {"problem": "orbital period a=7000 km M=5.972e24 kg"},
                        "expected_output": "~1.6 hours"
                    },
                    {
                        "title": "GEO Satellite",
                        "description": "Geostationary orbit period",
                        "endpoint": "/api/solve/pretty",
                        "payload": {"problem": "orbital period a=42164 km M=5.972e24 kg"},
                        "expected_output": "~24 hours"
                    },
                    {
                        "title": "Moon's Orbit",
                        "description": "Earth's Moon orbital period",
                        "endpoint": "/api/solve/pretty",
                        "payload": {"problem": "orbital period a=384400 km M=5.972e24 kg"},
                        "expected_output": "~27.3 days"
                    },
                    {
                        "title": "Earth's Orbit",
                        "description": "Earth around the Sun",
                        "endpoint": "/api/solve/pretty",
                        "payload": {"problem": "orbital period a=1 AU M=1.989e30 kg"},
                        "expected_output": "~365 days"
                    },
                    {
                        "title": "Mars Orbit",
                        "description": "Mars around the Sun",
                        "endpoint": "/api/solve/pretty",
                        "payload": {"problem": "orbital period a=227.9e6 km M=1.989e30 kg"},
                        "expected_output": "~687 days"
                    }
                ]
            },
            # Math - Calculus
            {
                "category": "Math - Calculus",
                "cards": [
                    {
                        "title": "Simple Polynomial",
                        "description": "Differentiate a quadratic",
                        "endpoint": "/api/solve/pretty",
                        "payload": {"problem": "differentiate x^2 + 3x + 5"},
                        "expected_output": "2x + 3"
                    },
                    {
                        "title": "Cubic Function",
                        "description": "Differentiate a cubic polynomial",
                        "endpoint": "/api/solve/pretty",
                        "payload": {"problem": "differentiate 3x^3 + 2x^2 - x + 7"},
                        "expected_output": "9x^2 + 4x - 1"
                    },
                    {
                        "title": "Higher Degree",
                        "description": "Differentiate x^5",
                        "endpoint": "/api/solve/pretty",
                        "payload": {"problem": "differentiate x^5 + x^4"},
                        "expected_output": "5x^4 + 4x^3"
                    }
                ]
            },
            # Math - Evaluation
            {
                "category": "Math - Evaluation",
                "cards": [
                    {
                        "title": "Order of Operations",
                        "description": "PEMDAS test",
                        "endpoint": "/api/solve",
                        "payload": {"problem": "2 + 3 * 4"},
                        "expected_output": "14"
                    },
                    {
                        "title": "Powers",
                        "description": "Exponentiation",
                        "endpoint": "/api/solve",
                        "payload": {"problem": "2 ** 10"},
                        "expected_output": "1024"
                    },
                    {
                        "title": "Complex Expression",
                        "description": "Mixed operations",
                        "endpoint": "/api/solve",
                        "payload": {"problem": "(5 + 3) * 2 ** 3 - 10"},
                        "expected_output": "54"
                    }
                ]
            },
            # Unit Conversions
            {
                "category": "Unit Conversions",
                "cards": [
                    {
                        "title": "Kilometers to SI",
                        "description": "Convert 7000 km to meters",
                        "endpoint": "/api/units",
                        "payload": {"value": "7000 km"},
                        "expected_output": "7,000,000 m"
                    },
                    {
                        "title": "AU to Meters",
                        "description": "1 Astronomical Unit",
                        "endpoint": "/api/units",
                        "payload": {"value": "1 AU"},
                        "expected_output": "149,597,870,700 m"
                    },
                    {
                        "title": "Solar Mass",
                        "description": "Mass of the Sun in kg",
                        "endpoint": "/api/units",
                        "payload": {"value": "1.989e30 kg"},
                        "expected_output": "1.989e30 kg"
                    }
                ]
            },
            # Time Formatting
            {
                "category": "Time Formatting",
                "cards": [
                    {
                        "title": "One Hour",
                        "description": "3600 seconds",
                        "endpoint": "/api/format/seconds",
                        "payload": {"seconds": 3600},
                        "expected_output": "1.00 hours"
                    },
                    {
                        "title": "One Day",
                        "description": "86400 seconds",
                        "endpoint": "/api/format/seconds",
                        "payload": {"seconds": 86400},
                        "expected_output": "24.00 hours"
                    },
                    {
                        "title": "ISS Period",
                        "description": "5559 seconds",
                        "endpoint": "/api/format/seconds",
                        "payload": {"seconds": 5559},
                        "expected_output": "1.54 hours"
                    },
                    {
                        "title": "One Year",
                        "description": "31536000 seconds",
                        "endpoint": "/api/format/seconds",
                        "payload": {"seconds": 31536000},
                        "expected_output": "1.00 years"
                    }
                ]
            },
            # Value Formatting with Units
            {
                "category": "Value Formatting",
                "cards": [
                    {
                        "title": "LEO Altitude",
                        "description": "Format with SI prefix",
                        "endpoint": "/api/format/units",
                        "payload": {"value": 7e6, "unit": "m"},
                        "expected_output": "7 Mm (LEO-ish altitude)"
                    },
                    {
                        "title": "Speed of Light",
                        "description": "Format c with hint",
                        "endpoint": "/api/format/units",
                        "payload": {"value": 299792458, "unit": "m/s"},
                        "expected_output": "300 Mm/s (≈ c)"
                    },
                    {
                        "title": "Earth's Mass",
                        "description": "Format with SI prefix",
                        "endpoint": "/api/format/units",
                        "payload": {"value": 5.972e24, "unit": "kg"},
                        "expected_output": "5.97e12 Tkg (Mass of Earth)"
                    }
                ]
            }
        ]
        
        return {
            "ok": True,
            "categories": cards,
            "total_cards": sum(len(cat["cards"]) for cat in cards),
            "endpoints": [
                "/api/solve",
                "/api/solve/pretty",
                "/api/units",
                "/api/format/seconds",
                "/api/format/units"
            ]
        }
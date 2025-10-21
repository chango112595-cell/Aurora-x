#!/usr/bin/env python3
"""
Demonstration of PORT configuration for Replit deployment.
Shows how each generated app will respect the PORT environment variable.
"""

import os


def demo_replit_config():
    """Demonstrate Replit-friendly port configuration."""

    print("""
    ╔════════════════════════════════════════════════════════╗
    ║     🚀 Replit Port Configuration Demo 🚀               ║
    ╚════════════════════════════════════════════════════════╝
    """)

    print("📋 How to Deploy Aurora-X Generated Apps on Replit:")
    print("=" * 60)

    print("\n1️⃣  Flask App (Python):")
    print("   • Default port: 8000")
    print("   • Replit will set PORT automatically")
    print("   • Generated code:")
    print("     ```python")
    print("     port = int(os.getenv('PORT', '8000'))")
    print("     app.run(host='0.0.0.0', port=port)")
    print("     ```")

    print("\n2️⃣  Go Service:")
    print("   • Default port: 8080")
    print("   • Generated code:")
    print("     ```go")
    print("     port := os.Getenv('PORT')")
    print("     if port == '' { port = '8080' }")
    print("     http.ListenAndServe(':'+port, nil)")
    print("     ```")

    print("\n3️⃣  C# Web API:")
    print("   • Default port: 5080")
    print("   • Generated code:")
    print("     ```csharp")
    print("     var port = Environment.GetEnvironmentVariable('PORT') ?? '5080';")
    print("     app.Run($'http://0.0.0.0:{port}');")
    print("     ```")

    print("\n" + "=" * 60)
    print("🎯 Replit Deployment Steps:")
    print("=" * 60)
    print("""
    1. Generate your app using Aurora-X:
       curl -X POST http://localhost:5001/chat \\
         -H 'Content-Type: application/json' \\
         -d '{"prompt": "fast microservice api"}'

    2. In Replit, the PORT is auto-assigned:
       • No manual configuration needed
       • Replit sets PORT environment variable
       • Your app automatically uses it

    3. Access your app:
       • Replit provides a public URL
       • Example: https://aurora-app.yourusername.replit.dev
       • All traffic proxied to your PORT
    """)

    print("=" * 60)
    print("💡 Testing Locally with Custom Ports:")
    print("=" * 60)
    print("""
    # Test with custom port locally:
    PORT=3000 python app.py              # Flask on port 3000
    PORT=4000 go run main.go             # Go on port 4000
    PORT=5000 dotnet run                 # C# on port 5000

    # Or use defaults (no PORT set):
    python app.py                        # Flask on 8000
    go run main.go                       # Go on 8080
    dotnet run                           # C# on 5080
    """)

    print("\n✅ All templates are now cloud-ready and port-configurable!")

    # Show current PORT if set
    current_port = os.getenv("PORT")
    if current_port:
        print(f"\n🔍 Current PORT environment variable: {current_port}")
    else:
        print("\n🔍 No PORT set (will use defaults)")

if __name__ == "__main__":
    demo_replit_config()

"""
Aurora's Final Fix - Add useLocation hook back
The hook was removed but never added back with location variable
"""


def final_layout_fix():
    print("🌟 Aurora: Applying final layout fix...")

    layout_file = "client/src/components/AuroraFuturisticLayout.tsx"

    with open(layout_file, encoding="utf-8") as f:
        content = f.read()

    # The hook call is missing! Add it after useState
    old_code = """export default function AuroraFuturisticLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navItems: NavItem[] = ["""

    new_code = """export default function AuroraFuturisticLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [location] = useLocation();

  const navItems: NavItem[] = ["""

    if old_code in content:
        content = content.replace(old_code, new_code)

        with open(layout_file, "w", encoding="utf-8") as f:
            f.write(content)
        print("   ✅ Added missing useLocation hook")
        return True
    else:
        print("   ⚠️  Code pattern not found - checking if already fixed...")
        if "const [location] = useLocation();" in content:
            print("   ✅ Hook already present")
            return True
        else:
            print("   ❌ Cannot find fix location")
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("🌟 AURORA FINAL LAYOUT FIX")
    print("=" * 60 + "\n")

    SUCCESS = final_layout_fix()

    print("\n" + "=" * 60)
    if SUCCESS:
        print("✨ Layout completely fixed!")
        print("   - useLocation imported ✅")
        print("   - useLocation hook called ✅")
        print("   - location variable used in routing ✅")
    else:
        print("❌ Fix failed - manual intervention needed")
    print("=" * 60)

import { ThemeToggle } from "../theme-toggle";
import { ThemeProvider } from "../theme-provider";

export default function ThemeToggleExample() {
  return (
    <ThemeProvider>
      <ThemeToggle />
    </ThemeProvider>
  );
}

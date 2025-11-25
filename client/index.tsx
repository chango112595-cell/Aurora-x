/**
 * Aurora Entry Point - Pure TSX (No HTML)
 * Converts traditional HTML entry to full TypeScript/React control
 */
import { createRoot } from "react-dom/client";
import App from "./src/App";
import "./src/index.css";
import { queryClient } from "./src/lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";

// Create root element programmatically
const rootElement = document.getElementById("root");

if (!rootElement) {
    // If root doesn't exist, create it
    const newRoot = document.createElement("div");
    newRoot.id = "root";
    document.body.appendChild(newRoot);

    console.log('🌟 Aurora: Created root element programmatically');

    createRoot(newRoot).render(
        <QueryClientProvider client={queryClient}>
            <App />
            <Toaster />
        </QueryClientProvider>
    );
} else {
    console.log('🌟 Aurora: Mounting to existing root element');
    createRoot(rootElement).render(
        <QueryClientProvider client={queryClient}>
            <App />
            <Toaster />
        </QueryClientProvider>
    );
}

console.log('✅ Aurora: Pure TSX entry loaded - 188 power units ready');

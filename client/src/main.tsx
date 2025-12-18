import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";

console.log('Aurora: Starting React app...');

const rootElement = document.getElementById("root");

if (!rootElement) {
  console.error('Aurora: Root element not found! Cannot mount React app.');
  document.body.innerHTML = '<h1>ERROR: React root element not found</h1>';
} else {
  try {
    console.log('Aurora: Mounting React app to root element...');
    createRoot(rootElement).render(
      <QueryClientProvider client={queryClient}>
        <App />
        <Toaster />
      </QueryClientProvider>
    );
    console.log('Aurora: React app mounted successfully!');
  } catch (error) {
    console.error('Aurora: Failed to render app:', error);
    rootElement.innerHTML = `<div style="padding: 20px; color: red;"><h1>Application Error</h1><p>${error instanceof Error ? error.message : 'Unknown error'}</p></div>`;
  }
}

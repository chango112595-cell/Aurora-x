/**
 * Aurora's Autonomous Error Detection System
 * Monitors and auto-fixes runtime errors
 */

'use client';

import { useEffect } from 'react';

export function AuroraErrorMonitor() {
    useEffect(() => {
        // Global error handler
        const handleError = (event: ErrorEvent) => {
            console.error('[AURORA ERROR DETECTED]', {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error,
            });

            // Aurora's autonomous analysis
            const errorType = event.error?.name || 'Unknown';
            const errorMessage = event.message;

            // Report to Aurora's intelligence
            fetch('/api/aurora/error-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: errorType,
                    message: errorMessage,
                    stack: event.error?.stack,
                    location: {
                        file: event.filename,
                        line: event.lineno,
                        column: event.colno,
                    },
                    timestamp: new Date().toISOString(),
                }),
            }).catch(console.error);

            // Prevent default error handling
            event.preventDefault();
        };

        // Unhandled promise rejections
        const handleRejection = (event: PromiseRejectionEvent) => {
            console.error('[AURORA PROMISE REJECTION]', {
                reason: event.reason,
                promise: event.promise,
            });

            fetch('/api/aurora/error-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'UnhandledPromiseRejection',
                    message: String(event.reason),
                    timestamp: new Date().toISOString(),
                }),
            }).catch(console.error);

            event.preventDefault();
        };

        // React error boundary fallback
        const handleReactError = (error: Error, errorInfo: any) => {
            console.error('[AURORA REACT ERROR]', error, errorInfo);

            fetch('/api/aurora/error-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'ReactError',
                    message: error.message,
                    stack: error.stack,
                    componentStack: errorInfo?.componentStack,
                    timestamp: new Date().toISOString(),
                }),
            }).catch(console.error);
        };

        window.addEventListener('error', handleError);
        window.addEventListener('unhandledrejection', handleRejection);

        // Store for React error boundary
        (window as any).__auroraReactErrorHandler = handleReactError;

        return () => {
            window.removeEventListener('error', handleError);
            window.removeEventListener('unhandledrejection', handleRejection);
            delete (window as any).__auroraReactErrorHandler;
        };
    }, []);

    return null;
}

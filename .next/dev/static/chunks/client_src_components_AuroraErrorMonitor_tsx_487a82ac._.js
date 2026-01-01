(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/client/src/components/AuroraErrorMonitor.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Aurora's Autonomous Error Detection System
 * Monitors and auto-fixes runtime errors
 */ __turbopack_context__.s([
    "AuroraErrorMonitor",
    ()=>AuroraErrorMonitor
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
'use client';
;
function AuroraErrorMonitor() {
    _s();
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AuroraErrorMonitor.useEffect": ()=>{
            // Global error handler
            const handleError = {
                "AuroraErrorMonitor.useEffect.handleError": (event)=>{
                    console.error('[AURORA ERROR DETECTED]', {
                        message: event.message,
                        filename: event.filename,
                        lineno: event.lineno,
                        colno: event.colno,
                        error: event.error
                    });
                    // Aurora's autonomous analysis
                    const errorType = event.error?.name || 'Unknown';
                    const errorMessage = event.message;
                    // Report to Aurora's intelligence
                    fetch('/api/aurora/error-report', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            type: errorType,
                            message: errorMessage,
                            stack: event.error?.stack,
                            location: {
                                file: event.filename,
                                line: event.lineno,
                                column: event.colno
                            },
                            timestamp: new Date().toISOString()
                        })
                    }).catch(console.error);
                    // Prevent default error handling
                    event.preventDefault();
                }
            }["AuroraErrorMonitor.useEffect.handleError"];
            // Unhandled promise rejections
            const handleRejection = {
                "AuroraErrorMonitor.useEffect.handleRejection": (event)=>{
                    console.error('[AURORA PROMISE REJECTION]', {
                        reason: event.reason,
                        promise: event.promise
                    });
                    fetch('/api/aurora/error-report', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            type: 'UnhandledPromiseRejection',
                            message: String(event.reason),
                            timestamp: new Date().toISOString()
                        })
                    }).catch(console.error);
                    event.preventDefault();
                }
            }["AuroraErrorMonitor.useEffect.handleRejection"];
            // React error boundary fallback
            const handleReactError = {
                "AuroraErrorMonitor.useEffect.handleReactError": (error, errorInfo)=>{
                    console.error('[AURORA REACT ERROR]', error, errorInfo);
                    fetch('/api/aurora/error-report', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            type: 'ReactError',
                            message: error.message,
                            stack: error.stack,
                            componentStack: errorInfo?.componentStack,
                            timestamp: new Date().toISOString()
                        })
                    }).catch(console.error);
                }
            }["AuroraErrorMonitor.useEffect.handleReactError"];
            window.addEventListener('error', handleError);
            window.addEventListener('unhandledrejection', handleRejection);
            // Store for React error boundary
            window.__auroraReactErrorHandler = handleReactError;
            return ({
                "AuroraErrorMonitor.useEffect": ()=>{
                    window.removeEventListener('error', handleError);
                    window.removeEventListener('unhandledrejection', handleRejection);
                    delete window.__auroraReactErrorHandler;
                }
            })["AuroraErrorMonitor.useEffect"];
        }
    }["AuroraErrorMonitor.useEffect"], []);
    return null;
}
_s(AuroraErrorMonitor, "OD7bBpZva5O2jO+Puf00hKivP7c=");
_c = AuroraErrorMonitor;
var _c;
__turbopack_context__.k.register(_c, "AuroraErrorMonitor");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=client_src_components_AuroraErrorMonitor_tsx_487a82ac._.js.map
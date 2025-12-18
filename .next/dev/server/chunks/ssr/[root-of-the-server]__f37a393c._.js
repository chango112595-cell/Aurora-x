module.exports = [
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[project]/client/src/components/AuroraErrorMonitor.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Aurora's Autonomous Error Detection System
 * Monitors and auto-fixes runtime errors
 */ __turbopack_context__.s([
    "AuroraErrorMonitor",
    ()=>AuroraErrorMonitor
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
'use client';
;
function AuroraErrorMonitor() {
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        // Global error handler
        const handleError = (event)=>{
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
        };
        // Unhandled promise rejections
        const handleRejection = (event)=>{
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
        };
        // React error boundary fallback
        const handleReactError = (error, errorInfo)=>{
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
        };
        window.addEventListener('error', handleError);
        window.addEventListener('unhandledrejection', handleRejection);
        // Store for React error boundary
        window.__auroraReactErrorHandler = handleReactError;
        return ()=>{
            window.removeEventListener('error', handleError);
            window.removeEventListener('unhandledrejection', handleRejection);
            delete window.__auroraReactErrorHandler;
        };
    }, []);
    return null;
}
}),
"[project]/node_modules/next/dist/server/route-modules/app-page/module.compiled.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
;
else {
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    else {
        if ("TURBOPACK compile-time truthy", 1) {
            if ("TURBOPACK compile-time truthy", 1) {
                module.exports = __turbopack_context__.r("[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)");
            } else //TURBOPACK unreachable
            ;
        } else //TURBOPACK unreachable
        ;
    }
} //# sourceMappingURL=module.compiled.js.map
}),
"[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

module.exports = __turbopack_context__.r("[project]/node_modules/next/dist/server/route-modules/app-page/module.compiled.js [app-ssr] (ecmascript)").vendored['react-ssr'].React; //# sourceMappingURL=react.js.map
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__f37a393c._.js.map
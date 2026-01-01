module.exports = [
"[externals]/child_process [external] (child_process, cjs, async loader)", ((__turbopack_context__) => {

__turbopack_context__.v((parentImport) => {
    return Promise.all([
  "server/chunks/[externals]_child_process_964038fc._.js"
].map((chunk) => __turbopack_context__.l(chunk))).then(() => {
        return parentImport("[externals]/child_process [external] (child_process, cjs)");
    });
});
}),
"[externals]/path [external] (path, cjs, async loader)", ((__turbopack_context__) => {

__turbopack_context__.v((parentImport) => {
    return Promise.resolve().then(() => {
        return parentImport("[externals]/path [external] (path, cjs)");
    });
});
}),
];
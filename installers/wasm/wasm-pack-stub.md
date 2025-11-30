# wasm-pack / Rust tips

If you want a native WASM module:

1) Install wasm-pack: cargo install wasm-pack
2) Create a Rust library with wasm-bindgen
3) Build with: wasm-pack build --target web
4) Import the generated JS/WASM in your web application

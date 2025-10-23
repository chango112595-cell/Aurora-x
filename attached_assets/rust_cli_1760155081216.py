RUST_MAIN = """fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.is_empty() {
        println!("rust cli ready. pass some args");
    } else {
        println!("args: {}", args.join(" "));
    }
}
"""

CARGO_TOML = """[package]
name = "aurora_cli"
version = "0.1.0"
edition = "2021"

[dependencies]
"""


def render_rust_cli(name: str) -> dict:
    return {"files": {"Cargo.toml": CARGO_TOML, "src/main.rs": RUST_MAIN}, "hint": "Run: cargo run -- hello world"}

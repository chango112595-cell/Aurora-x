
import { corpusStorage } from "../server/corpus-storage";

// Add a few test entries
const testEntries = [
  {
    id: "test-entry-1",
    timestamp: new Date().toISOString(),
    spec_id: "test-spec-1",
    spec_hash: "abc123",
    func_name: "add_numbers",
    func_signature: "def add_numbers(a: int, b: int) -> int",
    passed: 5,
    total: 5,
    score: 1.0,
    failing_tests: [],
    snippet: "def add_numbers(a: int, b: int) -> int:\n    return a + b",
    complexity: 1,
    iteration: 1,
    calls_functions: [],
    sig_key: "add_numbers|int,int|int",
    post_bow: ["add", "numbers", "return"],
    duration_ms: 50,
    synthesis_method: "beam_search"
  },
  {
    id: "test-entry-2",
    timestamp: new Date().toISOString(),
    spec_id: "test-spec-2",
    spec_hash: "def456",
    func_name: "reverse_string",
    func_signature: "def reverse_string(s: str) -> str",
    passed: 3,
    total: 3,
    score: 1.0,
    failing_tests: [],
    snippet: "def reverse_string(s: str) -> str:\n    return s[::-1]",
    complexity: 1,
    iteration: 1,
    calls_functions: [],
    sig_key: "reverse_string|str|str",
    post_bow: ["reverse", "string", "return"],
    duration_ms: 45,
    synthesis_method: "beam_search"
  }
];

console.log("[Test Corpus] Adding test entries...");
for (const entry of testEntries) {
  corpusStorage.insertEntry(entry);
  console.log(`[Test Corpus] Added: ${entry.func_name}`);
}

console.log("[Test Corpus] Done! Added", testEntries.length, "entries");
corpusStorage.close();

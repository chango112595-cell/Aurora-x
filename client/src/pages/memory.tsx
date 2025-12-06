import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Database, Brain, Search, Plus, AlertCircle, CheckCircle, Activity } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface MemoryStatus {
  success: boolean;
  status: {
    short_term_count: number;
    long_term_count: number;
    total_entries: number;
  };
}

interface MemoryRecord {
  id: string;
  text: string;
  meta: Record<string, any>;
  timestamp: string;
  score?: number;
}

interface MemoryWriteResult {
  success: boolean;
  id?: string;
  longterm?: boolean;
  error?: string;
}

interface MemoryQueryResult {
  success: boolean;
  results?: MemoryRecord[];
  error?: string;
}

export default function Memory() {
  const [status, setStatus] = useState<MemoryStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [writeText, setWriteText] = useState('');
  const [writeMeta, setWriteMeta] = useState('{}');
  const [writeLongterm, setWriteLongterm] = useState(false);
  const [queryText, setQueryText] = useState('');
  const [queryTopK, setQueryTopK] = useState(5);
  const [queryResults, setQueryResults] = useState<MemoryRecord[]>([]);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/memory/status');
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch memory status:', error);
    }
  };

  const handleWrite = async () => {
    setLoading(true);
    setMessage(null);
    try {
      let meta = {};
      try {
        meta = JSON.parse(writeMeta);
      } catch (e) {
        setMessage({ type: 'error', text: 'Invalid JSON in metadata field' });
        setLoading(false);
        return;
      }

      const response = await fetch('/api/memory/write', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: writeText,
          meta,
          longterm: writeLongterm,
        }),
      });

      const data: MemoryWriteResult = await response.json();
      
      if (data.success) {
        setMessage({ 
          type: 'success', 
          text: `Memory stored successfully! ID: ${data.id?.substring(0, 8)}... (${data.longterm ? 'Long-term' : 'Short-term'})` 
        });
        setWriteText('');
        setWriteMeta('{}');
        fetchStatus();
      } else {
        setMessage({ type: 'error', text: data.error || 'Failed to store memory' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error}` });
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch('/api/memory/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryText,
          top_k: queryTopK,
        }),
      });

      const data: MemoryQueryResult = await response.json();
      
      if (data.success && data.results) {
        setQueryResults(data.results);
        setMessage({ 
          type: 'success', 
          text: `Found ${data.results.length} matching memor${data.results.length === 1 ? 'y' : 'ies'}` 
        });
      } else {
        setMessage({ type: 'error', text: data.error || 'Query failed' });
        setQueryResults([]);
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error}` });
      setQueryResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-slate-900 to-gray-950 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <div className="relative">
            <div className="absolute inset-0 bg-cyan-500/30 rounded-full blur-md animate-pulse" />
            <div className="relative w-16 h-16 rounded-full border-2 border-cyan-400/50 flex items-center justify-center bg-gradient-to-br from-cyan-500/20 to-purple-500/20 backdrop-blur-sm">
              <Brain className="w-8 h-8 text-cyan-400" />
            </div>
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
              Aurora Memory System
            </h1>
            <p className="text-cyan-300/70 mt-1">Multi-layer hybrid memory with semantic search</p>
          </div>
        </div>

        {/* Status Message */}
        {message && (
          <div className={`p-4 rounded-lg border flex items-center gap-3 ${
            message.type === 'success' 
              ? 'bg-green-500/10 border-green-500/30 text-green-400'
              : 'bg-red-500/10 border-red-500/30 text-red-400'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle className="w-5 h-5" />
            ) : (
              <AlertCircle className="w-5 h-5" />
            )}
            <span>{message.text}</span>
          </div>
        )}

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-gradient-to-br from-cyan-950/50 to-purple-950/50 border-cyan-500/20 backdrop-blur-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-cyan-400 flex items-center gap-2">
                <Database className="w-5 h-5" />
                Memory Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              {status ? (
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-cyan-300/70">Short-term:</span>
                    <Badge variant="outline" className="bg-cyan-500/10 border-cyan-500/30 text-cyan-300">
                      {status.status.short_term_count}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-cyan-300/70">Long-term:</span>
                    <Badge variant="outline" className="bg-purple-500/10 border-purple-500/30 text-purple-300">
                      {status.status.long_term_count}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-cyan-300/70">Total:</span>
                    <Badge variant="outline" className="bg-blue-500/10 border-blue-500/30 text-blue-300">
                      {status.status.total_entries}
                    </Badge>
                  </div>
                </div>
              ) : (
                <div className="text-cyan-300/50 flex items-center gap-2">
                  <Activity className="w-4 h-4 animate-spin" />
                  Loading...
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-cyan-950/50 to-purple-950/50 border-cyan-500/20 backdrop-blur-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-cyan-400 flex items-center gap-2">
                <Brain className="w-5 h-5 animate-pulse" />
                System Health
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50" />
                <span className="text-green-400 font-mono">OPERATIONAL</span>
              </div>
              <p className="text-cyan-300/50 text-sm mt-2">
                Memory bridge connected
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-cyan-950/50 to-purple-950/50 border-cyan-500/20 backdrop-blur-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-cyan-400 flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Auto-Compression
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-cyan-300/70 text-sm">
                  Short → Mid: 10 messages
                </div>
                <div className="text-cyan-300/70 text-sm">
                  Mid → Long: 10 summaries
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Write Memory */}
          <Card className="bg-gradient-to-br from-cyan-950/50 to-purple-950/50 border-cyan-500/20 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-cyan-400 flex items-center gap-2">
                <Plus className="w-5 h-5" />
                Store Memory
              </CardTitle>
              <CardDescription className="text-cyan-300/50">
                Add new memories to the system
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-cyan-300/70 text-sm mb-2 block">Memory Text</label>
                <Textarea
                  value={writeText}
                  onChange={(e) => setWriteText(e.target.value)}
                  placeholder="Enter the memory text..."
                  className="bg-cyan-950/30 border-cyan-500/20 text-cyan-100 placeholder:text-cyan-500/30"
                  rows={4}
                />
              </div>

              <div>
                <label className="text-cyan-300/70 text-sm mb-2 block">Metadata (JSON)</label>
                <Textarea
                  value={writeMeta}
                  onChange={(e) => setWriteMeta(e.target.value)}
                  placeholder='{"type": "example", "tags": ["tag1"]}'
                  className="bg-cyan-950/30 border-cyan-500/20 text-cyan-100 font-mono text-sm placeholder:text-cyan-500/30"
                  rows={3}
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="longterm"
                  checked={writeLongterm}
                  onChange={(e) => setWriteLongterm(e.target.checked)}
                  className="w-4 h-4 rounded border-cyan-500/30 bg-cyan-950/30"
                />
                <label htmlFor="longterm" className="text-cyan-300/70 text-sm">
                  Store in long-term memory
                </label>
              </div>

              <Button
                onClick={handleWrite}
                disabled={loading || !writeText}
                className="w-full bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white"
              >
                <Plus className="w-4 h-4 mr-2" />
                Store Memory
              </Button>
            </CardContent>
          </Card>

          {/* Query Memory */}
          <Card className="bg-gradient-to-br from-cyan-950/50 to-purple-950/50 border-cyan-500/20 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-cyan-400 flex items-center gap-2">
                <Search className="w-5 h-5" />
                Search Memories
              </CardTitle>
              <CardDescription className="text-cyan-300/50">
                Query the memory system with semantic search
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-cyan-300/70 text-sm mb-2 block">Search Query</label>
                <Input
                  value={queryText}
                  onChange={(e) => setQueryText(e.target.value)}
                  placeholder="Enter search query..."
                  className="bg-cyan-950/30 border-cyan-500/20 text-cyan-100 placeholder:text-cyan-500/30"
                  onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
                />
              </div>

              <div>
                <label className="text-cyan-300/70 text-sm mb-2 block">Top K Results</label>
                <Input
                  type="number"
                  value={queryTopK}
                  onChange={(e) => setQueryTopK(parseInt(e.target.value) || 5)}
                  min={1}
                  max={20}
                  className="bg-cyan-950/30 border-cyan-500/20 text-cyan-100"
                />
              </div>

              <Button
                onClick={handleQuery}
                disabled={loading || !queryText}
                className="w-full bg-gradient-to-r from-purple-500 to-cyan-500 hover:from-purple-600 hover:to-cyan-600 text-white"
              >
                <Search className="w-4 h-4 mr-2" />
                Search
              </Button>

              <Button
                onClick={() => {
                  setQueryText('conversation');
                  setQueryTopK(10);
                }}
                variant="outline"
                className="w-full border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/10"
              >
                Show Recent Conversations
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Query Results */}
        {queryResults.length > 0 && (
          <Card className="bg-gradient-to-br from-cyan-950/50 to-purple-950/50 border-cyan-500/20 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-cyan-400">Search Results</CardTitle>
              <CardDescription className="text-cyan-300/50">
                Found {queryResults.length} matching memor{queryResults.length === 1 ? 'y' : 'ies'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {queryResults.map((result, idx) => (
                <div
                  key={result.id}
                  className="p-4 rounded-lg bg-cyan-950/30 border border-cyan-500/20 hover:border-cyan-500/40 transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <Badge variant="outline" className="bg-cyan-500/10 border-cyan-500/30 text-cyan-300">
                      #{idx + 1}
                    </Badge>
                    {result.score !== undefined && (
                      <Badge variant="outline" className="bg-purple-500/10 border-purple-500/30 text-purple-300">
                        Score: {result.score.toFixed(3)}
                      </Badge>
                    )}
                  </div>
                  <p className="text-cyan-100 mb-2">{result.text}</p>
                  <div className="flex items-center gap-3 text-xs text-cyan-400/50">
                    <span className="font-mono">{result.id.substring(0, 8)}...</span>
                    <span>{new Date(result.timestamp).toLocaleString()}</span>
                  </div>
                  {Object.keys(result.meta).length > 0 && (
                    <div className="mt-2 p-2 bg-cyan-950/50 rounded border border-cyan-500/10">
                      <pre className="text-xs text-cyan-300/70 font-mono">
                        {JSON.stringify(result.meta, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

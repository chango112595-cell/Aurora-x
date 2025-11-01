import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CheckCircle, AlertCircle, GitBranch, Code2, Zap, Shield, TrendingUp, RefreshCw, GitCommit } from 'lucide-react';

interface Commit {
    hash: string;
    message: string;
    short_hash: string;
}

interface FileChange {
    status: string;
    file: string;
    status_text: string;
}

interface AuroraRun {
    name: string;
    path: string;
    has_graph_diff: boolean;
    has_scores_diff: boolean;
    has_report: boolean;
    start_time?: number;
    duration?: number;
    seed?: number;
    max_iters?: number;
}

interface BranchInfo {
    name: string;
    commit_count: number;
    last_commit: string;
    last_commit_message: string;
    unique_features: string[];
    file_changes: number;
    lines_added: number;
    lines_deleted: number;
    feature_category: string;
    improvement_score: number;
}

interface ComparisonItem {
    id: string;
    title: string;
    description: string;
    status: 'approved' | 'pending' | 'rejected';
    category: string;
}

export default function ComparisonDashboard() {
    const [approvedItems, setApprovedItems] = useState<Set<string>>(new Set());
    const [commits, setCommits] = useState<Commit[]>([]);
    const [auroraRuns, setAuroraRuns] = useState<AuroraRun[]>([]);
    const [selectedCommit1, setSelectedCommit1] = useState<string>('');
    const [selectedCommit2, setSelectedCommit2] = useState<string>('');
    const [fileChanges, setFileChanges] = useState<FileChange[]>([]);
    const [currentBranch, setCurrentBranch] = useState<string>('');
    const [branches, setBranches] = useState<BranchInfo[]>([]);
    const [selectedBranch, setSelectedBranch] = useState<string>('');
    const [branchAnalysis, setBranchAnalysis] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    // Fetch real data from APIs
    const fetchCommits = async () => {
        try {
            const response = await fetch('/api/bridge/comparison/commits');
            const data = await response.json();
            if (data.ok) {
                setCommits(data.commits);
                setCurrentBranch(data.current_branch);
            }
        } catch (error) {
            console.error('Failed to fetch commits:', error);
        }
    };

    const fetchAuroraRuns = async () => {
        try {
            const response = await fetch('/api/bridge/comparison/aurora-runs');
            const data = await response.json();
            if (data.ok) {
                setAuroraRuns(data.runs);
            }
        } catch (error) {
            console.error('Failed to fetch Aurora runs:', error);
        }
    };

    const fetchDiff = async (commit1?: string, commit2?: string) => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (commit1) params.append('commit1', commit1);
            if (commit2) params.append('commit2', commit2);

            const response = await fetch(`/api/bridge/comparison/diff?${params}`);
            const data = await response.json();
            if (data.ok) {
                setFileChanges(data.files);
            }
        } catch (error) {
            console.error('Failed to fetch diff:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchBranches = async () => {
        try {
            const response = await fetch('/api/bridge/comparison/branches');
            const data = await response.json();
            if (data.ok) {
                setBranches(data.branches);
            }
        } catch (error) {
            console.error('Failed to fetch branches:', error);
        }
    };

    const fetchBranchAnalysis = async (branchName: string) => {
        setLoading(true);
        try {
            const response = await fetch(`/api/bridge/comparison/branch-analysis?branch=${encodeURIComponent(branchName)}`);
            const data = await response.json();
            if (data.ok) {
                setBranchAnalysis(data.analysis);
            }
        } catch (error) {
            console.error('Failed to fetch branch analysis:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleApproval = (itemId: string, approved: boolean) => {
        const newApproved = new Set(approvedItems);
        if (approved) {
            newApproved.add(itemId);
        } else {
            newApproved.delete(itemId);
        }
        setApprovedItems(newApproved);
    };

    useEffect(() => {
        fetchCommits();
        fetchAuroraRuns();
        fetchBranches();
        fetchDiff(); // Get current working directory changes
    }, []);

    useEffect(() => {
        if (selectedCommit1 || selectedCommit2) {
            fetchDiff(selectedCommit1, selectedCommit2);
        }
    }, [selectedCommit1, selectedCommit2]);

    const comparisonData = {
        overview: {
            totalBranches: 45,
            activeDevelopment: 12,
            mergedFeatures: 156,
            pendingReviews: 8,
            codeHealth: 94
        },
        branches: [
            { name: 'main', commits: 1240, lastActivity: '2 hours ago', status: 'stable' },
            { name: 'feature/ai-engine', commits: 45, lastActivity: '15 minutes ago', status: 'active' },
            { name: 'feature/dashboard-v2', commits: 23, lastActivity: '1 hour ago', status: 'active' },
            { name: 'hotfix/security-patch', commits: 3, lastActivity: '30 minutes ago', status: 'urgent' }
        ],
        features: [
            {
                id: 'ai-synthesis',
                title: 'AI Code Synthesis Engine',
                description: 'Advanced AI-powered code generation with multi-language support',
                status: 'approved' as const,
                category: 'Core Feature',
                impact: 'High',
                complexity: 'High'
            },
            {
                id: 'dashboard-ui',
                title: 'Professional Dashboard UI',
                description: 'Modern, responsive dashboard with real-time metrics',
                status: 'pending' as const,
                category: 'UI/UX',
                impact: 'Medium',
                complexity: 'Medium'
            },
            {
                id: 'api-gateway',
                title: 'Unified API Gateway',
                description: 'Centralized API management with rate limiting and authentication',
                status: 'approved' as const,
                category: 'Infrastructure',
                impact: 'High',
                complexity: 'High'
            }
        ],
        improvements: [
            {
                id: 'performance-opt',
                title: 'Performance Optimization',
                description: 'Reduced load times by 60% through code splitting and lazy loading',
                category: 'Performance',
                metrics: { before: '3.2s', after: '1.3s', improvement: '59%' }
            },
            {
                id: 'security-hardening',
                title: 'Security Hardening',
                description: 'Implemented OAuth2, HTTPS enforcement, and input validation',
                category: 'Security',
                metrics: { vulnerabilities: '0', security_score: '98/100' }
            }
        ]
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
            <div className="container mx-auto max-w-7xl">
      {/* Aurora's Quantum Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-cyan-950/20 to-purple-950/20" />
        
        {/* Particle field */}
        <div className="absolute inset-0 opacity-20" style={
          backgroundImage: 'radial-gradient(circle, rgba(6, 182, 212, 0.3) 1px, transparent 1px)',
          backgroundSize: '50px 50px',
          animation: 'particleFloat 20s linear infinite'
        } />
        
        {/* Neural network grid */}
        <svg className="absolute inset-0 w-full h-full opacity-10">
          <defs>
            <linearGradient id="grid-ComparisonDashboard" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#a855f7" stopOpacity="0.5" />
            </linearGradient>
          </defs>
          <pattern id="grid-pattern-ComparisonDashboard" width="50" height="50" patternUnits="userSpaceOnUse">
            <circle cx="25" cy="25" r="1" fill="url(#grid-ComparisonDashboard)" />
          </pattern>
          <rect width="100%" height="100%" fill="url(#grid-pattern-ComparisonDashboard)" />
        </svg>
        
        {/* Holographic orbs */}
        <div className="absolute top-20 left-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={animationDelay: '2s'} />
      </div>

                {/* Header */}
                <div className="mb-8 text-center">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-4">
                        Aurora-X Comparison Dashboard
                    </h1>
                    <p className="text-slate-300 text-lg">
                        Professional Git History Analysis & Feature Comparison
                    </p>
                </div>

                <Tabs defaultValue="git-comparison" className="space-y-6">
                    <TabsList className="grid w-full grid-cols-8 bg-slate-800/50 backdrop-blur-sm">
                        <TabsTrigger value="git-comparison" className="text-cyan-400">Git Comparison</TabsTrigger>
                        <TabsTrigger value="branch-analysis" className="text-cyan-400">Branch Analysis</TabsTrigger>
                        <TabsTrigger value="aurora-runs" className="text-cyan-400">Aurora Runs</TabsTrigger>
                        <TabsTrigger value="overview" className="text-cyan-400">Overview</TabsTrigger>
                        <TabsTrigger value="branches" className="text-cyan-400">Branches</TabsTrigger>
                        <TabsTrigger value="features" className="text-cyan-400">Features</TabsTrigger>
                        <TabsTrigger value="diagnostics" className="text-cyan-400">Diagnostics</TabsTrigger>
                        <TabsTrigger value="approval" className="text-cyan-400">Approval</TabsTrigger>
                    </TabsList>

                    {/* Git Comparison Tab */}
                    <TabsContent value="git-comparison" className="space-y-6">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Commit Selection */}
                            <Card className="bg-slate-800/50 backdrop-blur-sm border-cyan-500/30 quantum-card">
                                <CardHeader>
                                    <CardTitle className="text-cyan-400 flex items-center gap-2">
                                        <GitCommit className="w-5 h-5" />
                                        Select Commits to Compare
                                    </CardTitle>
                                    <CardDescription>
                                        Current Branch: <Badge className="bg-purple-500/20 text-purple-400">{currentBranch}</Badge>
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div>
                                        <label className="text-sm text-slate-300 mb-2 block">Commit 1 (Base)</label>
                                        <Select value={selectedCommit1} onValueChange={setSelectedCommit1}>
                                            <SelectTrigger className="bg-slate-700 border-slate-600">
                                                <SelectValue placeholder="Select base commit" />
                                            </SelectTrigger>
                                            <SelectContent className="bg-slate-800 border-slate-600">
                                                <SelectItem value="working-dir">Working Directory</SelectItem>
                                                {commits.map((commit) => (
                                                    <SelectItem key={commit.hash} value={commit.hash}>
                                                        {commit.short_hash}: {commit.message}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <div>
                                        <label className="text-sm text-slate-300 mb-2 block">Commit 2 (Compare with)</label>
                                        <Select value={selectedCommit2} onValueChange={setSelectedCommit2}>
                                            <SelectTrigger className="bg-slate-700 border-slate-600">
                                                <SelectValue placeholder="Select commit to compare" />
                                            </SelectTrigger>
                                            <SelectContent className="bg-slate-800 border-slate-600">
                                                <SelectItem value="working-dir">Working Directory</SelectItem>
                                                {commits.map((commit) => (
                                                    <SelectItem key={commit.hash} value={commit.hash}>
                                                        {commit.short_hash}: {commit.message}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <Button
                                        onClick={() => fetchDiff(selectedCommit1, selectedCommit2)}
                                        className="w-full bg-gradient-to-r from-cyan-500 to-purple-500"
                                        disabled={loading}
                                    >
                                        {loading ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : null}
                                        Compare Commits
                                    </Button>
                                </CardContent>
                            </Card>

                            {/* File Changes */}
                            <Card className="bg-slate-800/50 backdrop-blur-sm border-green-500/30 quantum-card">
                                <CardHeader>
                                    <CardTitle className="text-green-400 flex items-center gap-2">
                                        <Code2 className="w-5 h-5" />
                                        File Changes ({fileChanges.length})
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-2 max-h-96 overflow-y-auto">
                                        {fileChanges.length === 0 ? (
                                            <p className="text-slate-400 text-center py-8">No changes found</p>
                                        ) : (
                                            fileChanges.map((change, index) => (
                                                <div key={index} className="flex items-center justify-between p-2 bg-slate-700/50 rounded">
                                                    <span className="text-slate-300 text-sm font-mono">{change.file}</span>
                                                    <Badge
                                                        className={
                                                            change.status === 'M' ? 'bg-yellow-500/20 text-yellow-400' :
                                                                change.status === 'A' ? 'bg-green-500/20 text-green-400' :
                                                                    change.status === 'D' ? 'bg-red-500/20 text-red-400' :
                                                                        'bg-blue-500/20 text-blue-400'
                                                        }
                                                    >
                                                        {change.status_text}
                                                    </Badge>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Full Diff View */}
                        {fileChanges.length > 0 && (
                            <Card className="bg-slate-800/50 backdrop-blur-sm border-purple-500/30 quantum-card">
                                <CardHeader>
                                    <CardTitle className="text-purple-400">Detailed Diff View</CardTitle>
                                    <CardDescription>
                                        Comparing: {selectedCommit1 || 'Working Directory'} vs {selectedCommit2 || 'Working Directory'}
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <Button
                                        onClick={() => window.open('/api/bridge/diff/full', '_blank')}
                                        className="bg-purple-500/20 text-purple-400 border border-purple-500/30 hover:bg-purple-500/30"
                                    >
                                        View Full Diff in New Tab
                                    </Button>
                                </CardContent>
                            </Card>
                        )}
                    </TabsContent>

                    {/* Branch Analysis Tab */}
                    <TabsContent value="branch-analysis" className="space-y-6">
                        <div className="grid grid-cols-1 gap-6">
                            {/* Branch Selection */}
                            <Card className="bg-slate-800/50 backdrop-blur-sm border-cyan-500/30 quantum-card">
                                <CardHeader>
                                    <CardTitle className="text-cyan-400 flex items-center gap-2">
                                        <GitBranch className="w-5 h-5" />
                                        Branch Feature Analysis
                                    </CardTitle>
                                    <CardDescription>
                                        Analyze features and improvements across different branches
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div>
                                        <label className="text-sm text-slate-300 mb-2 block">Select Branch to Analyze</label>
                                        <Select value={selectedBranch} onValueChange={setSelectedBranch}>
                                            <SelectTrigger className="bg-slate-700 border-slate-600">
                                                <SelectValue placeholder="Choose a branch for detailed analysis" />
                                            </SelectTrigger>
                                            <SelectContent className="bg-slate-800 border-slate-600">
                                                {branches.map((branch) => (
                                                    <SelectItem key={branch.name} value={branch.name}>
                                                        {branch.name} ({branch.commit_count} commits)
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <Button
                                        onClick={() => selectedBranch && fetchBranchAnalysis(selectedBranch)}
                                        disabled={!selectedBranch || loading}
                                        className="w-full bg-gradient-to-r from-cyan-500 to-purple-500"
                                    >
                                        {loading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : null}
                                        Analyze Branch Features
                                    </Button>
                                </CardContent>
                            </Card>

                            {/* Branch Overview Grid */}
                            {branches.length > 0 && (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {branches.map((branch) => (
                                        <Card key={branch.name} className="bg-slate-800/50 backdrop-blur-sm border-cyan-500/30 hover:border-cyan-400/50 transition-colors">
                                            <CardHeader className="pb-3">
                                                <CardTitle className="text-cyan-400 text-sm flex items-center justify-between">
                                                    <span className="truncate">{branch.name}</span>
                                                    <Badge className={`ml-2 ${branch.improvement_score > 7 ? 'bg-green-500/20 text-green-400' : branch.improvement_score > 4 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-500/20 text-gray-400'}`}>
                                                        {branch.improvement_score}/10
                                                    </Badge>
                                                </CardTitle>
                                                <CardDescription className="text-xs">
                                                    {branch.feature_category}
                                                </CardDescription>
                                            </CardHeader>
                                            <CardContent className="space-y-2">
                                                <div className="flex justify-between text-xs text-slate-400">
                                                    <span>Commits: {branch.commit_count}</span>
                                                    <span>Files: {branch.file_changes}</span>
                                                </div>
                                                <div className="flex justify-between text-xs text-slate-400">
                                                    <span className="text-green-400">+{branch.lines_added}</span>
                                                    <span className="text-red-400">-{branch.lines_deleted}</span>
                                                </div>
                                                <div className="space-y-1">
                                                    {branch.unique_features.slice(0, 3).map((feature, idx) => (
                                                        <Badge key={idx} className="text-xs bg-purple-500/20 text-purple-400 block">
                                                            {feature}
                                                        </Badge>
                                                    ))}
                                                    {branch.unique_features.length > 3 && (
                                                        <Badge className="text-xs bg-slate-500/20 text-slate-400">
                                                            +{branch.unique_features.length - 3} more
                                                        </Badge>
                                                    )}
                                                </div>
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    className="w-full text-xs"
                                                    onClick={() => {
                                                        setSelectedBranch(branch.name);
                                                        fetchBranchAnalysis(branch.name);
                                                    }}
                                                >
                                                    Analyze
                                                </Button>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            )}

                            {/* Detailed Branch Analysis Results */}
                            {branchAnalysis && (
                                <Card className="bg-slate-800/50 backdrop-blur-sm border-cyan-500/30 quantum-card">
                                    <CardHeader>
                                        <CardTitle className="text-cyan-400 flex items-center gap-2">
                                            <TrendingUp className="w-5 h-5" />
                                            Detailed Analysis: {selectedBranch}
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-6">
                                        {/* Feature Highlights */}
                                        <div>
                                            <h4 className="text-lg font-semibold text-white mb-3">Key Features & Improvements</h4>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                {branchAnalysis.key_features?.map((feature: any, idx: number) => (
                                                    <div key={idx} className="bg-slate-700/50 p-4 rounded-lg border border-slate-600">
                                                        <div className="flex items-center gap-2 mb-2">
                                                            <CheckCircle className="w-4 h-4 text-green-400" />
                                                            <span className="font-medium text-green-400">{feature.category}</span>
                                                        </div>
                                                        <p className="text-sm text-slate-300">{feature.description}</p>
                                                        <div className="mt-2">
                                                            <Badge className="text-xs bg-blue-500/20 text-blue-400">
                                                                Impact: {feature.impact}
                                                            </Badge>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Code Quality Metrics */}
                                        {branchAnalysis.quality_metrics && (
                                            <div>
                                                <h4 className="text-lg font-semibold text-white mb-3">Code Quality Metrics</h4>
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                    <div className="bg-slate-700/50 p-3 rounded-lg text-center">
                                                        <div className="text-2xl font-bold text-cyan-400">{branchAnalysis.quality_metrics.test_coverage}%</div>
                                                        <div className="text-xs text-slate-400">Test Coverage</div>
                                                    </div>
                                                    <div className="bg-slate-700/50 p-3 rounded-lg text-center">
                                                        <div className="text-2xl font-bold text-green-400">{branchAnalysis.quality_metrics.code_quality_score}/10</div>
                                                        <div className="text-xs text-slate-400">Code Quality</div>
                                                    </div>
                                                    <div className="bg-slate-700/50 p-3 rounded-lg text-center">
                                                        <div className="text-2xl font-bold text-purple-400">{branchAnalysis.quality_metrics.performance_score}/10</div>
                                                        <div className="text-xs text-slate-400">Performance</div>
                                                    </div>
                                                    <div className="bg-slate-700/50 p-3 rounded-lg text-center">
                                                        <div className="text-2xl font-bold text-yellow-400">{branchAnalysis.quality_metrics.maintainability}/10</div>
                                                        <div className="text-xs text-slate-400">Maintainability</div>
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* File Changes Summary */}
                                        {branchAnalysis.file_changes && (
                                            <div>
                                                <h4 className="text-lg font-semibold text-white mb-3">File Changes Summary</h4>
                                                <div className="space-y-2 max-h-60 overflow-y-auto">
                                                    {branchAnalysis.file_changes.map((change: any, idx: number) => (
                                                        <div key={idx} className="flex items-center justify-between bg-slate-700/30 p-3 rounded">
                                                            <div className="flex items-center gap-3">
                                                                <Badge className={`w-8 text-center ${change.status === 'A' ? 'bg-green-500/20 text-green-400' : change.status === 'M' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'}`}>
                                                                    {change.status}
                                                                </Badge>
                                                                <span className="text-sm font-mono text-slate-300">{change.file}</span>
                                                            </div>
                                                            <div className="flex gap-2 text-xs">
                                                                {change.additions > 0 && <span className="text-green-400">+{change.additions}</span>}
                                                                {change.deletions > 0 && <span className="text-red-400">-{change.deletions}</span>}
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Recommendations */}
                                        {branchAnalysis.recommendations && (
                                            <div>
                                                <h4 className="text-lg font-semibold text-white mb-3">Merge Recommendations</h4>
                                                <div className="bg-slate-700/30 p-4 rounded-lg border-l-4 border-cyan-400">
                                                    <div className="flex items-start gap-3">
                                                        <Shield className="w-5 h-5 text-cyan-400 mt-0.5" />
                                                        <div>
                                                            <p className="text-slate-300">{branchAnalysis.recommendations.summary}</p>
                                                            <div className="mt-3 space-y-2">
                                                                {branchAnalysis.recommendations.action_items?.map((item: string, idx: number) => (
                                                                    <div key={idx} className="flex items-center gap-2">
                                                                        <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></div>
                                                                        <span className="text-sm text-slate-400">{item}</span>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>
                            )}
                        </div>
                    </TabsContent>

                    {/* Aurora Runs Tab */}
                    <TabsContent value="aurora-runs" className="space-y-6">
                        <Card className="bg-slate-800/50 backdrop-blur-sm border-cyan-500/30 quantum-card">
                            <CardHeader>
                                <CardTitle className="text-cyan-400 flex items-center gap-2">
                                    <Zap className="w-5 h-5" />
                                    Aurora Run History ({auroraRuns.length} runs)
                                </CardTitle>
                                <CardDescription>Compare different Aurora synthesis runs and their results</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4 max-h-96 overflow-y-auto">
                                    {auroraRuns.length === 0 ? (
                                        <p className="text-slate-400 text-center py-8">No Aurora runs found</p>
                                    ) : (
                                        auroraRuns.map((run, index) => (
                                            <div key={index} className="p-4 bg-slate-700/50 rounded-lg">
                                                <div className="flex items-center justify-between mb-2">
                                                    <span className="text-cyan-400 font-mono text-sm">{run.name}</span>
                                                    <div className="flex gap-2">
                                                        {run.has_graph_diff && <Badge className="bg-green-500/20 text-green-400 text-xs">Graph Diff</Badge>}
                                                        {run.has_scores_diff && <Badge className="bg-blue-500/20 text-blue-400 text-xs">Scores Diff</Badge>}
                                                        {run.has_report && <Badge className="bg-purple-500/20 text-purple-400 text-xs">Report</Badge>}
                                                    </div>
                                                </div>
                                                <div className="text-slate-400 text-xs space-y-1">
                                                    {run.start_time && <div>Started: {new Date(run.start_time * 1000).toLocaleString()}</div>}
                                                    {run.duration && <div>Duration: {run.duration.toFixed(2)}s</div>}
                                                    {run.seed && <div>Seed: {run.seed}</div>}
                                                    {run.max_iters && <div>Max Iterations: {run.max_iters}</div>}
                                                </div>
                                                {run.has_report && (
                                                    <Button
                                                        size="sm"
                                                        className="mt-2 bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/30"
                                                        onClick={() => window.open(`/runs/${run.name}/report.html`, '_blank')}
                                                    >
                                                        View Report
                                                    </Button>
                                                )}
                                            </div>
                                        ))
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Overview Tab */}
                    <TabsContent value="overview" className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                            <Card className="bg-slate-800/50 backdrop-blur-sm border-cyan-500/30 quantum-card">
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-cyan-400 flex items-center gap-2">
                                        <GitBranch className="w-5 h-5" />
                                        Branches
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-white">{comparisonData.overview.totalBranches}</div>
                                    <p className="text-slate-400 text-sm">Total branches</p>
                                </CardContent>
                            </Card>

                            <Card className="bg-slate-800/50 backdrop-blur-sm border-purple-500/30 quantum-card">
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-purple-400 flex items-center gap-2">
                                        <Code2 className="w-5 h-5" />
                                        Active Dev
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-white">{comparisonData.overview.activeDevelopment}</div>
                                    <p className="text-slate-400 text-sm">Active branches</p>
                                </CardContent>
                            </Card>

                            <Card className="bg-slate-800/50 backdrop-blur-sm border-green-500/30 quantum-card">
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-green-400 flex items-center gap-2">
                                        <CheckCircle className="w-5 h-5" />
                                        Features
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-white">{comparisonData.overview.mergedFeatures}</div>
                                    <p className="text-slate-400 text-sm">Merged features</p>
                                </CardContent>
                            </Card>

                            <Card className="bg-slate-800/50 backdrop-blur-sm border-yellow-500/30 quantum-card">
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-yellow-400 flex items-center gap-2">
                                        <AlertCircle className="w-5 h-5" />
                                        Reviews
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-white">{comparisonData.overview.pendingReviews}</div>
                                    <p className="text-slate-400 text-sm">Pending reviews</p>
                                </CardContent>
                            </Card>

                            <Card className="bg-slate-800/50 backdrop-blur-sm border-blue-500/30 quantum-card">
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-blue-400 flex items-center gap-2">
                                        <TrendingUp className="w-5 h-5" />
                                        Health
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-white">{comparisonData.overview.codeHealth}%</div>
                                    <p className="text-slate-400 text-sm">Code health</p>
                                </CardContent>
                            </Card>
                        </div>
                    </TabsContent>

                    {/* Branches Tab */}
                    <TabsContent value="branches" className="space-y-6">
                        <div className="grid gap-4">
                            {comparisonData.branches.map((branch, index) => (
                                <Card key={index} className="bg-slate-800/50 backdrop-blur-sm border-cyan-500/30">
                                    <CardHeader>
                                        <div className="flex items-center justify-between">
                                            <CardTitle className="text-cyan-400 flex items-center gap-2">
                                                <GitBranch className="w-5 h-5" />
                                                {branch.name}
                                            </CardTitle>
                                            <Badge
                                                variant={branch.status === 'stable' ? 'default' : branch.status === 'active' ? 'secondary' : 'destructive'}
                                                className={
                                                    branch.status === 'stable' ? 'bg-green-500/20 text-green-400' :
                                                        branch.status === 'active' ? 'bg-blue-500/20 text-blue-400' :
                                                            'bg-red-500/20 text-red-400'
                                                }
                                            >
                                                {branch.status}
                                            </Badge>
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="flex justify-between text-sm text-slate-300">
                                            <span>{branch.commits} commits</span>
                                            <span>Last activity: {branch.lastActivity}</span>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </TabsContent>

                    {/* Features Tab */}
                    <TabsContent value="features" className="space-y-6">
                        <div className="grid gap-6">
                            {comparisonData.features.map((feature) => (
                                <Card key={feature.id} className="bg-slate-800/50 backdrop-blur-sm border-cyan-500/30">
                                    <CardHeader>
                                        <div className="flex items-center justify-between">
                                            <CardTitle className="text-cyan-400">{feature.title}</CardTitle>
                                            <div className="flex gap-2">
                                                <Badge className="bg-purple-500/20 text-purple-400">{feature.category}</Badge>
                                                <Badge
                                                    variant={feature.status === 'approved' ? 'default' : 'secondary'}
                                                    className={feature.status === 'approved' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}
                                                >
                                                    {feature.status}
                                                </Badge>
                                            </div>
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <CardDescription className="text-slate-300 mb-4">
                                            {feature.description}
                                        </CardDescription>
                                        <div className="flex gap-4 text-sm">
                                            <span className="text-slate-400">Impact: <span className="text-cyan-400">{feature.impact}</span></span>
                                            <span className="text-slate-400">Complexity: <span className="text-purple-400">{feature.complexity}</span></span>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </TabsContent>

                    {/* Improvements Tab */}
                    <TabsContent value="improvements" className="space-y-6">
                        <div className="grid gap-6">
                            {comparisonData.improvements.map((improvement) => (
                                <Card key={improvement.id} className="bg-slate-800/50 backdrop-blur-sm border-green-500/30">
                                    <CardHeader>
                                        <div className="flex items-center justify-between">
                                            <CardTitle className="text-green-400 flex items-center gap-2">
                                                <Zap className="w-5 h-5" />
                                                {improvement.title}
                                            </CardTitle>
                                            <Badge className="bg-green-500/20 text-green-400">{improvement.category}</Badge>
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <CardDescription className="text-slate-300 mb-4">
                                            {improvement.description}
                                        </CardDescription>
                                        <div className="flex gap-4 text-sm">
                                            {Object.entries(improvement.metrics).map(([key, value]) => (
                                                <span key={key} className="text-slate-400">
                                                    {key}: <span className="text-cyan-400">{value}</span>
                                                </span>
                                            ))}
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </TabsContent>

                    {/* Diagnostics Tab */}
                    <TabsContent value="diagnostics" className="space-y-6">
                        <Card className="bg-slate-800/50 backdrop-blur-sm border-blue-500/30 quantum-card">
                            <CardHeader>
                                <CardTitle className="text-blue-400 flex items-center gap-2">
                                    <Shield className="w-5 h-5" />
                                    System Diagnostics
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center">
                                        <span className="text-slate-300">Build Status</span>
                                        <Badge className="bg-green-500/20 text-green-400">Passing</Badge>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-slate-300">Test Coverage</span>
                                        <Badge className="bg-cyan-500/20 text-cyan-400">94%</Badge>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-slate-300">Security Scan</span>
                                        <Badge className="bg-green-500/20 text-green-400">No Issues</Badge>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-slate-300">Performance Score</span>
                                        <Badge className="bg-purple-500/20 text-purple-400">98/100</Badge>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Approval Tab */}
                    <TabsContent value="approval" className="space-y-6">
                        <Card className="bg-slate-800/50 backdrop-blur-sm border-cyan-500/30 quantum-card">
                            <CardHeader>
                                <CardTitle className="text-cyan-400">Feature Approval System</CardTitle>
                                <CardDescription>Review and approve features for production deployment</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {comparisonData.features.map((feature) => (
                                        <div key={feature.id} className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
                                            <div>
                                                <h4 className="text-white font-medium">{feature.title}</h4>
                                                <p className="text-slate-400 text-sm">{feature.description}</p>
                                            </div>
                                            <div className="flex gap-2">
                                                <Button
                                                    size="sm"
                                                    variant={approvedItems.has(feature.id) ? "default" : "outline"}
                                                    onClick={() => handleApproval(feature.id, !approvedItems.has(feature.id))}
                                                    className={approvedItems.has(feature.id)
                                                        ? "bg-green-500/20 text-green-400 border-green-500/30"
                                                        : "border-cyan-500/30 text-cyan-400"
                                                    }
                                                >
                                                    {approvedItems.has(feature.id) ? "Approved" : "Approve"}
                                                </Button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div className="mt-6 pt-6 border-t border-slate-700">
                                    <div className="flex justify-between items-center">
                                        <span className="text-slate-300">
                                            Approved: {approvedItems.size} / {comparisonData.features.length}
                                        </span>
                                        <Button
                                            className="bg-gradient-to-r from-cyan-500 to-purple-500 text-white"
                                            disabled={approvedItems.size !== comparisonData.features.length}
                                        >
                                            Deploy to Production
                                        </Button>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    );
}
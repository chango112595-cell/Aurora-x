import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CheckCircle, AlertCircle, GitBranch, Code2, Zap, Shield, TrendingUp } from 'lucide-react';

interface ComparisonItem {
    id: string;
    title: string;
    description: string;
    status: 'approved' | 'pending' | 'rejected';
    category: string;
}

export default function ComparisonDashboard() {
    const [approvedItems, setApprovedItems] = useState<Set<string>>(new Set());

    const handleApproval = (itemId: string, approved: boolean) => {
        const newApproved = new Set(approvedItems);
        if (approved) {
            newApproved.add(itemId);
        } else {
            newApproved.delete(itemId);
        }
        setApprovedItems(newApproved);
    };

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
                {/* Header */}
                <div className="mb-8 text-center">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-4">
                        Aurora-X Comparison Dashboard
                    </h1>
                    <p className="text-slate-300 text-lg">
                        Professional Git History Analysis & Feature Comparison
                    </p>
                </div>

                <Tabs defaultValue="overview" className="space-y-6">
                    <TabsList className="grid w-full grid-cols-6 bg-slate-800/50 backdrop-blur-sm">
                        <TabsTrigger value="overview" className="text-cyan-400">Overview</TabsTrigger>
                        <TabsTrigger value="branches" className="text-cyan-400">Branches</TabsTrigger>
                        <TabsTrigger value="features" className="text-cyan-400">Features</TabsTrigger>
                        <TabsTrigger value="improvements" className="text-cyan-400">Improvements</TabsTrigger>
                        <TabsTrigger value="diagnostics" className="text-cyan-400">Diagnostics</TabsTrigger>
                        <TabsTrigger value="approval" className="text-cyan-400">Approval</TabsTrigger>
                    </TabsList>

                    {/* Overview Tab */}
                    <TabsContent value="overview" className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                            <Card className="bg-slate-800/50 backdrop-blur-sm border-cyan-500/30">
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

                            <Card className="bg-slate-800/50 backdrop-blur-sm border-purple-500/30">
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

                            <Card className="bg-slate-800/50 backdrop-blur-sm border-green-500/30">
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

                            <Card className="bg-slate-800/50 backdrop-blur-sm border-yellow-500/30">
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

                            <Card className="bg-slate-800/50 backdrop-blur-sm border-blue-500/30">
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
                        <Card className="bg-slate-800/50 backdrop-blur-sm border-blue-500/30">
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
                        <Card className="bg-slate-800/50 backdrop-blur-sm border-cyan-500/30">
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
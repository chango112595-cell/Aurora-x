import { ErrorBoundary } from '@/components/error-boundary';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, ArrowRight } from "lucide-react";
import { Link } from "wouter";

export default function Library() {
  return (
    <div className="h-full overflow-auto bg-gradient-to-br from-background via-background to-primary/5">
      <div className="p-6 space-y-6 relative">
        {/* Futuristic grid background overlay */}
        <div className="absolute inset-0 opacity-10 pointer-events-none">
          <div className="absolute inset-0" style={{
            backgroundImage: `linear-gradient(rgba(6, 182, 212, 0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(6, 182, 212, 0.1) 1px, transparent 1px)`,
            backgroundSize: '50px 50px'
          }} />
        </div>

        {/* Animated glow orbs */}
        <div className="absolute top-20 right-20 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-pulse pointer-events-none" />
        <div className="absolute bottom-20 left-20 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse pointer-events-none" style={{ animationDelay: '1s' }} />

        <div className="relative z-10 max-w-2xl mx-auto text-center space-y-8">
          <div className="space-y-4">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-cyan-400 to-primary bg-clip-text text-transparent">
              Code Library
            </h1>
            <p className="text-muted-foreground text-lg">
              Aurora's synthesized code has been integrated into Luminar Nexus
            </p>
          </div>

          <Card className="border-2 border-primary/30 bg-primary/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 justify-center">
                <BookOpen className="h-6 w-6" />
                View Your Learning Corpus
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                All synthesized functions and learning data are now available in Luminar Nexus under the "Learning" tab, integrated with real-time monitoring and analytics.
              </p>
              <Link href="/luminar">
                <Button size="lg" className="w-full gap-2">
                  <span>Go to Luminar Nexus</span>
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
            <div className="p-4 rounded-lg border border-primary/20 bg-background/50">
              <h3 className="font-semibold mb-2">📚 Complete Corpus</h3>
              <p className="text-sm text-muted-foreground">Browse all synthesized functions with scores and test results</p>
            </div>
            <div className="p-4 rounded-lg border border-primary/20 bg-background/50">
              <h3 className="font-semibold mb-2">🔍 Full-Text Search</h3>
              <p className="text-sm text-muted-foreground">Search by function name or signature instantly</p>
            </div>
            <div className="p-4 rounded-lg border border-primary/20 bg-background/50">
              <h3 className="font-semibold mb-2">📊 Analytics</h3>
              <p className="text-sm text-muted-foreground">View metrics and performance of Aurora's learning</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

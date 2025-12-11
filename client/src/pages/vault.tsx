import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { Shield, Lock, Key, Clock, CheckCircle, AlertCircle, RefreshCw } from "lucide-react";

interface VaultRequest {
  ts: number;
  op: string;
  alias?: string;
  requester?: string;
  error?: string;
}

interface VaultHealth {
  ok: boolean;
  configured: boolean;
  hasMasterPassphrase: boolean;
  hasAdminKey: boolean;
  ts: number;
}

export default function VaultPage() {
  const { toast } = useToast();
  const [unlockAlias, setUnlockAlias] = useState("");
  const [requesterName, setRequesterName] = useState("");
  const [adminKey, setAdminKey] = useState(() => localStorage.getItem("aurora_admin_key") || "");

  useEffect(() => {
    localStorage.setItem("aurora_admin_key", adminKey);
  }, [adminKey]);

  const healthQuery = useQuery<VaultHealth>({
    queryKey: ["/api/vault/health"]
  });

  const requestsQuery = useQuery<{ requests: VaultRequest[] }>({
    queryKey: ["/api/vault/requests"],
    enabled: !!adminKey,
    refetchInterval: 10000
  });

  const requestUnlockMutation = useMutation({
    mutationFn: async (data: { alias: string; requester?: string }) => {
      const res = await fetch("/api/vault/unlock-request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      return res.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Unlock Requested",
        description: data.message || "Request submitted for approval."
      });
      setUnlockAlias("");
      setRequesterName("");
    },
    onError: () => {
      toast({
        title: "Request Failed",
        description: "Could not submit unlock request.",
        variant: "destructive"
      });
    }
  });

  const approveUnlockMutation = useMutation({
    mutationFn: async (alias: string) => {
      const res = await fetch("/api/vault/approve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": adminKey
        },
        body: JSON.stringify({ alias })
      });
      return res.json();
    },
    onSuccess: (data) => {
      if (data.ok) {
        toast({
          title: "Unlock Approved",
          description: `Secret '${data.alias}' has been decrypted.`
        });
      } else {
        toast({
          title: "Approval Failed",
          description: data.error || "Could not decrypt secret.",
          variant: "destructive"
        });
      }
    },
    onError: () => {
      toast({
        title: "Approval Failed",
        description: "Could not process approval request.",
        variant: "destructive"
      });
    }
  });

  const handleRequestUnlock = () => {
    if (!unlockAlias.trim()) {
      toast({
        title: "Missing Alias",
        description: "Please enter a secret alias.",
        variant: "destructive"
      });
      return;
    }
    requestUnlockMutation.mutate({
      alias: unlockAlias.trim(),
      requester: requesterName.trim() || undefined
    });
  };

  const handleApprove = (alias: string) => {
    if (!adminKey) {
      toast({
        title: "Admin Key Required",
        description: "Please enter your admin API key first.",
        variant: "destructive"
      });
      return;
    }
    approveUnlockMutation.mutate(alias);
  };

  const getOpIcon = (op: string) => {
    switch (op) {
      case "encrypt":
        return <Lock className="h-4 w-4 text-green-500" />;
      case "decrypt":
        return <Key className="h-4 w-4 text-blue-500" />;
      case "unlock_request":
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case "approved_unlock":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "decrypt_error":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Shield className="h-4 w-4 text-muted-foreground" />;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Shield className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold" data-testid="text-vault-title">ASE-∞ Vault</h1>
          <p className="text-muted-foreground">Multi-layer encrypted secret management</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Vault Status</CardTitle>
          </CardHeader>
          <CardContent>
            {healthQuery.isLoading ? (
              <div className="flex items-center gap-2">
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span className="text-sm">Checking...</span>
              </div>
            ) : healthQuery.data?.configured ? (
              <Badge variant="default" className="bg-green-600">
                <CheckCircle className="h-3 w-3 mr-1" />
                Configured
              </Badge>
            ) : (
              <Badge variant="destructive">
                <AlertCircle className="h-3 w-3 mr-1" />
                Not Configured
              </Badge>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Master Passphrase</CardTitle>
          </CardHeader>
          <CardContent>
            {healthQuery.data?.hasMasterPassphrase ? (
              <Badge variant="default" className="bg-green-600">Set</Badge>
            ) : (
              <Badge variant="outline">Not Set</Badge>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Admin Key</CardTitle>
          </CardHeader>
          <CardContent>
            {healthQuery.data?.hasAdminKey ? (
              <Badge variant="default" className="bg-green-600">Configured</Badge>
            ) : (
              <Badge variant="outline">Not Configured</Badge>
            )}
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="request" className="w-full">
        <TabsList>
          <TabsTrigger value="request" data-testid="tab-vault-request">Request Unlock</TabsTrigger>
          <TabsTrigger value="admin" data-testid="tab-vault-admin">Admin Approvals</TabsTrigger>
          <TabsTrigger value="log" data-testid="tab-vault-log">Operation Log</TabsTrigger>
        </TabsList>

        <TabsContent value="request" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Request Secret Unlock</CardTitle>
              <CardDescription>
                Request access to an encrypted secret. An admin must approve the request.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="alias">Secret Alias</Label>
                <Input
                  id="alias"
                  placeholder="e.g., discord_webhook, admin_api_key"
                  value={unlockAlias}
                  onChange={(e) => setUnlockAlias(e.target.value)}
                  data-testid="input-vault-alias"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="requester">Your Name (optional)</Label>
                <Input
                  id="requester"
                  placeholder="e.g., Aurora System"
                  value={requesterName}
                  onChange={(e) => setRequesterName(e.target.value)}
                  data-testid="input-vault-requester"
                />
              </div>
              <Button
                onClick={handleRequestUnlock}
                disabled={requestUnlockMutation.isPending}
                data-testid="button-vault-request"
              >
                {requestUnlockMutation.isPending ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Requesting...
                  </>
                ) : (
                  <>
                    <Lock className="h-4 w-4 mr-2" />
                    Request Unlock
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="admin" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Admin Authentication</CardTitle>
              <CardDescription>
                Enter your admin API key to view and approve unlock requests.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="adminKey">Admin API Key</Label>
                <Input
                  id="adminKey"
                  type="password"
                  placeholder="Enter admin API key"
                  value={adminKey}
                  onChange={(e) => setAdminKey(e.target.value)}
                  data-testid="input-vault-admin-key"
                />
              </div>
              <Button
                onClick={() => requestsQuery.refetch()}
                disabled={!adminKey}
                variant="outline"
                data-testid="button-vault-load"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Load Requests
              </Button>
            </CardContent>
          </Card>

          {adminKey && requestsQuery.data?.requests && (
            <Card>
              <CardHeader>
                <CardTitle>Pending Requests</CardTitle>
                <CardDescription>
                  {requestsQuery.data.requests.filter(r => r.op === "unlock_request").length} unlock request(s)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {requestsQuery.data.requests
                    .filter(r => r.op === "unlock_request")
                    .slice(0, 20)
                    .map((req, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between p-3 border rounded-lg"
                        data-testid={`row-vault-request-${i}`}
                      >
                        <div className="flex items-center gap-3">
                          {getOpIcon(req.op)}
                          <div>
                            <div className="font-medium">{req.alias}</div>
                            <div className="text-sm text-muted-foreground">
                              {req.requester || "Unknown"} - {new Date(req.ts).toLocaleString()}
                            </div>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          onClick={() => req.alias && handleApprove(req.alias)}
                          disabled={approveUnlockMutation.isPending}
                          data-testid={`button-approve-${i}`}
                        >
                          Approve
                        </Button>
                      </div>
                    ))}
                  {requestsQuery.data.requests.filter(r => r.op === "unlock_request").length === 0 && (
                    <div className="text-center text-muted-foreground py-8">
                      No pending unlock requests
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="log" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Operation Log</CardTitle>
              <CardDescription>
                Recent vault operations (requires admin key)
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!adminKey ? (
                <div className="text-center text-muted-foreground py-8">
                  Enter admin key to view operation log
                </div>
              ) : requestsQuery.isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin" />
                </div>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {requestsQuery.data?.requests?.slice(0, 50).map((req, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-3 p-2 border-b last:border-0"
                      data-testid={`row-vault-log-${i}`}
                    >
                      {getOpIcon(req.op)}
                      <div className="flex-1">
                        <span className="font-medium">{req.op}</span>
                        {req.alias && <span className="text-muted-foreground ml-2">({req.alias})</span>}
                        {req.error && <span className="text-red-500 ml-2">{req.error}</span>}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {new Date(req.ts).toLocaleString()}
                      </div>
                    </div>
                  ))}
                  {(!requestsQuery.data?.requests || requestsQuery.data.requests.length === 0) && (
                    <div className="text-center text-muted-foreground py-8">
                      No operations logged yet
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

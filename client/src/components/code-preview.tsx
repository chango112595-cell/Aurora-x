import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Copy, Download } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface CodePreviewProps {
  title?: string;
  code?: string;
  language?: string;
  score?: number;
}

export function CodePreview({ 
  title = "Generated Code",
  code = `def normalize_spaces(s: str) -> str:
    return ' '.join(s.split())

def tokenize(s: str) -> list[str]:
    return s.split()

def safe_int(s: str, default: int) -> int:
    try:
        return int(s)
    except ValueError:
        return default`,
  language = "python",
  score = 0.95
}: CodePreviewProps) {
  const { toast } = useToast();

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    toast({
      title: "Copied to clipboard",
      description: "Code has been copied successfully",
    });
  };

  const handleDownload = () => {
    const blob = new Blob([code], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `generated_code.${language}`;
    a.click();
    URL.revokeObjectURL(url);
    toast({
      title: "Downloaded",
      description: "Code has been downloaded successfully",
    });
  };

  return (
    <Card data-testid="card-code-preview">
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <CardTitle>{title}</CardTitle>
            <Badge variant="secondary">{language}</Badge>
          </div>
          <div className="flex items-center gap-2">
            <Badge className="bg-chart-2 text-white">Score: {score.toFixed(2)}</Badge>
            <Button variant="ghost" size="icon" onClick={handleCopy} data-testid="button-copy">
              <Copy className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={handleDownload} data-testid="button-download">
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <pre className="rounded-md bg-muted p-4 overflow-x-auto">
          <code className="text-sm font-mono" data-testid="code-content">{code}</code>
        </pre>
      </CardContent>
    </Card>
  );
}

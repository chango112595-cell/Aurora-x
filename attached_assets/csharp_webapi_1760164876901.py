
PROGRAM_CS = """using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Hosting;
using System;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/health", () => Results.Json(new { ok = true }));
app.MapPost("/echo", (Echo e) => Results.Json(e));

var port = Environment.GetEnvironmentVariable("PORT") ?? "5080";
app.Run($"http://0.0.0.0:{port}");

public record Echo(string Message);
"""

CS_PROJ = """<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
"""

def render_csharp_webapi(name: str) -> dict:
    folder = name or "Aurora.WebApi"
    return {"folder": folder, "files": {f"{folder}.csproj": CS_PROJ, "Program.cs": PROGRAM_CS}, "hint": "Run: PORT=5080 dotnet run"}

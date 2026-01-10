/**
 * Centralized configuration for Aurora server
 * Provides consistent host/port/URL management across all services
 */

const DEFAULT_HOST = process.env.AURORA_HOST || process.env.HOST || '0.0.0.0';
const DEFAULT_PORT = parseInt(process.env.PORT || process.env.AURORA_PORT || '5000', 10);
const DEFAULT_PROTOCOL = process.env.AURORA_PROTOCOL || (process.env.NODE_ENV === 'production' ? 'https' : 'http');

// For internal service communication (localhost)
const INTERNAL_HOST = process.env.AURORA_INTERNAL_HOST || '127.0.0.1';

// Base URL for public-facing endpoints
export function getBaseUrl(): string {
  if (process.env.BASE_URL) {
    return process.env.BASE_URL;
  }
  if (process.env.PUBLIC_BASE_URL) {
    return process.env.PUBLIC_BASE_URL;
  }
  // In production, should be set via BASE_URL
  // In development, use localhost
  const host = process.env.NODE_ENV === 'production' ? DEFAULT_HOST : INTERNAL_HOST;
  return `${DEFAULT_PROTOCOL}://${host}:${DEFAULT_PORT}`;
}

// Internal service URLs (for service-to-service communication)
export function getInternalUrl(port?: number, path = ''): string {
  const servicePort = port || DEFAULT_PORT;
  return `http://${INTERNAL_HOST}:${servicePort}${path}`;
}

// Aurora Nexus V3 API URL
export function getAuroraNexusUrl(): string {
  if (process.env.AURORA_NEXUS_URL) {
    return process.env.AURORA_NEXUS_URL;
  }
  const nexusPort = parseInt(process.env.AURORA_NEXUS_PORT || '5001', 10);
  return getInternalUrl(nexusPort);
}

// Luminar Nexus V2 URL
export function getLuminarUrl(): string {
  if (process.env.LUMINAR_URL) {
    return process.env.LUMINAR_URL;
  }
  const luminarPort = parseInt(process.env.LUMINAR_PORT || '8000', 10);
  return getInternalUrl(luminarPort);
}

// Memory Fabric URL
export function getMemoryFabricUrl(): string {
  if (process.env.MEMORY_FABRIC_URL) {
    return process.env.MEMORY_FABRIC_URL;
  }
  const memoryPort = parseInt(process.env.MEMORY_FABRIC_PORT || '5002', 10);
  return getInternalUrl(memoryPort);
}

// Memory Service URL
export function getMemoryServiceUrl(): string {
  if (process.env.MEMORY_SERVICE_URL) {
    return process.env.MEMORY_SERVICE_URL;
  }
  return getMemoryFabricUrl(); // Default to memory fabric
}

// Export host/port for direct use
export const config = {
  host: DEFAULT_HOST,
  port: DEFAULT_PORT,
  protocol: DEFAULT_PROTOCOL,
  internalHost: INTERNAL_HOST,
  baseUrl: getBaseUrl(),
  auroraNexusUrl: getAuroraNexusUrl(),
  luminarUrl: getLuminarUrl(),
  memoryFabricUrl: getMemoryFabricUrl(),
  memoryServiceUrl: getMemoryServiceUrl(),
};

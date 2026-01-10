/**
 * Aurora-X Security Validator
 *
 * Validates that insecure default secrets are not used in production.
 * Fails startup in production mode if defaults are detected.
 * Warns in development mode when defaults are used.
 * Checks both environment variables AND generated secret files.
 */

import fs from 'fs';
import path from 'path';

interface InsecureDefault {
  key: string;
  defaultValue: string;
  description: string;
  critical: boolean;
  secretFile?: string; // Path to secret file if auto-generated
}

const SECRETS_DIR = process.env.AURORA_SECRETS_DIR || path.join(process.cwd(), 'secrets');

const INSECURE_DEFAULTS: InsecureDefault[] = [
  {
    key: 'AURORA_API_KEY',
    defaultValue: 'dev-key-change-in-production',
    description: 'Aurora API authentication key',
    critical: true,
    secretFile: path.join(SECRETS_DIR, 'api_key')
  },
  {
    key: 'AURORA_ADMIN_KEY',
    defaultValue: 'aurora-admin-key',
    description: 'Aurora admin API key',
    critical: true
  },
  {
    key: 'JWT_SECRET',
    defaultValue: 'change-this-in-production-to-a-strong-secret',
    description: 'JWT signing secret',
    critical: true,
    secretFile: path.join(SECRETS_DIR, 'jwt_secret')
  },
  {
    key: 'ADMIN_PASSWORD',
    defaultValue: 'Alebec95!',
    description: 'Default admin user password',
    critical: true,
    secretFile: path.join(SECRETS_DIR, 'admin_password')
  },
  {
    key: 'AURORA_HEALTH_TOKEN',
    defaultValue: 'ok',
    description: 'Health check authentication token',
    critical: false
  },
  {
    key: 'AURORA_MASTER_PASSPHRASE',
    defaultValue: '',
    description: 'Vault master passphrase (empty is insecure)',
    critical: true
  }
];

interface ValidationResult {
  valid: boolean;
  criticalIssues: string[];
  warnings: string[];
}

function isSecureSecret(value: string, defaultValue: string): boolean {
  // If value is empty or matches default, it's insecure
  if (!value || value === defaultValue) {
    return false;
  }
  // If value is auto-generated (64+ hex chars for API keys, or long random strings), it's secure
  if (value.length >= 32 && /^[a-f0-9]+$/i.test(value)) {
    return true; // Hex-encoded secure key
  }
  // If value is significantly different from default and has reasonable length, consider it secure
  if (value.length >= 16 && value !== defaultValue) {
    return true;
  }
  return false;
}

function checkSecretFile(filePath: string | undefined, defaultValue: string): boolean {
  if (!filePath) {
    return false;
  }
  try {
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8').trim();
      return isSecureSecret(content, defaultValue);
    }
  } catch {
    // File doesn't exist or can't be read
  }
  return false;
}

export function validateSecurityDefaults(): ValidationResult {
  const isProduction = process.env.NODE_ENV === 'production';
  const criticalIssues: string[] = [];
  const warnings: string[] = [];

  for (const item of INSECURE_DEFAULTS) {
    const envValue = process.env[item.key];

    // Check if environment variable is set and secure
    const envIsSecure = envValue && isSecureSecret(envValue, item.defaultValue);

    // Check if secret file exists and contains secure value
    const fileIsSecure = checkSecretFile(item.secretFile, item.defaultValue);

    // If either env var or file is secure, we're good
    if (envIsSecure || fileIsSecure) {
      continue; // This secret is secure, skip to next
    }

    // If we get here, neither env var nor file has a secure value
    const isUsingDefault = !envValue || envValue === item.defaultValue;

    if (isUsingDefault) {
      const message = `${item.key}: ${item.description} is using insecure default value`;

      if (item.critical) {
        criticalIssues.push(message);
      } else {
        warnings.push(message);
      }
    }
  }

  return {
    valid: criticalIssues.length === 0,
    criticalIssues,
    warnings
  };
}

export function enforceSecurityAtStartup(): void {
  const isProduction = process.env.NODE_ENV === 'production';
  const result = validateSecurityDefaults();

  console.log('\n═══════════════════════════════════════════════════════════');
  console.log('🔐 AURORA-X SECURITY VALIDATION');
  console.log('═══════════════════════════════════════════════════════════');
  console.log(`Environment: ${isProduction ? 'PRODUCTION' : 'development'}`);
  console.log('');

  if (result.warnings.length > 0) {
    console.log('⚠️  WARNINGS:');
    for (const warning of result.warnings) {
      console.log(`   - ${warning}`);
    }
    console.log('');
  }

  if (result.criticalIssues.length > 0) {
    console.log('🚨 CRITICAL SECURITY ISSUES:');
    for (const issue of result.criticalIssues) {
      console.log(`   ❌ ${issue}`);
    }
    console.log('');

    if (isProduction) {
      console.log('═══════════════════════════════════════════════════════════');
      console.log('💀 FATAL: Cannot start in production with insecure defaults!');
      console.log('');
      console.log('To fix this, set secure values for the following environment variables:');
      for (const issue of result.criticalIssues) {
        const key = issue.split(':')[0];
        console.log(`   export ${key}="<your-secure-value>"`);
      }
      console.log('');
      console.log('Or use secrets management to configure these values securely.');
      console.log('═══════════════════════════════════════════════════════════\n');
      process.exit(1);
    } else {
      console.log('⚠️  DEVELOPMENT MODE: Allowing startup with insecure defaults.');
      console.log('   These MUST be configured before deploying to production!');
      console.log('');
    }
  }

  if (result.valid && result.warnings.length === 0) {
    console.log('✅ All security checks passed!');
  } else if (result.valid) {
    console.log('✅ Critical security checks passed (with warnings).');
  }

  console.log('═══════════════════════════════════════════════════════════\n');
}

export function isSecureForProduction(): boolean {
  const result = validateSecurityDefaults();
  return result.valid;
}

export { INSECURE_DEFAULTS };

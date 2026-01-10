/**
 * Notification System
 * Handles email and webhook notifications
 */

import nodemailer from 'nodemailer';
import { getBaseUrl } from './config';

// ══════════════════════════════════════════════════════════════
// Email Configuration
// ══════════════════════════════════════════════════════════════

let emailTransporter: nodemailer.Transporter | null = null;

// Initialize email transporter if credentials are provided
if (process.env.SENDGRID_API_KEY) {
  emailTransporter = nodemailer.createTransport({
    host: 'smtp.sendgrid.net',
    port: 587,
    auth: {
      user: 'apikey',
      pass: process.env.SENDGRID_API_KEY
    }
  });
  console.log('[Notifications] ✉️  SendGrid email configured');
} else if (process.env.RESEND_API_KEY) {
  emailTransporter = nodemailer.createTransport({
    host: 'smtp.resend.com',
    port: 587,
    auth: {
      user: 'resend',
      pass: process.env.RESEND_API_KEY
    }
  });
  console.log('[Notifications] ✉️  Resend email configured');
} else {
  console.log('[Notifications] ⚠️  No email service configured (set SENDGRID_API_KEY or RESEND_API_KEY)');
}

// ══════════════════════════════════════════════════════════════
// Email Functions
// ══════════════════════════════════════════════════════════════

export interface EmailOptions {
  to: string;
  subject: string;
  text?: string;
  html?: string;
  from?: string;
}

export async function sendEmail(options: EmailOptions): Promise<boolean> {
  if (!emailTransporter) {
    console.warn('[Notifications] Cannot send email - no email service configured');
    return false;
  }

  try {
    const defaultFrom = process.env.EMAIL_FROM || 'aurora@chango.dev';

    await emailTransporter.sendMail({
      from: options.from || defaultFrom,
      to: options.to,
      subject: options.subject,
      text: options.text,
      html: options.html
    });

    console.log('[Notifications] ✅ Email sent to:', options.to);
    return true;
  } catch (error: any) {
    console.error('[Notifications] ❌ Email error:', error.message);
    return false;
  }
}

// ══════════════════════════════════════════════════════════════
// Discord Webhook
// ══════════════════════════════════════════════════════════════

export interface DiscordMessage {
  content?: string;
  embeds?: Array<{
    title?: string;
    description?: string;
    color?: number;
    fields?: Array<{
      name: string;
      value: string;
      inline?: boolean;
    }>;
    timestamp?: string;
  }>;
}

export async function sendDiscordNotification(message: DiscordMessage): Promise<boolean> {
  const webhookUrl = process.env.DISCORD_WEBHOOK_URL;

  if (!webhookUrl) {
    console.warn('[Notifications] Cannot send Discord message - DISCORD_WEBHOOK_URL not set');
    return false;
  }

  try {
    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(message)
    });

    if (response.ok) {
      console.log('[Notifications] ✅ Discord notification sent');
      return true;
    } else {
      console.error('[Notifications] ❌ Discord webhook failed:', response.status);
      return false;
    }
  } catch (error: any) {
    console.error('[Notifications] ❌ Discord error:', error.message);
    return false;
  }
}

// ══════════════════════════════════════════════════════════════
// Notification Templates
// ══════════════════════════════════════════════════════════════

export async function notifyCodeSynthesisComplete(
  synthesisId: string,
  functionName: string,
  userEmail?: string
): Promise<void> {
  const baseUrl = getBaseUrl();
  // Send email if configured and user email provided
  if (userEmail && emailTransporter) {
    await sendEmail({
      to: userEmail,
      subject: `Code Synthesis Complete: ${functionName}`,
      html: `
        <h2>✅ Your code is ready!</h2>
        <p>Aurora has finished synthesizing your function: <strong>${functionName}</strong></p>
        <p>Synthesis ID: <code>${synthesisId}</code></p>
        <p><a href="${baseUrl}/dashboard">View in Dashboard</a></p>
      `,
      text: `Your code synthesis is complete!\n\nFunction: ${functionName}\nSynthesis ID: ${synthesisId}`
    });
  }

  // Send Discord notification if configured
  await sendDiscordNotification({
    embeds: [{
      title: '✅ Code Synthesis Complete',
      description: `Function **${functionName}** has been synthesized successfully!`,
      color: 0x00ff00, // Green
      fields: [
        {
          name: 'Synthesis ID',
          value: synthesisId,
          inline: true
        },
        {
          name: 'Function Name',
          value: functionName,
          inline: true
        }
      ],
      timestamp: new Date().toISOString()
    }]
  });
}

export async function notifySystemAlert(
  alertType: 'error' | 'warning' | 'info',
  title: string,
  message: string
): Promise<void> {
  const colors = {
    error: 0xff0000, // Red
    warning: 0xffa500, // Orange
    info: 0x00bfff // Blue
  };

  await sendDiscordNotification({
    embeds: [{
      title: `${alertType === 'error' ? '🚨' : alertType === 'warning' ? '⚠️' : 'ℹ️'} ${title}`,
      description: message,
      color: colors[alertType],
      timestamp: new Date().toISOString()
    }]
  });
}

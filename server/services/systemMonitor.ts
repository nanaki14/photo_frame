import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import type { SystemStatus } from '../../src/lib/types';
import { FileManager } from './fileManager';

export class SystemMonitor {
	private fileManager = new FileManager();

	/**
	 * Get complete system status
	 */
	async getSystemStatus(): Promise<SystemStatus> {
		try {
			const [battery, storage, display] = await Promise.all([
				this.getBatteryStatus(),
				this.getStorageStatus(),
				this.getDisplayStatus(),
			]);

			return {
				battery,
				storage,
				display,
			};
		} catch (error) {
			console.error('Error getting system status:', error);
			throw new Error('Failed to get system status');
		}
	}

	/**
	 * Get battery status
	 */
	async getBatteryStatus(): Promise<{ level: number; charging: boolean }> {
		try {
			// For Raspberry Pi, read battery information
			// This is a simplified implementation - actual implementation may vary based on hardware
			const result = await this.executeCommand(
				'cat /sys/class/power_supply/BAT*/capacity',
				{ fallback: true },
			);

			let level = 100; // Default to full if no battery detected
			let charging = false;

			if (result.success && result.output) {
				level = parseInt(result.output.trim(), 10) || 100;
			}

			// Check charging status
			const chargingResult = await this.executeCommand(
				'cat /sys/class/power_supply/BAT*/status',
				{ fallback: true },
			);
			if (chargingResult.success && chargingResult.output) {
				charging = chargingResult.output
					.trim()
					.toLowerCase()
					.includes('charging');
			}

			return {
				level: Math.max(0, Math.min(100, level)),
				charging,
			};
		} catch (error) {
			console.error('Error getting battery status:', error);
			// Return default values if battery monitoring fails
			return {
				level: 100,
				charging: false,
			};
		}
	}

	/**
	 * Get storage status
	 */
	async getStorageStatus(): Promise<{
		used: number;
		total: number;
		available: number;
	}> {
		try {
			// Get disk usage for the storage directory
			const storageDir = path.join(process.cwd(), 'storage');
			const result = await this.executeCommand(`df -B1 "${storageDir}"`);

			if (result.success && result.output) {
				const lines = result.output.trim().split('\n');
				if (lines.length > 1) {
					const parts = lines[1].split(/\s+/);
					if (parts.length >= 4) {
						const total = parseInt(parts[1], 10) || 0;
						const used = parseInt(parts[2], 10) || 0;
						const available = parseInt(parts[3], 10) || 0;

						return { used, total, available };
					}
				}
			}

			// Fallback: calculate from photo storage
			const stats = await this.fileManager.getStorageStats();
			return {
				used: stats.totalSize,
				total: stats.totalSize + 100 * 1024 * 1024, // Assume 100MB available
				available: 100 * 1024 * 1024,
			};
		} catch (error) {
			console.error('Error getting storage status:', error);
			// Return default values if storage monitoring fails
			return {
				used: 0,
				total: 1024 * 1024 * 1024, // 1GB
				available: 1024 * 1024 * 1024,
			};
		}
	}

	/**
	 * Get display status
	 */
	async getDisplayStatus(): Promise<{
		hasPhoto: boolean;
		lastUpdate: string;
		status: 'active' | 'updating' | 'error';
	}> {
		try {
			const statusFile = path.join(
				process.cwd(),
				'storage',
				'config',
				'display_status.json',
			);

			try {
				const data = await fs.readFile(statusFile, 'utf-8');
				const status = JSON.parse(data);

				return {
					hasPhoto: !!status.currentPhoto,
					lastUpdate: status.lastUpdate || new Date().toISOString(),
					status: status.status || 'active',
				};
			} catch {
				// If status file doesn't exist, check for current photo
				const currentPhoto = await this.fileManager.getCurrentPhoto();

				return {
					hasPhoto: !!currentPhoto,
					lastUpdate: new Date().toISOString(),
					status: 'active',
				};
			}
		} catch (error) {
			console.error('Error getting display status:', error);
			return {
				hasPhoto: false,
				lastUpdate: new Date().toISOString(),
				status: 'error',
			};
		}
	}

	/**
	 * Execute system command with timeout
	 */
	private async executeCommand(
		command: string,
		options: { timeout?: number; fallback?: boolean } = {},
	): Promise<{ success: boolean; output?: string; error?: string }> {
		return new Promise((resolve) => {
			const { timeout = 5000, fallback = false } = options;

			const process = spawn('sh', ['-c', command]);
			let output = '';
			let errorOutput = '';

			process.stdout.on('data', (data) => {
				output += data.toString();
			});

			process.stderr.on('data', (data) => {
				errorOutput += data.toString();
			});

			process.on('close', (code) => {
				if (code === 0) {
					resolve({ success: true, output: output.trim() });
				} else {
					if (fallback) {
						// For battery/charging commands, failure is acceptable
						resolve({ success: false, error: errorOutput.trim() });
					} else {
						resolve({
							success: false,
							error: errorOutput.trim() || `Command failed with code ${code}`,
						});
					}
				}
			});

			process.on('error', (error) => {
				if (fallback) {
					resolve({ success: false, error: error.message });
				} else {
					resolve({
						success: false,
						error: `Failed to execute command: ${error.message}`,
					});
				}
			});

			// Set timeout
			setTimeout(() => {
				process.kill();
				resolve({ success: false, error: 'Command timed out' });
			}, timeout);
		});
	}

	/**
	 * Get system uptime
	 */
	async getUptime(): Promise<number> {
		try {
			const result = await this.executeCommand('cat /proc/uptime');

			if (result.success && result.output) {
				const uptimeSeconds = parseFloat(result.output.split(' ')[0]);
				return Math.floor(uptimeSeconds);
			}

			return 0;
		} catch (error) {
			console.error('Error getting uptime:', error);
			return 0;
		}
	}

	/**
	 * Get CPU temperature (for Raspberry Pi)
	 */
	async getCPUTemperature(): Promise<number> {
		try {
			const result = await this.executeCommand(
				'cat /sys/class/thermal/thermal_zone0/temp',
				{ fallback: true },
			);

			if (result.success && result.output) {
				const temp = parseInt(result.output.trim(), 10);
				return Math.round(temp / 1000); // Convert from millidegrees to degrees
			}

			return 0;
		} catch (error) {
			console.error('Error getting CPU temperature:', error);
			return 0;
		}
	}

	/**
	 * Check if system is running on Raspberry Pi
	 */
	async isRaspberryPi(): Promise<boolean> {
		try {
			const result = await this.executeCommand('cat /proc/device-tree/model', {
				fallback: true,
			});

			if (result.success && result.output) {
				return result.output.toLowerCase().includes('raspberry pi');
			}

			return false;
		} catch (error) {
			return false;
		}
	}
}

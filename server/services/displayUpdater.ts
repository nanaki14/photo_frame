import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { FileManager } from './fileManager';

export class DisplayUpdater {
	private fileManager = new FileManager();
	private statusFile = path.join(
		process.cwd(),
		'storage',
		'config',
		'display_status.json',
	);
	private isUpdating = false;

	constructor() {
		this.ensureStatusFile();
	}

	/**
	 * Ensure display status file exists
	 */
	private async ensureStatusFile(): Promise<void> {
		try {
			await fs.access(this.statusFile);
		} catch {
			// File doesn't exist, create it
			const initialStatus = {
				isUpdating: false,
				lastUpdate: new Date().toISOString(),
				currentPhoto: null,
				status: 'active',
			};
			await fs.writeFile(
				this.statusFile,
				JSON.stringify(initialStatus, null, 2),
			);
		}
	}

	/**
	 * Update display status
	 */
	private async updateStatus(status: {
		isUpdating?: boolean;
		lastUpdate?: string;
		currentPhoto?: string | null;
		status?: 'active' | 'updating' | 'error';
	}): Promise<void> {
		try {
			let currentStatus = {};
			try {
				const data = await fs.readFile(this.statusFile, 'utf-8');
				currentStatus = JSON.parse(data);
			} catch {
				// Use empty object if file doesn't exist or is invalid
			}

			const newStatus = {
				...currentStatus,
				...status,
				lastUpdate: status.lastUpdate || new Date().toISOString(),
			};

			await fs.writeFile(this.statusFile, JSON.stringify(newStatus, null, 2));
		} catch (error) {
			console.error('Error updating display status:', error);
		}
	}

	/**
	 * Update display with specific photo
	 */
	async updateDisplay(
		photoId: string,
	): Promise<{ success: boolean; message: string }> {
		if (this.isUpdating) {
			return {
				success: false,
				message: 'Display update already in progress',
			};
		}

		try {
			this.isUpdating = true;
			await this.updateStatus({ isUpdating: true, status: 'updating' });

			// Get photo details
			const photo = await this.fileManager.getPhotoById(photoId);
			if (!photo) {
				throw new Error('Photo not found');
			}

			const photoPath = this.fileManager.getPhotoFilePath(photo.filename);

			// Verify file exists
			try {
				await fs.access(photoPath);
			} catch {
				throw new Error('Photo file not found');
			}

			// Call Python script to update display
			const result = await this.callPythonScript('update_display.py', [
				photoPath,
			]);

			if (result.success) {
				await this.updateStatus({
					isUpdating: false,
					currentPhoto: photoId,
					status: 'active',
				});

				// Set as current photo
				await this.fileManager.setCurrentPhoto(photoId);

				return {
					success: true,
					message: 'Display updated successfully',
				};
			} else {
				throw new Error(result.error || 'Python script execution failed');
			}
		} catch (error) {
			console.error('Error updating display:', error);

			await this.updateStatus({
				isUpdating: false,
				status: 'error',
			});

			return {
				success: false,
				message:
					error instanceof Error ? error.message : 'Failed to update display',
			};
		} finally {
			this.isUpdating = false;
		}
	}

	/**
	 * Get current update status
	 */
	async getUpdateStatus(): Promise<{
		isUpdating: boolean;
		lastUpdate: string;
		currentPhoto: string | null;
	}> {
		try {
			const data = await fs.readFile(this.statusFile, 'utf-8');
			const status = JSON.parse(data);

			return {
				isUpdating: status.isUpdating || false,
				lastUpdate: status.lastUpdate || new Date().toISOString(),
				currentPhoto: status.currentPhoto || null,
			};
		} catch (error) {
			console.error('Error getting update status:', error);
			return {
				isUpdating: false,
				lastUpdate: new Date().toISOString(),
				currentPhoto: null,
			};
		}
	}

	/**
	 * Call Python script with arguments
	 */
	private async callPythonScript(
		scriptName: string,
		args: string[],
	): Promise<{ success: boolean; output?: string; error?: string }> {
		return new Promise((resolve) => {
			const scriptPath = path.join(process.cwd(), 'display', scriptName);
			const pythonProcess = spawn('python3', [scriptPath, ...args]);

			let output = '';
			let errorOutput = '';

			pythonProcess.stdout.on('data', (data) => {
				output += data.toString();
			});

			pythonProcess.stderr.on('data', (data) => {
				errorOutput += data.toString();
			});

			pythonProcess.on('close', (code) => {
				if (code === 0) {
					resolve({ success: true, output: output.trim() });
				} else {
					resolve({
						success: false,
						error: errorOutput.trim() || `Script exited with code ${code}`,
					});
				}
			});

			pythonProcess.on('error', (error) => {
				resolve({
					success: false,
					error: `Failed to start Python script: ${error.message}`,
				});
			});

			// Set timeout for long-running scripts
			setTimeout(() => {
				pythonProcess.kill();
				resolve({
					success: false,
					error: 'Script execution timed out',
				});
			}, 30000); // 30 second timeout
		});
	}
}

import { Hono } from 'hono';
import type { ApiResponse, SystemStatus } from '../../src/lib/types';
import { SystemMonitor } from '../services/systemMonitor';

const app = new Hono();
const systemMonitor = new SystemMonitor();

// Get system status
app.get('/', async (c) => {
	try {
		const status = await systemMonitor.getSystemStatus();
		const response: ApiResponse<SystemStatus> = {
			success: true,
			data: status,
		};
		return c.json(response);
	} catch (error) {
		console.error('Error fetching system status:', error);
		return c.json(
			{
				success: false,
				error: 'Failed to fetch system status',
			},
			500,
		);
	}
});

// Get battery status
app.get('/battery', async (c) => {
	try {
		const batteryStatus = await systemMonitor.getBatteryStatus();
		const response: ApiResponse<{ level: number; charging: boolean }> = {
			success: true,
			data: batteryStatus,
		};
		return c.json(response);
	} catch (error) {
		console.error('Error fetching battery status:', error);
		return c.json(
			{
				success: false,
				error: 'Failed to fetch battery status',
			},
			500,
		);
	}
});

// Get storage status
app.get('/storage', async (c) => {
	try {
		const storageStatus = await systemMonitor.getStorageStatus();
		const response: ApiResponse<{
			used: number;
			total: number;
			available: number;
		}> = {
			success: true,
			data: storageStatus,
		};
		return c.json(response);
	} catch (error) {
		console.error('Error fetching storage status:', error);
		return c.json(
			{
				success: false,
				error: 'Failed to fetch storage status',
			},
			500,
		);
	}
});

// Get display status
app.get('/display', async (c) => {
	try {
		const displayStatus = await systemMonitor.getDisplayStatus();
		const response: ApiResponse<{
			hasPhoto: boolean;
			lastUpdate: string;
			status: 'active' | 'updating' | 'error';
		}> = {
			success: true,
			data: displayStatus,
		};
		return c.json(response);
	} catch (error) {
		console.error('Error fetching display status:', error);
		return c.json(
			{
				success: false,
				error: 'Failed to fetch display status',
			},
			500,
		);
	}
});

export default app;

import { Hono } from 'hono';
import type { ApiResponse } from '../../src/lib/types';
import { DisplayUpdater } from '../services/displayUpdater';

const app = new Hono();
const displayUpdater = new DisplayUpdater();

// Update display with specific photo
app.post('/update', async (c) => {
	try {
		const body = await c.req.json();
		const { photoId } = body;

		if (!photoId) {
			return c.json(
				{
					success: false,
					error: 'Photo ID is required',
				},
				400,
			);
		}

		const result = await displayUpdater.updateDisplay(photoId);

		const response: ApiResponse<{ success: boolean; message: string }> = {
			success: true,
			data: result,
		};

		return c.json(response);
	} catch (error) {
		console.error('Error updating display:', error);
		return c.json(
			{
				success: false,
				error: 'Failed to update display',
			},
			500,
		);
	}
});

// Get display update status
app.get('/status', async (c) => {
	try {
		const status = await displayUpdater.getUpdateStatus();

		const response: ApiResponse<{
			isUpdating: boolean;
			lastUpdate: string;
			currentPhoto: string | null;
		}> = {
			success: true,
			data: status,
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

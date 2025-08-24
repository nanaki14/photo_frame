import { Hono } from 'hono';
import type { ApiResponse, Photo } from '../../src/lib/types';
import { DisplayUpdater } from '../services/displayUpdater';
import { FileManager } from '../services/fileManager';
import * as imageProcessor from '../services/imageProcessor';

const app = new Hono();
const fileManager = new FileManager();
const displayUpdater = new DisplayUpdater();

// Get current photo (single photo management)
app.get('/', async (c) => {
	try {
		const currentPhoto = await fileManager.getCurrentPhoto();
		const response: ApiResponse<Photo | null> = {
			success: true,
			data: currentPhoto,
		};
		return c.json(response);
	} catch (error) {
		console.error('Error fetching current photo:', error);
		return c.json(
			{
				success: false,
				error: 'Failed to fetch current photo',
			},
			500,
		);
	}
});

// Upload new photo
app.post('/', async (c) => {
	try {
		const body = await c.req.parseBody();
		const file = body['photo'] as File;

		if (!file) {
			return c.json(
				{
					success: false,
					error: 'No photo file provided',
				},
				400,
			);
		}

		// Validate file type (JPEG only)
		if (file.type !== 'image/jpeg') {
			return c.json(
				{
					success: false,
					error: 'Invalid file type. Only JPEG files are allowed.',
				},
				400,
			);
		}

		// Additional JPEG validation using imageProcessor
		const isValidJpeg = await imageProcessor.validateImage(file);
		if (!isValidJpeg) {
			return c.json(
				{
					success: false,
					error: 'Invalid JPEG file or corrupted image.',
				},
				400,
			);
		}

		// Validate file size (10MB limit)
		const maxSize = 10 * 1024 * 1024; // 10MB
		if (file.size > maxSize) {
			return c.json(
				{
					success: false,
					error: 'File size too large. Maximum 10MB allowed.',
				},
				400,
			);
		}

		// Process and save the image
		const processedImage = await imageProcessor.processImage(file);
		const savedPhoto = await fileManager.savePhoto(processedImage, file.name);

		// Update display immediately (single photo management - no ID needed)
		await displayUpdater.updateDisplay('current');

		const response: ApiResponse<Photo> = {
			success: true,
			data: savedPhoto,
		};

		return c.json(response, 201);
	} catch (error) {
		console.error('Error uploading photo:', error);
		return c.json(
			{
				success: false,
				error: 'Failed to upload photo',
			},
			500,
		);
	}
});

// Delete current photo (single photo management)
app.delete('/', async (c) => {
	try {
		// Delete the current photo (ID is ignored in single photo management)
		const deleted = await fileManager.deletePhoto('current');

		if (!deleted) {
			return c.json(
				{
					success: false,
					error: 'No photo to delete',
				},
				404,
			);
		}

		const response: ApiResponse<{ success: boolean }> = {
			success: true,
			data: { success: true },
		};

		return c.json(response);
	} catch (error) {
		console.error('Error deleting photo:', error);
		return c.json(
			{
				success: false,
				error: 'Failed to delete photo',
			},
			500,
		);
	}
});

export default app;

import { serve } from '@hono/node-server';
import { serveStatic } from '@hono/node-server/serve-static';
import { exec } from 'child_process';
import fs from 'fs/promises';
import { Hono } from 'hono';
import path from 'path';
import sharp from 'sharp';
import { promisify } from 'util';

const execAsync = promisify(exec);

const app = new Hono();

// Live reload functionality for development using file watching
const isDevelopment = process.env.NODE_ENV !== 'production';
let reloadClients: Set<any> = new Set();

if (isDevelopment) {
	// SSE endpoint for live reload
	app.get('/dev/reload', async (c) => {
		const headers = new Headers({
			'Content-Type': 'text/event-stream',
			'Cache-Control': 'no-cache',
			'Connection': 'keep-alive',
			'Access-Control-Allow-Origin': '*',
		});

		const encoder = new TextEncoder();
		const stream = new ReadableStream({
			start(controller) {
				// Add client to set
				const client = { controller };
				reloadClients.add(client);

				// Send initial connection message
				controller.enqueue(encoder.encode('data: connected\n\n'));

				// Remove client when connection closes
				const cleanup = () => {
					reloadClients.delete(client);
				};

				// Store cleanup function
				client.cleanup = cleanup;
			},
		});

		return new Response(stream, { headers });
	});

	// Watch for file changes in dist directory
	const { watch } = require('fs');
	const distPath = path.join(process.cwd(), 'src', 'dist');

	watch(distPath, { recursive: true }, (eventType: string, filename: string) => {
		if (filename && (
			filename.endsWith('.js') ||
			filename.endsWith('.html') ||
			filename.endsWith('.css')
		)) {
			console.log(`🔄 Triggering browser reload for: ${filename}`);
			const encoder = new TextEncoder();
			reloadClients.forEach(client => {
				try {
					client.controller.enqueue(encoder.encode('data: reload\n\n'));
				} catch (e) {
					// Client disconnected
					reloadClients.delete(client);
				}
			});
		}
	});
}

// Configuration
const UPLOAD_DIR = path.join(process.cwd(), 'uploads');
const DISPLAY_SCRIPT = path.join(process.cwd(), 'display', 'update_display.py');
const TARGET_WIDTH = 800;
const TARGET_HEIGHT = 480;
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

// Performance optimizations for Raspberry Pi Zero 2 WH
const isProduction = process.env.NODE_ENV === 'production';
const isPi = process.platform === 'linux' && process.arch === 'arm';

// Optimize Sharp settings for Pi Zero 2 WH
const SHARP_OPTIONS = {
	// Use single thread on Pi Zero to avoid memory issues
	concurrency: isPi ? 1 : require('os').cpus().length,
	// Limit memory usage
	limitInputPixels: isPi ? 50 * 1024 * 1024 : undefined, // 50MP limit on Pi
	// Use less memory for caching
	cache: isPi ? { memory: 16, files: 0 } : undefined,
};

// Apply Sharp settings
if (isPi) {
	sharp.cache(SHARP_OPTIONS.cache);
	sharp.concurrency(SHARP_OPTIONS.concurrency);
	// Note: limitInputPixels is set per-instance in sharp() constructor
}

// Ensure upload directory exists
async function ensureUploadDir() {
	try {
		await fs.access(UPLOAD_DIR);
	} catch {
		await fs.mkdir(UPLOAD_DIR, { recursive: true });
	}
}

// Initialize upload directory
ensureUploadDir();

// Static file serving for uploads
app.use(
	'/uploads/*',
	serveStatic({
		root: './',
		rewriteRequestPath: (path) => path,
	}),
);

// Static file serving for React app (built version)
app.use(
	'/*',
	serveStatic({
		root: './dist',
		index: 'index.html',
		rewriteRequestPath: (path) => {
			// Serve index.html for non-API routes, but not for static assets
			if (
				!path.startsWith('/api') &&
				!path.startsWith('/uploads') &&
				!path.includes('.') &&
				path !== '/'
			) {
				return '/index.html';
			}
			return path;
		},
	}),
);

// Photo upload endpoint
app.post('/api/photo', async (c) => {
	try {
		const body = await c.req.formData();
		const file = body.get('photo') as File;

		if (!file) {
			return c.json({ success: false, error: 'No file provided' }, 400);
		}

		// Validate file type (JPEG only)
		if (file.type !== 'image/jpeg') {
			return c.json(
				{ success: false, error: 'Only JPEG files are allowed' },
				400,
			);
		}

		// Validate file size
		if (file.size > MAX_FILE_SIZE) {
			return c.json({ success: false, error: 'File size too large' }, 400);
		}

		// Remove existing photo
		try {
			const files = await fs.readdir(UPLOAD_DIR);
			for (const existingFile of files) {
				if (existingFile.endsWith('.jpg') || existingFile.endsWith('.jpeg')) {
					await fs.unlink(path.join(UPLOAD_DIR, existingFile));
				}
			}
		} catch (error) {
			console.log('No existing files to remove or error removing:', error);
		}

		// Generate filename (fixed name)
		const filename = `photo.jpg`;
		const filepath = path.join(UPLOAD_DIR, filename);

		// Convert File to Buffer
		const buffer = Buffer.from(await file.arrayBuffer());

		// Process image with Sharp (resize and optimize for Waveshare E Ink Spectra 6)
		// Use streaming approach for better memory efficiency on Pi
		// Note: The Floyd-Steinberg dithering is applied in display_manager.py
		const sharpInstance = sharp(buffer, {
			// Limit memory usage for Pi Zero 2 WH
			limitInputPixels: isPi ? 50 * 1024 * 1024 : undefined,
			sequentialRead: true, // Better for single-core Pi Zero
		});

		// CRITICAL FIX: Convert to RGB explicitly FIRST before any color operations
		// Some JPEGs might be in other color spaces
		let processStream = sharpInstance
			.toColorspace('srgb')  // Ensure sRGB color space
			.resize(TARGET_WIDTH, TARGET_HEIGHT, {
				fit: 'contain',
				background: { r: 255, g: 255, b: 255 },
				// Use faster algorithm on Pi
				kernel: isPi ? 'nearest' : 'lanczos3',
			});

		// Add back color enhancements one by one
		// Start with modulate ONLY (no negate, no sharpen)
		const processedBuffer = await processStream
			.modulate({
				brightness: 1.0,
				saturation: 3.0,  // Maximum saturation for color visibility
				hue: 0,
			})
			.jpeg({
				quality: 100,  // MAXIMUM quality
				progressive: false,
				optimiseScans: false,
			})
			.toBuffer();

		// Save processed image
		await fs.writeFile(filepath, processedBuffer);

		// Get image metadata
		const metadata = await sharp(processedBuffer).metadata();

		// Update display by calling Python script
		try {
			await execAsync(`python3 ${DISPLAY_SCRIPT} ${filepath}`);
		} catch (error) {
			console.error('Display update failed:', error);
			// Don't fail the upload if display update fails
		}

		const uploadedAt = new Date().toISOString();

		return c.json({
			success: true,
			filename,
			uploadedAt,
			width: metadata.width || TARGET_WIDTH,
			height: metadata.height || TARGET_HEIGHT,
		});
	} catch (error) {
		console.error('Upload error:', error);
		return c.json(
			{
				success: false,
				error: error instanceof Error ? error.message : 'Upload failed',
			},
			500,
		);
	}
});

// Get current photo
app.get('/api/photo', async (c) => {
	try {
		const files = await fs.readdir(UPLOAD_DIR);
		const photoFile = files.find(
			(file) => file.endsWith('.jpg') || file.endsWith('.jpeg'),
		);

		if (!photoFile) {
			return c.json({ success: true, data: null });
		}

		const filepath = path.join(UPLOAD_DIR, photoFile);
		const stats = await fs.stat(filepath);
		const metadata = await sharp(filepath).metadata();

		const photo = {
			filename: photoFile,
			originalName: photoFile,
			size: stats.size,
			width: metadata.width || 0,
			height: metadata.height || 0,
			uploadedAt: stats.mtime.toISOString(),
		};

		return c.json({ success: true, data: photo });
	} catch (error) {
		console.error('Get photo error:', error);
		return c.json(
			{
				success: false,
				error: error instanceof Error ? error.message : 'Failed to get photo',
			},
			500,
		);
	}
});

// Delete current photo
app.delete('/api/photo', async (c) => {
	try {
		const files = await fs.readdir(UPLOAD_DIR);
		let deleted = false;

		for (const file of files) {
			if (file.endsWith('.jpg') || file.endsWith('.jpeg')) {
				await fs.unlink(path.join(UPLOAD_DIR, file));
				deleted = true;
			}
		}

		// Clear display
		try {
			await execAsync(`python3 ${DISPLAY_SCRIPT}`);
		} catch (error) {
			console.error('Display clear failed:', error);
		}

		return c.json({ success: true, data: { success: deleted } });
	} catch (error) {
		console.error('Delete photo error:', error);
		return c.json(
			{
				success: false,
				error:
					error instanceof Error ? error.message : 'Failed to delete photo',
			},
			500,
		);
	}
});

// Get system status
app.get('/api/status', async (c) => {
	try {
		// Check if photo exists
		const files = await fs.readdir(UPLOAD_DIR);
		const hasPhoto = files.some(
			(file) => file.endsWith('.jpg') || file.endsWith('.jpeg'),
		);

		let lastUpdate = '';
		if (hasPhoto) {
			const photoFile = files.find(
				(file) => file.endsWith('.jpg') || file.endsWith('.jpeg'),
			);
			if (photoFile) {
				const stats = await fs.stat(path.join(UPLOAD_DIR, photoFile));
				lastUpdate = stats.mtime.toISOString();
			}
		}

		const status = {
			battery: {
				level: 100, // Mock data - would need actual battery monitoring
				charging: false,
			},
			storage: {
				used: 0, // Mock data - would calculate actual usage
				total: 1000000000, // 1GB mock
				available: 1000000000,
			},
			display: {
				hasPhoto,
				lastUpdate,
				status: 'active' as const,
			},
		};

		return c.json({ success: true, data: status });
	} catch (error) {
		console.error('Get status error:', error);
		return c.json(
			{
				success: false,
				error: error instanceof Error ? error.message : 'Failed to get status',
			},
			500,
		);
	}
});

export default app;

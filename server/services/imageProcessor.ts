import sharp from 'sharp';

// Local image processing configuration interface
interface ImageProcessingConfig {
	targetWidth: number;
	targetHeight: number;
	quality: number;
}

const defaultConfig: ImageProcessingConfig = {
	targetWidth: 800, // Waveshare 7.3inch e-ink display width
	targetHeight: 480, // Waveshare 7.3inch e-ink display height
	quality: 90, // JPEG quality for processed images
};

let currentConfig = { ...defaultConfig };

/**
 * Process uploaded image for e-ink display optimization
 */
export async function processImage(file: File): Promise<{
	buffer: Buffer;
	metadata: {
		width: number;
		height: number;
		format: string;
		size: number;
	};
}> {
	try {
		// Convert File to Buffer
		const arrayBuffer = await file.arrayBuffer();
		const inputBuffer = Buffer.from(arrayBuffer);

		// Process image with Sharp
		const processedImage = sharp(inputBuffer)
			.resize(currentConfig.targetWidth, currentConfig.targetHeight, {
				fit: 'inside', // Maintain aspect ratio
				withoutEnlargement: true, // Don't enlarge smaller images
				background: { r: 255, g: 255, b: 255, alpha: 1 }, // White background
			})
			.grayscale() // Convert to grayscale for e-ink
			.jpeg({
				quality: currentConfig.quality,
				progressive: false, // Better for e-ink displays
				mozjpeg: true, // Better compression
			});

		const buffer = await processedImage.toBuffer();
		const metadata = await sharp(buffer).metadata();

		return {
			buffer,
			metadata: {
				width: metadata.width || 0,
				height: metadata.height || 0,
				format: metadata.format || 'jpeg',
				size: buffer.length,
			},
		};
	} catch (error) {
		console.error('Error processing image:', error);
		throw new Error('Failed to process image');
	}
}

/**
 * Create thumbnail for web interface
 */
export async function createThumbnail(
	file: File,
	size: number = 200,
): Promise<Buffer> {
	try {
		const arrayBuffer = await file.arrayBuffer();
		const inputBuffer = Buffer.from(arrayBuffer);

		const thumbnail = await sharp(inputBuffer)
			.resize(size, size, {
				fit: 'cover',
				position: 'center',
			})
			.jpeg({
				quality: 80,
				progressive: true,
			})
			.toBuffer();

		return thumbnail;
	} catch (error) {
		console.error('Error creating thumbnail:', error);
		throw new Error('Failed to create thumbnail');
	}
}

/**
 * Optimize image specifically for e-ink display characteristics
 */
export async function optimizeForEInk(buffer: Buffer): Promise<Buffer> {
	try {
		// E-ink specific optimizations
		const optimized = await sharp(buffer)
			// Increase contrast for better e-ink visibility
			.linear(1.2, -(128 * 1.2) + 128)
			// Apply slight sharpening
			.sharpen(1, 1, 0.5)
			// Ensure white background
			.flatten({ background: { r: 255, g: 255, b: 255 } })
			.jpeg({
				quality: 95,
				progressive: false,
			})
			.toBuffer();

		return optimized;
	} catch (error) {
		console.error('Error optimizing for e-ink:', error);
		throw new Error('Failed to optimize image for e-ink display');
	}
}

/**
 * Validate image file (JPEG only)
 */
export async function validateImage(file: File): Promise<boolean> {
	try {
		// Check MIME type first
		if (file.type !== 'image/jpeg') {
			return false;
		}

		const arrayBuffer = await file.arrayBuffer();
		const buffer = Buffer.from(arrayBuffer);

		const metadata = await sharp(buffer).metadata();

		// Check if it's a valid image
		if (!metadata.width || !metadata.height) {
			return false;
		}

		// Ensure format is JPEG
		if (metadata.format !== 'jpeg') {
			return false;
		}

		return true;
	} catch (error) {
		console.error('Error validating image:', error);
		return false;
	}
}

/**
 * Get image dimensions without full processing
 */
export async function getImageDimensions(
	file: File,
): Promise<{ width: number; height: number }> {
	try {
		const arrayBuffer = await file.arrayBuffer();
		const buffer = Buffer.from(arrayBuffer);

		const metadata = await sharp(buffer).metadata();

		return {
			width: metadata.width || 0,
			height: metadata.height || 0,
		};
	} catch (error) {
		console.error('Error getting image dimensions:', error);
		throw new Error('Failed to get image dimensions');
	}
}

/**
 * Update processing configuration
 */
export function updateConfig(config: Partial<ImageProcessingConfig>): void {
	currentConfig = { ...currentConfig, ...config };
}

/**
 * Get current configuration
 */
export function getConfig(): ImageProcessingConfig {
	return { ...currentConfig };
}

/**
 * Reset configuration to defaults
 */
export function resetConfig(): void {
	currentConfig = { ...defaultConfig };
}

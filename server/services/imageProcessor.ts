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
	quality: 95, // High quality for e-ink color accuracy
};

let currentConfig = { ...defaultConfig };

/**
 * Process uploaded image for Waveshare 7.3inch e-ink color display optimization
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

		// Process image with Sharp for Waveshare 7.3inch e-ink color display
		const processedImage = sharp(inputBuffer)
			.resize(currentConfig.targetWidth, currentConfig.targetHeight, {
				fit: 'inside', // Maintain aspect ratio
				withoutEnlargement: true, // Don't enlarge smaller images
				background: { r: 255, g: 255, b: 255, alpha: 1 }, // White background
			})
			// Optimize for e-ink color display characteristics
			.modulate({
				brightness: 1.1, // Higher brightness for e-ink visibility
				saturation: 0.9, // Slightly reduce saturation for better e-ink reproduction
			})
			// Apply sharpening for better e-ink clarity
			.sharpen(1.0, 0.5, 0.5)
			.jpeg({
				quality: currentConfig.quality,
				progressive: false, // Disable progressive for e-ink
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
 * Optimize image for Waveshare 7.3inch e-ink color display characteristics
 */
export async function optimizeForEInkColorDisplay(
	buffer: Buffer,
): Promise<Buffer> {
	try {
		// E-ink color display optimizations
		const optimized = await sharp(buffer)
			// Enhance contrast and reduce saturation for e-ink
			.modulate({
				brightness: 1.1, // Higher brightness for e-ink visibility
				saturation: 0.9, // Slightly reduce saturation for better e-ink reproduction
			})
			// Apply sharpening for better e-ink clarity
			.sharpen(1.0, 0.5, 0.5)
			.jpeg({
				quality: 95,
				progressive: false, // E-ink displays don't benefit from progressive
			})
			.toBuffer();

		return optimized;
	} catch (error) {
		console.error('Error optimizing for e-ink color display:', error);
		throw new Error('Failed to optimize image for e-ink color display');
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

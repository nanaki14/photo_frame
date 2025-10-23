import { promises as fs } from 'fs';
import path from 'path';
import type { Photo } from '../../src/lib/types';

export class FileManager {
	private photosDir = path.join(process.cwd(), 'storage', 'photos');
	private thumbnailsDir = path.join(process.cwd(), 'storage', 'thumbnails');
	private metadataFile = path.join(
		process.cwd(),
		'storage',
		'config',
		'photos.json',
	);
	private currentPhotoFile = path.join(
		process.cwd(),
		'storage',
		'config',
		'current.json',
	);

	constructor() {
		this.ensureDirectories();
	}

	/**
	 * Ensure required directories exist
	 */
	private async ensureDirectories(): Promise<void> {
		try {
			await fs.mkdir(this.photosDir, { recursive: true });
			await fs.mkdir(this.thumbnailsDir, { recursive: true });
			await fs.mkdir(path.dirname(this.metadataFile), { recursive: true });
		} catch (error) {
			console.error('Error creating directories:', error);
		}
	}

	/**
	 * Load photo metadata from file (single photo)
	 */
	private async loadPhotoMetadata(): Promise<Photo | null> {
		try {
			const data = await fs.readFile(this.metadataFile, 'utf-8');
			return JSON.parse(data);
		} catch (error) {
			// File doesn't exist or is invalid, return null
			return null;
		}
	}

	/**
	 * Load photos metadata from file (legacy - for backwards compatibility)
	 */
	private async loadPhotosMetadata(): Promise<Photo[]> {
		try {
			const photo = await this.loadPhotoMetadata();
			return photo ? [photo] : [];
		} catch (error) {
			// File doesn't exist or is invalid, return empty array
			return [];
		}
	}

	/**
	 * Save a processed photo (overwrites existing photo for single photo management)
	 */
	async savePhoto(
		processedImage: { buffer: Buffer; metadata: any },
		originalName: string,
	): Promise<Photo> {
		try {
			// For single photo management, use a fixed filename
			const filename = 'current_photo.jpg';
			const filePath = path.join(this.photosDir, filename);

			// Remove existing photo first
			try {
				await fs.unlink(filePath);
			} catch {
				// No existing photo, continue
			}

			// Save the processed image
			await fs.writeFile(filePath, processedImage.buffer);

			// Create photo metadata
			const photo: Photo = {
				filename,
				originalName: 'photo',
				size: processedImage.buffer.length,
				width: processedImage.metadata.width,
				height: processedImage.metadata.height,
				uploadedAt: new Date().toISOString(),
			};

			// For single photo management, save as single photo metadata
			await fs.writeFile(this.metadataFile, JSON.stringify(photo, null, 2));

			return photo;
		} catch (error) {
			console.error('Error saving photo:', error);
			throw new Error('Failed to save photo');
		}
	}

	/**
	 * Get current photo (single photo management)
	 */
	async getAllPhotos(): Promise<Photo[]> {
		try {
			const photo = await this.loadPhotoMetadata();
			return photo ? [photo] : [];
		} catch (error) {
			console.error('Error getting photo:', error);
			throw new Error('Failed to get photo');
		}
	}

	/**
	 * Get current photo (ID parameter ignored in single photo management)
	 */
	async getPhotoById(id: string): Promise<Photo | null> {
		try {
			return await this.loadPhotoMetadata();
		} catch (error) {
			console.error('Error getting photo:', error);
			throw new Error('Failed to get photo');
		}
	}

	/**
	 * Delete current photo (ID parameter ignored in single photo management)
	 */
	async deletePhoto(id: string): Promise<boolean> {
		try {
			const photo = await this.loadPhotoMetadata();

			if (!photo) {
				return false;
			}

			const filePath = path.join(this.photosDir, photo.filename);
			const thumbnailPath = path.join(this.thumbnailsDir, photo.filename);

			// Remove files
			try {
				await fs.unlink(filePath);
			} catch (error) {
				// File might not exist, continue
			}

			try {
				await fs.unlink(thumbnailPath);
			} catch (error) {
				// Thumbnail might not exist, continue
			}

			// Remove metadata file
			try {
				await fs.unlink(this.metadataFile);
			} catch (error) {
				// Metadata file might not exist, continue
			}

			// Clear current photo
			await this.clearCurrentPhoto();

			return true;
		} catch (error) {
			console.error('Error deleting photo:', error);
			throw new Error('Failed to delete photo');
		}
	}

	/**
	 * Get current displayed photo
	 */
	async getCurrentPhoto(): Promise<Photo | null> {
		try {
			// In single photo management, the current photo is the only photo
			return await this.loadPhotoMetadata();
		} catch (error) {
			// No photo exists
			return null;
		}
	}

	/**
	 * Set current displayed photo (simplified for single photo management)
	 */
	async setCurrentPhoto(photoId: string): Promise<void> {
		try {
			// In single photo management, the current photo is always the only photo
			// This method is kept for compatibility but doesn't need to do anything
			const photo = await this.loadPhotoMetadata();
			if (!photo) {
				throw new Error('No photo found');
			}
			// Photo is already current by definition
		} catch (error) {
			console.error('Error setting current photo:', error);
			throw new Error('Failed to set current photo');
		}
	}

	/**
	 * Clear current photo
	 */
	async clearCurrentPhoto(): Promise<void> {
		try {
			await fs.unlink(this.currentPhotoFile);
		} catch (error) {
			// File might not exist, which is fine
		}
	}

	/**
	 * Get photo file path
	 */
	getPhotoFilePath(filename: string): string {
		return path.join(this.photosDir, filename);
	}

	/**
	 * Get thumbnail file path
	 */
	getThumbnailFilePath(filename: string): string {
		return path.join(this.thumbnailsDir, filename);
	}

	/**
	 * Save thumbnail
	 */
	async saveThumbnail(
		filename: string,
		thumbnailBuffer: Buffer,
	): Promise<void> {
		try {
			const thumbnailPath = path.join(this.thumbnailsDir, filename);
			await fs.writeFile(thumbnailPath, thumbnailBuffer);
		} catch (error) {
			console.error('Error saving thumbnail:', error);
			throw new Error('Failed to save thumbnail');
		}
	}

	/**
	 * Get storage statistics for single photo
	 */
	async getStorageStats(): Promise<{
		totalPhotos: number;
		totalSize: number;
	}> {
		try {
			const photo = await this.loadPhotoMetadata();

			return {
				totalPhotos: photo ? 1 : 0,
				totalSize: photo ? photo.size : 0,
			};
		} catch (error) {
			console.error('Error getting storage stats:', error);
			throw new Error('Failed to get storage statistics');
		}
	}
}

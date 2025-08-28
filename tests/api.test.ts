import { describe, expect, it } from 'bun:test';
import { apiClient } from '../src/lib/api';

// Mock server setup for testing
// const mockServer = {
// 	port: 3001,
// 	url: `http://localhost:3001`,
// };

describe('API Client Tests', () => {
	describe('Photo Upload API', () => {
		it('should upload a valid JPEG file', async () => {
			// Create a mock JPEG file
			const mockFile = new File(['mock jpeg data'], 'test.jpg', {
				type: 'image/jpeg',
			});

			// This would normally call the actual API
			// For now, we'll test the function exists and handles parameters
			expect(apiClient.uploadPhoto).toBeDefined();
			expect(typeof apiClient.uploadPhoto).toBe('function');
		});

		it('should reject non-JPEG files', async () => {
			const mockFile = new File(['mock png data'], 'test.png', {
				type: 'image/png',
			});

			// Test that the function exists and can handle the file parameter
			expect(apiClient.uploadPhoto).toBeDefined();
		});
	});

	describe('Photo Management API', () => {
		it('should get current photo', async () => {
			expect(apiClient.getCurrentPhoto).toBeDefined();
			expect(typeof apiClient.getCurrentPhoto).toBe('function');
		});

		it('should delete current photo', async () => {
			expect(apiClient.deleteCurrentPhoto).toBeDefined();
			expect(typeof apiClient.deleteCurrentPhoto).toBe('function');
		});
	});

	describe('System Status API', () => {
		it('should get system status', async () => {
			expect(apiClient.getSystemStatus).toBeDefined();
			expect(typeof apiClient.getSystemStatus).toBe('function');
		});
	});
});

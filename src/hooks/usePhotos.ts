import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/api';
import type { Photo, PhotoUploadResponse } from '../lib/types';

// Query key constants
export const QUERY_KEYS = {
	currentPhoto: ['photo'] as const,
};

// Get current displayed photo
export function useCurrentPhoto() {
	return useQuery({
		queryKey: QUERY_KEYS.currentPhoto,
		queryFn: async () => {
			const response = await apiClient.getCurrentPhoto();
			if (!response.success) {
				throw new Error(response.error || 'Failed to fetch current photo');
			}
			return response.data;
		},
		refetchInterval: 30 * 1000, // Refetch every 30 seconds
	});
}

// Upload photo (replaces current photo)
export function usePhotoUpload() {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: async (file: File): Promise<PhotoUploadResponse> => {
			const response = await apiClient.uploadPhoto(file);
			if (!response.success || !response.data) {
				throw new Error(response.error || 'Failed to upload photo');
			}
			return response.data;
		},
		onSuccess: () => {
			// Invalidate and refetch current photo after successful upload
			queryClient.invalidateQueries({ queryKey: QUERY_KEYS.currentPhoto });
		},
	});
}

// Delete current photo
export function usePhotoDelete() {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: async () => {
			const response = await apiClient.deleteCurrentPhoto();
			if (!response.success) {
				throw new Error(response.error || 'Failed to delete photo');
			}
			return response.data;
		},
		onSuccess: () => {
			// Invalidate current photo query after successful deletion
			queryClient.invalidateQueries({ queryKey: QUERY_KEYS.currentPhoto });
		},
	});
}

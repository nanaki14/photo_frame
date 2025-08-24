import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../lib/api';
import type { SystemStatus } from '../lib/types';

// Query key constants
export const STATUS_QUERY_KEYS = {
	systemStatus: ['status'] as const,
	batteryStatus: ['status', 'battery'] as const,
	storageStatus: ['status', 'storage'] as const,
	displayStatus: ['status', 'display'] as const,
};

// Get complete system status
export function useSystemStatus() {
	return useQuery({
		queryKey: STATUS_QUERY_KEYS.systemStatus,
		queryFn: async () => {
			const response = await apiClient.getSystemStatus();
			if (!response.success || !response.data) {
				throw new Error(response.error || 'Failed to fetch system status');
			}
			return response.data;
		},
		refetchInterval: 60 * 1000, // Refetch every minute
		staleTime: 30 * 1000, // 30 seconds stale time
	});
}

// Get battery status only
export function useBatteryStatus() {
	const { data: systemStatus, ...rest } = useSystemStatus();

	return {
		data: systemStatus?.battery,
		...rest,
	};
}

// Get storage status only
export function useStorageStatus() {
	const { data: systemStatus, ...rest } = useSystemStatus();

	return {
		data: systemStatus?.storage,
		...rest,
	};
}

// Get display status only
export function useDisplayStatus() {
	const { data: systemStatus, ...rest } = useSystemStatus();

	return {
		data: systemStatus?.display,
		...rest,
	};
}

// Hook for monitoring if display is currently updating
export function useDisplayUpdateStatus() {
	return useQuery({
		queryKey: ['display', 'updateStatus'] as const,
		queryFn: async () => {
			const response = await apiClient.getSystemStatus();
			if (!response.success || !response.data) {
				throw new Error(response.error || 'Failed to fetch display status');
			}
			return {
				isUpdating: response.data.display.status === 'updating',
				status: response.data.display.status,
				lastUpdate: response.data.display.lastUpdate,
				hasPhoto: response.data.display.hasPhoto,
			};
		},
		refetchInterval: 2 * 1000, // Refetch every 2 seconds when display is updating
		staleTime: 1 * 1000, // 1 second stale time for real-time updates
	});
}

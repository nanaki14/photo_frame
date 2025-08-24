import type {
	ApiResponse,
	Photo,
	PhotoUploadResponse,
	SystemStatus,
} from './types';

const baseUrl = '';

async function request<T>(
	endpoint: string,
	options: RequestInit = {},
): Promise<ApiResponse<T>> {
	try {
		const response = await fetch(`${baseUrl}/api${endpoint}`, {
			headers: {
				'Content-Type': 'application/json',
				...options.headers,
			},
			...options,
		});

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const data = await response.json();
		return { success: true, data };
	} catch (error) {
		console.error('API request failed:', error);
		return {
			success: false,
			error: error instanceof Error ? error.message : 'Unknown error',
		};
	}
}

// 写真関連API（単一写真管理）
export async function uploadPhoto(
	file: File,
): Promise<ApiResponse<PhotoUploadResponse>> {
	const formData = new FormData();
	formData.append('photo', file);

	try {
		const response = await fetch(`${baseUrl}/api/photo`, {
			method: 'POST',
			body: formData,
		});

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const data = await response.json();
		return { success: true, data };
	} catch (error) {
		console.error('Photo upload failed:', error);
		return {
			success: false,
			error: error instanceof Error ? error.message : 'Upload failed',
		};
	}
}

export async function getCurrentPhoto(): Promise<ApiResponse<Photo | null>> {
	return request<Photo | null>('/photo');
}

export async function deleteCurrentPhoto(): Promise<
	ApiResponse<{ success: boolean }>
> {
	return request<{ success: boolean }>('/photo', {
		method: 'DELETE',
	});
}

// システム状態API
export async function getSystemStatus(): Promise<ApiResponse<SystemStatus>> {
	return request<SystemStatus>('/status');
}

// APIクライアントオブジェクト（後方互換性のため）
export const apiClient = {
	uploadPhoto,
	getCurrentPhoto,
	deleteCurrentPhoto,
	getSystemStatus,
};

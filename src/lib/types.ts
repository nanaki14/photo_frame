// 写真関連の型定義（単一写真管理）
export interface Photo {
	filename: string;
	originalName: string;
	size: number;
	width: number;
	height: number;
	uploadedAt: string;
}

// システム状態の型定義
export interface SystemStatus {
	battery: {
		level: number;
		charging: boolean;
	};
	storage: {
		used: number;
		total: number;
		available: number;
	};
	display: {
		hasPhoto: boolean;
		lastUpdate: string;
		status: 'active' | 'updating' | 'error';
	};
}

// API レスポンスの型定義
export interface ApiResponse<T> {
	success: boolean;
	data?: T;
	error?: string;
}

export interface PhotoUploadResponse {
	success: boolean;
	filename: string;
	uploadedAt: string;
}

// ディスプレイの状態
export type DisplayStatus = 'active' | 'updating' | 'error';

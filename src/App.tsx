import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Trash2, Upload } from 'lucide-react';
import React from 'react';
import { PhotoUploader } from './components/PhotoUploader';
import { Button } from './components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { useCurrentPhoto, usePhotoDelete } from './hooks/usePhotos';
import { useDisplayUpdateStatus, useSystemStatus } from './hooks/useStatus';
import './index.css';

// Create a client
const queryClient = new QueryClient({
	defaultOptions: {
		queries: {
			retry: 1,
			staleTime: 5 * 60 * 1000, // 5 minutes
		},
	},
});

function MainApp() {
	const { data: currentPhoto, isLoading: photoLoading } = useCurrentPhoto();
	const { data: updateStatus } = useDisplayUpdateStatus();
	const { data: systemStatus } = useSystemStatus();
	const deletePhoto = usePhotoDelete();

	const handleDeletePhoto = async () => {
		if (window.confirm('Are you sure you want to delete this photo?')) {
			try {
				await deletePhoto.mutateAsync();
			} catch (error) {
				console.error('Failed to delete photo:', error);
			}
		}
	};

	return (
		<div className="container mx-auto space-y-6 p-6">
			<div className="text-center">
				<h1 className="font-bold text-3xl text-gray-900">
					Digital Photo Frame
				</h1>
				<p className="mt-2 text-gray-600">
					Upload photos to display on your e-ink screen
				</p>
			</div>

			<div className="grid grid-cols-1 gap-4 md:grid-cols-3">
				<Card>
					<CardHeader className="pb-2">
						<CardTitle className="font-medium text-sm">
							Display Status
						</CardTitle>
					</CardHeader>
					<CardContent>
						<div className="space-y-2">
							<div className="flex items-center justify-between">
								<span className="text-gray-600 text-sm">Status:</span>
								<span
									className={`font-medium text-sm ${
										updateStatus?.status === 'updating'
											? 'text-blue-600'
											: updateStatus?.status === 'error'
												? 'text-red-600'
												: 'text-green-600'
									}`}
								>
									{updateStatus?.status === 'updating'
										? 'Updating...'
										: updateStatus?.status === 'error'
											? 'Error'
											: 'Active'}
								</span>
							</div>
							{currentPhoto ? (
								<div className="text-gray-500 text-xs">
									Current: {currentPhoto.originalName}
								</div>
							) : (
								<div className="text-gray-400 text-xs">No photo displayed</div>
							)}
						</div>
					</CardContent>
				</Card>

				<Card>
					<CardHeader className="pb-2">
						<CardTitle className="font-medium text-sm">Battery</CardTitle>
					</CardHeader>
					<CardContent>
						<div className="space-y-2">
							<div className="flex items-center justify-between">
								<span className="text-gray-600 text-sm">Level:</span>
								<span className="font-medium text-sm">
									{systemStatus?.battery.level ?? 0}%
								</span>
							</div>
							<div className="h-2 w-full rounded-full bg-gray-200">
								<div
									className={`h-2 rounded-full ${
										(systemStatus?.battery.level ?? 0) > 20
											? 'bg-green-500'
											: 'bg-red-500'
									}`}
									style={{ width: `${systemStatus?.battery.level ?? 0}%` }}
								/>
							</div>
							{systemStatus?.battery.charging && (
								<div className="text-blue-600 text-xs">Charging</div>
							)}
						</div>
					</CardContent>
				</Card>

				<Card>
					<CardHeader className="pb-2">
						<CardTitle className="font-medium text-sm">Storage</CardTitle>
					</CardHeader>
					<CardContent>
						<div className="space-y-2">
							<div className="flex items-center justify-between">
								<span className="text-gray-600 text-sm">Used:</span>
								<span className="font-medium text-sm">
									{systemStatus
										? `${Math.round(systemStatus.storage.used / (1024 * 1024))}MB`
										: '0MB'}
								</span>
							</div>
							<div className="h-2 w-full rounded-full bg-gray-200">
								<div
									className="h-2 rounded-full bg-blue-500"
									style={{
										width: systemStatus
											? `${Math.min(100, (systemStatus.storage.used / systemStatus.storage.total) * 100)}%`
											: '0%',
									}}
								/>
							</div>
						</div>
					</CardContent>
				</Card>
			</div>

			<div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
				<Card>
					<CardHeader>
						<CardTitle>Upload New Photo</CardTitle>
					</CardHeader>
					<CardContent>
						<PhotoUploader />
					</CardContent>
				</Card>

				<Card>
					<CardHeader>
						<CardTitle>Current Display</CardTitle>
					</CardHeader>
					<CardContent>
						{photoLoading ? (
							<div className="flex h-48 items-center justify-center rounded-lg bg-gray-100">
								<div className="text-gray-500">Loading...</div>
							</div>
						) : currentPhoto ? (
							<div className="space-y-4">
								<div className="flex aspect-video items-center justify-center overflow-hidden rounded-lg bg-gray-100">
									<img
										src={`/uploads/${currentPhoto.filename}`}
										alt={currentPhoto.originalName}
										className="max-h-full max-w-full object-contain"
									/>
								</div>
								<div className="text-gray-600 text-sm">
									<div className="font-medium">{currentPhoto.originalName}</div>
									<div className="text-xs">
										{currentPhoto.width}×{currentPhoto.height} •
										{Math.round(currentPhoto.size / 1024)}KB •
										{new Date(currentPhoto.uploadedAt).toLocaleDateString()}
									</div>
								</div>
								<Button
									variant="outline"
									size="sm"
									onClick={handleDeletePhoto}
									disabled={deletePhoto.isPending}
									className="w-full text-red-600 hover:text-red-800"
								>
									<Trash2 className="mr-2 h-4 w-4" />
									{deletePhoto.isPending ? 'Deleting...' : 'Delete Photo'}
								</Button>
							</div>
						) : (
							<div className="flex h-48 flex-col items-center justify-center rounded-lg bg-gray-100">
								<Upload className="mb-2 h-8 w-8 text-gray-400" />
								<div className="mb-2 text-gray-500">No photo displayed</div>
								<div className="text-gray-400 text-xs">
									Upload a JPEG photo to get started
								</div>
							</div>
						)}
					</CardContent>
				</Card>
			</div>
		</div>
	);
}

export function App() {
	return (
		<QueryClientProvider client={queryClient}>
			<div className="min-h-screen bg-gray-50">
				<MainApp />
			</div>
			<ReactQueryDevtools initialIsOpen={false} />
		</QueryClientProvider>
	);
}

export default App;

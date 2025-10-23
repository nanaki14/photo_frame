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
				<h1 className="font-bold text-2xl text-gray-900">
					Digital Photo Frame 🖼️
				</h1>
			</div>

			<div className="grid grid-cols-1 gap-6">
				<Card className="rounded">
					<CardHeader>
						<CardTitle>Upload New Photo 📷</CardTitle>
					</CardHeader>
					<CardContent>
						<PhotoUploader />
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

import { AlertCircle, Check, Upload, X } from 'lucide-react';
import type React from 'react';
import { useRef, useState } from 'react';
import { usePhotoUpload } from '../hooks/usePhotos';
import { ImageCropper } from './ImageCropper';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';

export function PhotoUploader() {
	const [dragActive, setDragActive] = useState(false);
	const [uploadProgress, setUploadProgress] = useState<number | null>(null);
	const [selectedImage, setSelectedImage] = useState<string | null>(null);
	const [originalFile, setOriginalFile] = useState<File | null>(null);
	const fileInputRef = useRef<HTMLInputElement>(null);
	const uploadPhoto = usePhotoUpload();

	const handleDrag = (e: React.DragEvent) => {
		e.preventDefault();
		e.stopPropagation();
		if (e.type === 'dragenter' || e.type === 'dragover') {
			setDragActive(true);
		} else if (e.type === 'dragleave') {
			setDragActive(false);
		}
	};

	const handleDrop = (e: React.DragEvent) => {
		e.preventDefault();
		e.stopPropagation();
		setDragActive(false);

		if (e.dataTransfer.files && e.dataTransfer.files[0]) {
			handleFile(e.dataTransfer.files[0]);
		}
	};

	const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
		if (e.target.files && e.target.files[0]) {
			handleFile(e.target.files[0]);
		}
	};

	const handleFile = async (file: File) => {
		// Validate file type (JPEG only)
		if (file.type !== 'image/jpeg') {
			alert('Please select a JPEG image file only.');
			return;
		}

		// Validate file size (10MB limit)
		const maxSize = 10 * 1024 * 1024; // 10MB
		if (file.size > maxSize) {
			alert('File size too large. Maximum 10MB allowed.');
			return;
		}

		// Store original file and show cropper
		setOriginalFile(file);
		const imageUrl = URL.createObjectURL(file);
		setSelectedImage(imageUrl);
	};

	const handleCropComplete = async (croppedImageBlob: Blob) => {
		try {
			// Convert blob to File for upload
			const croppedFile = new File(
				[croppedImageBlob],
				originalFile?.name || 'cropped-image.jpg',
				{
					type: 'image/jpeg',
				},
			);

			setUploadProgress(0);
			setSelectedImage(null);
			setOriginalFile(null);

			// Simulate upload progress
			const progressInterval = setInterval(() => {
				setUploadProgress((prev) => {
					if (prev === null) return 0;
					if (prev >= 90) return prev; // Stop at 90% until actual upload completes
					return prev + 10;
				});
			}, 200);

			await uploadPhoto.mutateAsync(croppedFile);

			clearInterval(progressInterval);
			setUploadProgress(100);

			// Reset after success
			setTimeout(() => {
				setUploadProgress(null);
				if (fileInputRef.current) {
					fileInputRef.current.value = '';
				}
			}, 2000);
		} catch (error) {
			setUploadProgress(null);
			console.error('Upload failed:', error);
		}
	};

	const handleCropCancel = () => {
		if (selectedImage) {
			URL.revokeObjectURL(selectedImage);
		}
		setSelectedImage(null);
		setOriginalFile(null);
		if (fileInputRef.current) {
			fileInputRef.current.value = '';
		}
	};

	const handleButtonClick = () => {
		fileInputRef.current?.click();
	};

	const getStatusIcon = () => {
		if (uploadPhoto.isError) {
			return <AlertCircle className="h-5 w-5 text-red-500" />;
		}
		if (uploadProgress === 100) {
			return <Check className="h-5 w-5 text-green-500" />;
		}
		return <Upload className="h-5 w-5" />;
	};

	const getStatusText = () => {
		if (uploadPhoto.isError) {
			return 'Upload failed. Please try again.';
		}
		if (uploadProgress === 100) {
			return 'Photo uploaded and displayed successfully!';
		}
		if (uploadPhoto.isPending) {
			return `Uploading and updating display... ${uploadProgress}%`;
		}
		return 'Drop your JPEG photo here or click to browse';
	};

	return (
		<>
			{selectedImage && (
				<ImageCropper
					imageSrc={selectedImage}
					onCropComplete={handleCropComplete}
					onCancel={handleCropCancel}
				/>
			)}

			<div className="space-y-4">
				<Card
					className={`cursor-pointer border-2 border-dashed transition-colors ${
						dragActive
							? 'border-blue-500 bg-blue-50'
							: uploadPhoto.isError
								? 'border-red-300 bg-red-50'
								: uploadProgress === 100
									? 'border-green-300 bg-green-50'
									: 'border-gray-300 hover:border-gray-400'
					}`}
					onDragEnter={handleDrag}
					onDragLeave={handleDrag}
					onDragOver={handleDrag}
					onDrop={handleDrop}
					onClick={handleButtonClick}
				>
					<CardContent className="flex flex-col items-center justify-center px-6 py-12">
						<div className="mb-4">{getStatusIcon()}</div>

						<p className="mb-4 text-center text-gray-600">{getStatusText()}</p>

						{uploadProgress !== null && uploadProgress < 100 && (
							<div className="mb-4 w-full max-w-xs">
								<div className="h-2 w-full rounded-full bg-gray-200">
									<div
										className="h-2 rounded-full bg-blue-500 transition-all duration-300"
										style={{ width: `${uploadProgress}%` }}
									/>
								</div>
							</div>
						)}

						<div className="text-center text-gray-500 text-sm">
							<p>Supported format: JPEG only</p>
							<p>Maximum file size: 10MB</p>
							<p className="mt-2 text-gray-400 text-xs">
								Images will be cropped to fit the e-ink display (5:3 ratio)
							</p>
						</div>

						<Button
							variant="outline"
							className="mt-4"
							disabled={uploadPhoto.isPending || selectedImage !== null}
							onClick={(e) => {
								e.stopPropagation();
								handleButtonClick();
							}}
						>
							{uploadPhoto.isPending ? 'Uploading...' : 'Choose JPEG File'}
						</Button>
					</CardContent>
				</Card>

				<input
					ref={fileInputRef}
					type="file"
					accept="image/jpeg"
					onChange={handleFileInput}
					className="hidden"
				/>

				{uploadPhoto.isError && (
					<div className="text-center text-red-600 text-sm">
						{uploadPhoto.error?.message || 'Upload failed. Please try again.'}
					</div>
				)}
			</div>
		</>
	);
}

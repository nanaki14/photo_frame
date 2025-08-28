import React, { useCallback, useId, useState } from 'react';
import Cropper from 'react-easy-crop';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

// Define types locally to avoid import issues
interface Area {
	x: number;
	y: number;
	width: number;
	height: number;
}

interface Point {
	x: number;
	y: number;
}

interface ImageCropperProps {
	imageSrc: string;
	onCropComplete: (croppedImageBlob: Blob) => void;
	onCancel: () => void;
}

// Display aspect ratio: 800×480 = 5:3
const DISPLAY_ASPECT_RATIO = 800 / 480;

export function ImageCropper({
	imageSrc,
	onCropComplete,
	onCancel,
}: ImageCropperProps) {
	const [crop, setCrop] = useState<Point>({ x: 0, y: 0 });
	const [zoom, setZoom] = useState(1);
	const [croppedAreaPixels, setCroppedAreaPixels] = useState<Area | null>(null);
	const [isProcessing, setIsProcessing] = useState(false);
	const sliderId = useId();

	const onCropCompleteCallback = useCallback(
		(croppedArea: Area, croppedAreaPixels: Area) => {
			setCroppedAreaPixels(croppedAreaPixels);
		},
		[],
	);

	const createCroppedImage = useCallback(async () => {
		if (!croppedAreaPixels) return;

		setIsProcessing(true);

		try {
			const canvas = document.createElement('canvas');
			const ctx = canvas.getContext('2d');

			if (!ctx) {
				throw new Error('Failed to get canvas context');
			}

			const image = new Image();
			image.crossOrigin = 'anonymous';

			await new Promise((resolve, reject) => {
				image.onload = resolve;
				image.onerror = reject;
				image.src = imageSrc;
			});

			// Set canvas size to cropped area
			canvas.width = croppedAreaPixels.width;
			canvas.height = croppedAreaPixels.height;

			// Draw the cropped image
			ctx.drawImage(
				image,
				croppedAreaPixels.x,
				croppedAreaPixels.y,
				croppedAreaPixels.width,
				croppedAreaPixels.height,
				0,
				0,
				croppedAreaPixels.width,
				croppedAreaPixels.height,
			);

			// Convert canvas to blob
			canvas.toBlob(
				(blob) => {
					if (blob) {
						onCropComplete(blob);
					}
				},
				'image/jpeg',
				0.95,
			);
		} catch (error) {
			console.error('Error creating cropped image:', error);
			alert('Failed to crop image. Please try again.');
		} finally {
			setIsProcessing(false);
		}
	}, [croppedAreaPixels, imageSrc, onCropComplete]);

	return (
		<div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
			<Card className="mx-4 w-full max-w-4xl">
				<CardHeader>
					<CardTitle>Crop Image for Display</CardTitle>
					<p className="text-gray-600 text-sm">
						Crop your image to fit the e-ink display (5:3 aspect ratio)
					</p>
				</CardHeader>
				<CardContent className="space-y-4">
					<div className="relative h-96 w-full">
						<Cropper
							image={imageSrc}
							crop={crop}
							zoom={zoom}
							aspect={DISPLAY_ASPECT_RATIO}
							onCropChange={setCrop}
							onCropComplete={onCropCompleteCallback}
							onZoomChange={setZoom}
							showGrid={true}
							cropShape="rect"
							style={{
								containerStyle: {
									backgroundColor: '#f3f4f6',
									borderRadius: '0.5rem',
								},
							}}
						/>
					</div>

					<div className="space-y-2">
						<label
							htmlFor={sliderId}
							className="block font-medium text-gray-700 text-sm"
						>
							Zoom: {Math.round(zoom * 100)}%
						</label>
						<input
							id={sliderId}
							type="range"
							value={zoom}
							min={1}
							max={3}
							step={0.1}
							onChange={(e) => setZoom(Number(e.target.value))}
							className="w-full"
						/>
					</div>

					<div className="flex justify-end space-x-3">
						<Button
							variant="outline"
							onClick={onCancel}
							disabled={isProcessing}
						>
							Cancel
						</Button>
						<Button
							onClick={createCroppedImage}
							disabled={isProcessing || !croppedAreaPixels}
						>
							{isProcessing ? 'Processing...' : 'Apply Crop'}
						</Button>
					</div>
				</CardContent>
			</Card>
		</div>
	);
}

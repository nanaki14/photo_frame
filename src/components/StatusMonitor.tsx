import { AlertTriangle, Battery, HardDrive, Wifi } from 'lucide-react';
import React from 'react';
import { useSystemStatus } from '../hooks/useStatus';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

export function StatusMonitor() {
	const { data: status, isLoading, error } = useSystemStatus();

	if (isLoading) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>System Monitor</CardTitle>
				</CardHeader>
				<CardContent>
					<div className="text-center text-gray-500">
						Loading system status...
					</div>
				</CardContent>
			</Card>
		);
	}

	if (error) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>System Monitor</CardTitle>
				</CardHeader>
				<CardContent>
					<div className="flex items-center gap-2 text-red-600">
						<AlertTriangle className="h-4 w-4" />
						<span className="text-sm">Unable to load system status</span>
					</div>
				</CardContent>
			</Card>
		);
	}

	if (!status) {
		return null;
	}

	return (
		<Card>
			<CardHeader>
				<CardTitle>System Monitor</CardTitle>
			</CardHeader>
			<CardContent>
				<div className="space-y-4">
					{/* Battery Status */}
					<div className="flex items-center justify-between">
						<div className="flex items-center gap-2">
							<Battery
								className={`h-4 w-4 ${status.battery.charging ? 'text-green-500' : 'text-gray-600'}`}
							/>
							<span className="font-medium text-sm">Battery</span>
						</div>
						<div className="text-right">
							<div className="font-medium text-sm">{status.battery.level}%</div>
							{status.battery.charging && (
								<div className="text-green-600 text-xs">Charging</div>
							)}
						</div>
					</div>

					{/* Storage Status */}
					<div className="flex items-center justify-between">
						<div className="flex items-center gap-2">
							<HardDrive className="h-4 w-4 text-gray-600" />
							<span className="font-medium text-sm">Storage</span>
						</div>
						<div className="text-right">
							<div className="font-medium text-sm">
								{Math.round(status.storage.used / (1024 * 1024))}MB used
							</div>
							<div className="text-gray-500 text-xs">
								of {Math.round(status.storage.total / (1024 * 1024))}MB
							</div>
						</div>
					</div>

					{/* Display Status */}
					<div className="flex items-center justify-between">
						<div className="flex items-center gap-2">
							<div
								className={`h-3 w-3 rounded-full ${
									status.display.status === 'active'
										? 'bg-green-500'
										: status.display.status === 'updating'
											? 'bg-blue-500'
											: 'bg-red-500'
								}`}
							/>
							<span className="font-medium text-sm">Display</span>
						</div>
						<div className="text-right">
							<div className="font-medium text-sm capitalize">
								{status.display.status}
							</div>
							<div className="text-gray-500 text-xs">
								{status.display.hasPhoto ? 'Photo displayed' : 'No photo'}
							</div>
						</div>
					</div>

					{/* Last Update */}
					<div className="border-t pt-2">
						<div className="text-gray-500 text-xs">
							Last updated:{' '}
							{new Date(status.display.lastUpdate).toLocaleTimeString()}
						</div>
					</div>
				</div>
			</CardContent>
		</Card>
	);
}

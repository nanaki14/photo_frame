import { serve } from '@hono/node-server';
import { serveStatic } from '@hono/node-server/serve-static';
import fs from 'fs';
import path from 'path';
import app from './server/app';

// Serve static files (React app)
app.use(
	'/*',
	serveStatic({
		root: './src',
		index: 'index.html',
		rewriteRequestPath: (path) => {
			// Serve index.html for non-API routes
			if (!path.startsWith('/api') && !path.startsWith('/uploads')) {
				return '/index.html';
			}
			return path;
		},
	}),
);

const port = process.env.PORT ? parseInt(process.env.PORT) : 3000;

serve({
	fetch: app.fetch,
	port,
});

console.log(
	`🚀 Digital Photo Frame Server running at http://localhost:${port}`,
);
console.log(`📸 Upload photos via web interface`);
console.log(`🖼️  Display integration ready`);

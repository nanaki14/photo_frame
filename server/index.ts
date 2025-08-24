import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { serveStatic } from 'hono/bun';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import displayRoutes from './routes/display';
// Import route handlers
import photoRoutes from './routes/photos';
import statusRoutes from './routes/status';

const app = new Hono();

// Middleware
app.use('*', logger());
app.use(
	'*',
	cors({
		origin: ['http://localhost:3000', 'http://127.0.0.1:3000'],
		allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
		allowHeaders: ['Content-Type', 'Authorization'],
	}),
);

// Serve static files (uploaded photos and thumbnails)
app.use('/storage/*', serveStatic({ root: './storage' }));

// Serve React app static files
app.use('/assets/*', serveStatic({ root: './src' }));

// API Routes
app.route('/api/photos', photoRoutes);
app.route('/api/status', statusRoutes);
app.route('/api/display', displayRoutes);

// Health check endpoint
app.get('/api/health', (c) => {
	return c.json({
		status: 'ok',
		timestamp: new Date().toISOString(),
		version: '1.0.0',
	});
});

// Serve React app for all other routes (SPA routing)
app.get('*', serveStatic({ path: './src/index.html' }));

const port = process.env.PORT || 3001;

console.log(`🚀 Photo Frame Server starting on port ${port}`);

export default {
	port,
	fetch: app.fetch,
};

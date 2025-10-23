import app from './server/app';

const port = process.env.PORT ? parseInt(process.env.PORT) : 3000;
const isDevelopment = process.env.NODE_ENV !== 'production';

// Use Bun's built-in server with proper TypeScript support
export default {
	port,
	fetch: app.fetch,
	development: isDevelopment,
};

console.log(
	`🚀 Digital Photo Frame Server running at http://localhost:${port}`,
);
console.log(`📸 Upload photos via web interface`);
console.log(`🖼️  Display integration ready`);

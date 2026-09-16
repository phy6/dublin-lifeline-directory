import adapter from '@sveltejs/adapter-static';

export default {
	compilerOptions: {
		runes: ({ filename }) => (filename.split(/[/\\]/).includes('node_modules') ? undefined : true)
	},
	kit: {
		adapter: adapter({ strict: false, fallback: 'index.html' }),
		prerender: {
			entries: ['*', '/offline.html'],
			handleUnseenRoutes: 'ignore'
		}
	}
};

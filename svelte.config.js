import adapter from '@sveltejs/adapter-static';

export default {
	compilerOptions: {
		runes: ({ filename }) => (filename.split(/[/\\]/).includes('node_modules') ? undefined : true)
	},
	kit: {
		adapter: adapter({ strict: false, fallback: 'index.html' }),
		// Project Pages serves from /dublin-lifeline-directory, so the
		// deploy workflow builds with BASE_PATH=/dublin-lifeline-directory.
		// Empty locally keeps dev/preview at root.
		paths: {
			base: process.env.BASE_PATH || ''
		},
		prerender: {
			entries: ['*', '/offline.html'],
			handleUnseenRoutes: 'ignore',
			handleMissingId: 'ignore'
		}
	}
};

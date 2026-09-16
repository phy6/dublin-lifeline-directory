const fs = require('fs');
const content = fs.readFileSync('prototype-ui.html', 'utf8');
const scriptMatch = content.match(/<script>([\s\S]*?)<\/script>/);
if (scriptMatch) {
	const script = scriptMatch[1];
	try {
		new Function(script);
		console.log('Syntax OK');
	} catch (e) {
		console.error('Syntax Error:', e.message);
		// Find the line
		const lines = script.split('\n');
		const errorLine = e.stack.match(/<anonymous>:(\d+):/);
		if (errorLine) {
			const lineNum = parseInt(errorLine[1]);
			console.log('Error at line:', lineNum);
			console.log(
				'Context:',
				script
					.split('\n')
					.slice(Math.max(0, lineNum - 10), lineNum + 5)
					.join('\n')
			);
		}
	}
}

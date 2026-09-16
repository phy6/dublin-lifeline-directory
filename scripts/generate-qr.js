import QRCode from 'qrcode';
import { writeFileSync } from 'fs';
import { resolve } from 'path';

const URL = 'https://dublin-city-support.github.io/';
const OUTPUT_PATH = resolve('static/qr-code.svg');

async function generateQR() {
	try {
		const svg = await QRCode.toString(URL, {
			type: 'svg',
			errorCorrectionLevel: 'H',
			margin: 1,
			width: 300,
			color: {
				dark: '#000000',
				light: '#ffffff'
			}
		});

		writeFileSync(OUTPUT_PATH, svg);
		console.log(`QR code generated at ${OUTPUT_PATH}`);
	} catch (error) {
		console.error('Failed to generate QR code:', error);
		process.exit(1);
	}
}

generateQR();

// App-wide reactive language. Runes in a .svelte.ts module = shared state:
// any component importing `lang` re-renders when it changes. No prop drilling.
export const lang = $state<{ current: 'en' | 'ga' }>({ current: 'en' });

export function setLang(v: 'en' | 'ga') {
	lang.current = v;
	if (typeof window !== 'undefined') {
		document.documentElement.lang = v;
		try {
			localStorage.setItem('dcs-language', v);
		} catch {
			/* storage unavailable — language still applies for the session */
		}
	}
}

export function loadLang() {
	if (typeof window !== 'undefined') {
		const saved = localStorage.getItem('dcs-language');
		const initial =
			saved === 'ga' || saved === 'en' ? saved : navigator.language.startsWith('ga') ? 'ga' : 'en';
		lang.current = initial;
		document.documentElement.lang = initial;
	}
}

const STRINGS = {
	en: {
		directory: 'Directory',
		map: 'Map',
		search: 'Search',
		'app-title': 'Dublin City Support',
		'app-intro': 'Find day centres, GP clinics, and mobile health units across Dublin City.',
		'search-title': 'Search Services',
		'search-placeholder': 'Search by name, address, or service type...',
		'filter-category': 'Filter by category',
		'filter-day': 'Filter by day',
		'all-categories': 'All Categories',
		'all-days': 'All Days',
		'services-found': 'services found',
		'view-details': 'View details',
		'open-now': 'Open now',
		closed: 'Closed',
		'view-on-map': 'View on Map',
		settings: 'Settings',
		'need-help': 'Need help? Chat',
		offline: 'You are offline. Showing saved information — some details may be out of date.',
		'map-title': 'Service Map',
		'map-intro': 'Find support services across Dublin City on the interactive map below.',
		'map-help': 'Use arrow keys to navigate, press Enter or Space on a marker to view details.',
		location: 'Location',
		'opening-hours': 'Opening Hours',
		'no-hours': 'Opening hours not available.',
		'services-offered': 'Services Offered',
		categories: 'Categories',
		'last-verified': 'Last verified',
		source: 'Source',
		'not-found': 'Service not found',
		'not-found-body': "The service you're looking for doesn't exist or has been removed.",
		'search-another': 'Search for another service',
		back: 'Back'
	},
	ga: {
		directory: 'Eolaire',
		map: 'Léarscáil',
		search: 'Cuardaigh',
		'app-title': 'Tacaíocht Chathair Bhaile Átha Cliath',
		'app-intro':
			'Aimsigh ionaid lae, clinicí DG agus aonaid sláinte soghluaiste ar fud Bhaile Átha Cliath.',
		'search-title': 'Cuardaigh Seirbhísí',
		'search-placeholder': 'Cuardaigh de réir ainm, seolta, nó cineáil seirbhíse...',
		'filter-category': 'Scag de réir catagóire',
		'filter-day': 'Scag de réir lae',
		'all-categories': 'Gach Catagóir',
		'all-days': 'Gach Lá',
		'services-found': 'seirbhís aimsithe',
		'view-details': 'Féach sonraí',
		'open-now': 'Oscailte anois',
		closed: 'Dúnta',
		'view-on-map': 'Féach ar an Léarscáil',
		settings: 'Socruithe',
		'need-help': 'Cabhair? Comhrá',
		offline:
			'Tá tú as líne. Faisnéis shábháilte á taispeáint — d’fhéadfadh sonraí a bheith as dáta.',
		'map-title': 'Léarscáil Seirbhísí',
		'map-intro':
			'Aimsigh seirbhísí tacaíochta ar fud Bhaile Átha Cliath ar an léarscáil idirghníomhach.',
		'map-help':
			'Úsáid na saigheadeochracha, brúigh Enter nó Spás ar mharcóir chun sonraí a fheiceáil.',
		location: 'Suíomh',
		'opening-hours': 'Uaireanta Oscailte',
		'no-hours': 'Níl uaireanta oscailte ar fáil.',
		'services-offered': 'Seirbhísí ar Tairiscint',
		categories: 'Catagóirí',
		'last-verified': 'Fíoraithe',
		source: 'Foinse',
		'not-found': 'Níor aimsíodh an tseirbhís',
		'not-found-body': 'Níl an tseirbhís atá uait ann nó tá sí bainte.',
		'search-another': 'Cuardaigh seirbhís eile',
		back: 'Ar ais'
	}
} as const;

export type I18nKey = keyof (typeof STRINGS)['en'];

export function t(key: I18nKey): string {
	return STRINGS[lang.current][key] ?? STRINGS.en[key];
}

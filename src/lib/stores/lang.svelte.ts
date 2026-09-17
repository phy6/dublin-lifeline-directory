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
		planner: 'Planner',
		'skip-link': 'Skip to main content',
		'planner-title': 'Weekly Planner',
		'planner-device-warning':
			'Your plan is stored only on this device. Download a backup to keep it safe.',
		'planner-prev': 'Previous week',
		'planner-today': 'Today',
		'planner-next': 'Next week',
		'planner-meals': 'Meals',
		'planner-appointments': 'Appointments',
		'planner-empty': 'Nothing planned this day.',
		'planner-add': 'Add',
		'planner-add-title': 'Add appointment',
		'planner-edit-title': 'Edit appointment',
		'planner-title-label': 'Title',
		'planner-day': 'Day',
		'planner-start': 'Start',
		'planner-end': 'End',
		'planner-location': 'Location',
		'planner-notes': 'Notes',
		'planner-org': 'Organisation',
		'planner-no-org': 'No organisation',
		'planner-recurrence': 'Repeats',
		'planner-once': 'Once',
		'planner-weekly': 'Weekly',
		'planner-save': 'Save',
		'planner-cancel': 'Cancel',
		'planner-edit': 'Edit',
		'planner-delete': 'Delete',
		'planner-download': 'Download .ics',
		'planner-download-week': 'Download week (.ics)',
		'planner-backup': 'Download backup',
		'planner-restore': 'Restore',
		'planner-restored': 'Restored {count} appointments',
		'planner-invalid': 'Backup file invalid — nothing changed',
		'planner-view': 'Planner view',
		'planner-view-day': 'Day',
		'planner-view-week': 'Week',
		'planner-view-month': 'Month',
		'planner-prev-day': 'Previous day',
		'planner-next-day': 'Next day',
		'planner-prev-month': 'Previous month',
		'planner-next-month': 'Next month',
		'planner-add-appt': 'Add appointment',
		'planner-actions': 'Appointment actions',
		'planner-confirm-delete': 'Delete "{title}"? This cannot be undone.',
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
		back: 'Back',
		'no-matching-services': 'No services match these filters.',
		'clear-filters': 'Clear filters',
		'install-app': 'Install app',
		'install-app-blurb': 'Add Dublin City Support to your home screen for offline access.',
		'not-now': 'Not now',
		'report-wrong-info': 'Report wrong info',
		'report-email-subject': 'Outdated info'
	},
	ga: {
		directory: 'Eolaire',
		map: 'Léarscáil',
		search: 'Cuardaigh',
		planner: 'Pleanálaí',
		'skip-link': 'Léim go dtí an príomhábhar',
		'planner-title': 'Pleanálaí Seachtainiúil',
		'planner-device-warning':
			'Stóráiltear do phlean ar an ngléas seo amháin. Íoslódáil cúltaca chun é a choinneáil sábháilte.',
		'planner-prev': 'An tseachtain roimhe',
		'planner-today': 'Inniu',
		'planner-next': 'An chéad seachtain eile',
		'planner-meals': 'Béilí',
		'planner-appointments': 'Coinní',
		'planner-empty': 'Níl aon rud beartaithe don lá seo.',
		'planner-add': 'Cuir leis',
		'planner-add-title': 'Cuir coinne leis',
		'planner-edit-title': 'Cuir an choinne in eagar',
		'planner-title-label': 'Teideal',
		'planner-day': 'Lá',
		'planner-start': 'Tús',
		'planner-end': 'Deireadh',
		'planner-location': 'Suíomh',
		'planner-notes': 'Nótaí',
		'planner-org': 'Eagraíocht',
		'planner-no-org': 'Gan eagraíocht',
		'planner-recurrence': 'Athuair',
		'planner-once': 'Uair amháin',
		'planner-weekly': 'Seachtainiúil',
		'planner-save': 'Sábháil',
		'planner-cancel': 'Cealaigh',
		'planner-edit': 'Eagar',
		'planner-delete': 'Scrios',
		'planner-download': 'Íoslódáil .ics',
		'planner-download-week': 'Íoslódáil an tseachtain (.ics)',
		'planner-backup': 'Íoslódáil cúltaca',
		'planner-restore': 'Athchóirigh',
		'planner-restored': 'Athchóiríodh {count} ceapachán',
		'planner-invalid': 'Comhad cúltaca neamhbhailí — níor athraíodh aon rud',
		'planner-view': 'Radharc an phleanálaí',
		'planner-view-day': 'Lá',
		'planner-view-week': 'Seachtain',
		'planner-view-month': 'Mí',
		'planner-prev-day': 'An lá roimhe',
		'planner-next-day': 'An chéad lá eile',
		'planner-prev-month': 'An mhí roimhe',
		'planner-next-month': 'An chéad mhí eile',
		'planner-add-appt': 'Cuir coinne leis',
		'planner-actions': 'Gníomhartha coinne',
		'planner-confirm-delete': 'Scrios "{title}"? Ní féidir é seo a chealú.',
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
		back: 'Ar ais',
		'no-matching-services': 'Ní oireann aon seirbhís do na scagairí seo.',
		'clear-filters': 'Glan na scagairí',
		'install-app': 'Suiteáil an aip',
		'install-app-blurb':
			'Cuir Tacaíocht Bhaile Átha Cliath le do scáileán baile le rochtain as líne.',
		'not-now': 'Níos déanaí',
		'report-wrong-info': 'Tuairiscigh eolas mícheart',
		'report-email-subject': 'Eolas as dáta'
	}
} as const;

export type I18nKey = keyof (typeof STRINGS)['en'];

export function t(key: I18nKey): string {
	return STRINGS[lang.current][key] ?? STRINGS.en[key];
}

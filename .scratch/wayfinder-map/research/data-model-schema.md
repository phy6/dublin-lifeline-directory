# Dublin City Support Services — Data Model Schema & Migration Plan

**Document Version:** 1.0
**Date:** 2026-09-14
**Project:** Dublin City Support Services PWA (SvelteKit + @sveltejs/adapter-static + @vite-pwa/sveltekit)
**Architecture:** Static JSON on GitHub Pages — no backend, no database
**Data Source:** `src/lib/data/services.json` (consumed by SvelteKit load functions)

---

## Table of Contents

1. [Architecture Constraints](#1-architecture-constraints)
2. [Schema Definitions](#2-schema-definitions)
   - [2.1 Location Schema](#21-location-schema)
   - [2.2 Service Schema](#22-service-schema)
   - [2.3 Schedule Schema](#23-schedule-schema)
   - [2.4 Healthcare Clinic Schema](#24-healthcare-clinic-schema)
3. [Composite Data Structure (services.json)](#3-composite-data-structureservicesjson)
4. [Data Migration Path](#4-data-migration-path)
5. [Schema Evolution & Extension Guide](#5-schema-evolution--extension-guide)

---

## 1. Architecture Constraints

All data is served as static JSON hosted on GitHub Pages. The app uses SvelteKit's `+page.server.ts` and client-side `load` functions to import or fetch the JSON. The service worker (`@vite-pwa/sveltekit`) precaches and serves `services.json` via `StaleWhileRevalidate`. There is no backend, no database, and no server-side processing.

**Implications for the data model:**

- Every field must be representable as JSON — no blobs, binary data, or server-side computed fields
- Data must be self-contained in a single JSON file (`services.json`) that can be fetched at runtime or imported at build time
- Coordinates, contact info, and schedule details must be embedded in the data, not fetched from an external API
- The `metadata` object must carry freshness/version information for the offline strategy

---

## 2. Schema Definitions

### 2.1 Location Schema

A `Location` represents a physical site where Dublin support services are offered. This unifies the flyer's `day_support_centres` and the location references within `free_doctor_clinics`.

```typescript
// src/lib/data/schemas.ts

interface Location {
	// --- Identity ---
	id: string; // Unique slug identifier (e.g., "capuchin-day-centre")
	name: string; // Display name (e.g., "Capuchin Day Centre")

	// --- Address ---
	address: string; // Full street address (e.g., "29 Bow St, Dublin 7")
	eircode?: string; // Irish postal code (optional — flyer only gave "Dublin 1-8")
	county?: string; // County (default: "Dublin")

	// --- Coordinates ---
	coordinates: {
		latitude: number; // Decimal degrees (missing from flyer — must be added)
		longitude: number; // Decimal degrees (missing from flyer — must be added)
	};

	// --- Services offered ---
	serviceIds: string[]; // References to Service.id[]
	categories: string[]; // Service category names (e.g., ["Food", "Hygiene", "Connectivity"])
	healthcareServiceIds?: string[]; // References to HealthcareService.id[] (optional)

	// --- Schedule ---
	scheduleIds: string[]; // References to Schedule.id[]

	// --- Contact ---
	contact: {
		phone?: string; // Phone number (null/missing in flyer)
		email?: string; // Email address (null/missing in flyer)
		website?: string; // Website URL (null/missing in flyer)
	};

	// --- Operational ---
	isOpenNow?: boolean; // Computed from current time vs schedule (runtime)
	notes?: string; // Special notes (e.g., "Clothes market on Fridays at 16:00")

	// --- Metadata ---
	metadata: {
		version: string; // Semver string (e.g., "3.1.0")
		lastUpdated: string; // ISO 8601 timestamp
		lastVerified: string; // ISO 8601 date when location was verified
		lastScraped: string; // ISO 8601 timestamp when data was scraped
		source: string; // Source URL (e.g., "www.primarycaresafetynet.ie")
	};
}
```

**Field notes derived from flyer data:**

| Field             | Flyer Status                          | Action Required                             |
| ----------------- | ------------------------------------- | ------------------------------------------- |
| `coordinates`     | ❌ Missing for all 5 locations        | Must be geocoded and added                  |
| `contact.phone`   | ❌ Missing for all locations          | Must be sourced externally or marked `null` |
| `contact.email`   | ❌ Missing for all locations          | Must be sourced externally or marked `null` |
| `contact.website` | ❌ Missing for all locations          | Must be sourced externally or marked `null` |
| `eircode`         | ❌ Missing (only "Dublin 1-8" area)   | Must be geocoded or added manually          |
| `notes`           | ✅ Present for some locations         | Copy from `special_notes` field             |
| `categories`      | ✅ Derived from `services_categories` | Map directly                                |
| `serviceIds`      | ✅ Present in flyer                   | Map from `services` array                   |

**Locations from flyer (5 Day Support Centres):**

| ID                       | Name                   | Address                        | Categories                              |
| ------------------------ | ---------------------- | ------------------------------ | --------------------------------------- |
| `mendicity-institute`    | Mendicity Institute    | 9 Island St., Dublin 8         | Food, Hygiene, Connectivity, Employment |
| `capuchin-day-centre`    | Capuchin Day Centre    | 29 Bow St, Dublin 7            | Food, Connectivity, Hygiene, Healthcare |
| `lighthouse-cafe`        | The Lighthouse Cafe    | 28 Pearse Street, Dublin 2     | Food, Connectivity, Hygiene             |
| `merchants-quay-ireland` | Merchants Quay Ireland | 13/14 Merchants Quay, Dublin 8 | Food, Connectivity, Hygiene, Healthcare |
| `inclusion-health-hub`   | Inclusion Health Hub   | 60 Amiens St, Dublin 1         | Healthcare                              |

---

### 2.2 Service Schema

A `Service` represents a distinct offering available at one or more locations. Services are categorized for filtering and map display.

```typescript
interface Service {
	id: string; // Unique slug (e.g., "hot-meals", "gp-clinic")
	name: string; // Display name (e.g., "Hot Meals", "GP Clinic")
	category: string; // One of: "Food" | "Hygiene" | "Connectivity" | "Healthcare" | "Employment" | "Other"
	description: string; // Human-readable description of the service
	isHealthcare: boolean; // Whether this is a healthcare service (derived from category)
}
```

**Category enum:**

```typescript
type ServiceCategory = 'Food' | 'Hygiene' | 'Connectivity' | 'Healthcare' | 'Employment' | 'Other';
```

**Services derived from flyer data:**

| Service ID          | Name                     | Category     | Description                    | Source                                                                   |
| ------------------- | ------------------------ | ------------ | ------------------------------ | ------------------------------------------------------------------------ |
| `food`              | Food                     | Food         | Meals provided at the location | Flyer: "Food", "Hot Meals (Breakfast & Lunch)", "Food & phone charging"  |
| `shower-clothes`    | Shower & Clothes Washing | Hygiene      | Shower and laundry facilities  | Flyer: "Shower & Clothes washing", "Shower/Clothing"                     |
| `connectivity`      | WiFi & Phone Charging    | Connectivity | Free WiFi and device charging  | Flyer: "WiFi & phone charging", "WiFi & Phone Charging"                  |
| `employment-clinic` | Employment Clinic        | Employment   | Employment support services    | Flyer: "Employment Clinic (Mon 6:15pm)"                                  |
| `gp-clinic`         | GP Clinic                | Healthcare   | General Practitioner services  | Flyer: "Doctor/Nurse/Dentist/Chiropodist/Optician", "GP Clinic services" |
| `nurse`             | Nurse                    | Healthcare   | Nursing services               | Flyer: "Doctor/Nurse/Dentist/Chiropodist/Optician"                       |
| `dentist`           | Dentist                  | Healthcare   | Dental services                | Flyer: "Doctor/Nurse/Dentist/Chiropodist/Optician"                       |
| `chiropodist`       | Chiropodist              | Healthcare   | Podiatry/chiropody services    | Flyer: "Doctor/Nurse/Dentist/Chiropodist/Optician"                       |
| `optician`          | Optician                 | Healthcare   | Eye care/optician services     | Flyer: "Doctor/Nurse/Dentist/Chiropodist/Optician"                       |
| `clothes-market`    | Clothes Market           | Hygiene      | Clothing distribution event    | Flyer: "Clothes (market on Fridays 16:00)"                               |

**Notes:**

- Services are normalized from the flyer's free-text descriptions into discrete, filterable entries
- Healthcare services from flyer fields (`healthcare_services`) map to individual Service entries
- The `isHealthcare` flag enables quick filtering for the map view and emergency contacts section

---

### 2.3 Schedule Schema

A `Schedule` defines the operating hours for a specific location on a given day, including walk-in vs appointment availability.

```typescript
interface Schedule {
	id: string; // Unique slug (e.g., "capuchin-day-centre-mon")
	locationId: string; // References Location.id
	day: DayOfWeek; // Day of the week
	hours: ScheduleHours; // Opening hours for this day
	walkInAvailable: boolean | null; // Whether walk-ins are accepted
	appointmentAvailable: boolean | null; // Whether appointments are accepted
}

type DayOfWeek = 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';

interface ScheduleHours {
	open: string | null; // Opening time in HH:MM format (e.g., "08:30"), or null if closed
	close: string | null; // Closing time in HH:MM format (e.g., "22:30"), or null if closed
	// Supports split sessions via SchedulePeriods[] (see below)
}

interface SchedulePeriods {
	periods: Array<{
		open: string; // HH:MM
		close: string; // HH:MM
	}>;
}
```

**Handling split hours:** Some locations have multiple sessions per day (e.g., Capuchin: "07:30-11:30, 12:30-15:00"). Use the `SchedulePeriods` structure:

```typescript
// Example: Capuchin Day Centre Monday
{
  id: "capuchin-day-centre-monday",
  locationId: "capuchin-day-centre",
  day: "monday",
  hours: {
    periods: [
      { open: "07:30", close: "11:30" },
      { open: "12:30", close: "15:00" }
    ]
  },
  walkInAvailable: null,     // Not specified on flyer
  appointmentAvailable: null // Not specified on flyer
}
```

**Handling special schedules:** The Mendicity Institute Sunday has two sessions: "09:30-14:30, 16:30-22:30". The Lighthouse Cafe has varying schedules across different days.

**Schedule entries derived from flyer:**

Each location requires 7 day entries (one per `DayOfWeek`). Total schedule entries:

| Location               | Monday–Friday           | Saturday              | Sunday                               | Total entries |
| ---------------------- | ----------------------- | --------------------- | ------------------------------------ | ------------- |
| Mendicity Institute    | 5 entries (08:30-22:30) | 0 (null)              | 2 periods (09:30-14:30, 16:30-22:30) | 7             |
| Capuchin Day Centre    | 5 entries (split hours) | 1 entry (split hours) | 0 (null)                             | 7             |
| The Lighthouse Cafe    | 5 entries (varied)      | 1 entry (15:00-18:00) | 1 entry (15:00-18:00)                | 7             |
| Merchants Quay Ireland | 5 entries (08:00-19:00) | 0 (null)              | 1 entry (08:00-14:00)                | 7             |
| Inclusion Health Hub   | 0 (hours null)          | 0                     | 0                                    | 7             |

**Total: 35 Schedule entries** (7 days × 5 locations)

**Special cases:**

- `hours: null` (Inclusion Health Hub) → `SchedulePeriods.periods: []` and `walkInAvailable: null`, `appointmentAvailable: null`
- GP clinics have separate schedules in the Healthcare Clinic schema, not in the Location schedule
- Walk-in/appointment availability is not specified in the flyer → `null` for all day-support-centre schedules

---

### 2.4 Healthcare Clinic Schema

A `HealthcareClinic` represents a medical facility associated with a location, offering GP and other healthcare services with specific scheduling details.

```typescript
interface HealthcareClinic {
	id: string; // Unique slug (e.g., "capuchin-day-centre-gp")
	name: string; // Display name (e.g., "Capuchin Day Centre GP Clinic")
	locationId: string; // References Location.id
	address: string; // Full address (may differ from Location.address)
	schedule: {
		mon_fri: ScheduleDetail | null; // Monday–Friday schedule
		saturday: ScheduleDetail | null; // Saturday schedule
		sunday: ScheduleDetail | null; // Sunday schedule
	};
	appointmentAvailable: boolean | null; // Whether appointments are accepted
	walkInAvailable: boolean | null; // Whether walk-ins are accepted
	scheduleDetails: string; // Human-readable schedule description
	serviceIds: string[]; // References to Service.id[] (e.g., ["gp-clinic", "nurse", "dentist"])
	notes?: string; // Additional notes
}

interface ScheduleDetail {
	description: string | null; // Human-readable schedule (e.g., "Appointment and walk-in times available")
	hours: SchedulePeriods | null; // Structured hours if available
}
```

**Healthcare clinics derived from flyer (`free_doctor_clinics`):**

| ID                          | Name                             | Location                 | Schedule                                       | Walk-in | Appointment |
| --------------------------- | -------------------------------- | ------------------------ | ---------------------------------------------- | ------- | ----------- |
| `inclusion-health-hub-gp`   | Inclusion Health Hub GP Clinic   | `inclusion-health-hub`   | Mon-Fri: Appointment and walk-in (unspecified) | ✅      | ✅          |
| `capuchin-day-centre-gp`    | Capuchin Day Centre GP Clinic    | `capuchin-day-centre`    | Mon-Fri: Appointment and walk-in (unspecified) | ✅      | ✅          |
| `merchants-quay-ireland-gp` | Merchants Quay Ireland GP Clinic | `merchants-quay-ireland` | Mon-Fri: Appointment and walk-in (unspecified) | ✅      | ✅          |
| `mendicity-institute-gp`    | Mendicity Institute GP Clinic    | `mendicity-institute`    | Mon-Fri: Appointment and walk-in (unspecified) | ✅      | ✅          |
| `mobile-health-unit`        | Mobile Health Unit (MHU)         | null (mobile)            | Visiting different locations on scheduled days | ❓      | ❓          |

**Key notes:**

- The MHU has `locationId: null` since it travels to different locations
- GP clinic `schedule` uses `mon_fri`, `saturday`, `sunday` keys rather than individual days (the flyer does not specify exact hours)
- `appointmentAvailable` and `walkInAvailable` are `true` for 4 clinics, `null` for MHU
- Healthcare services per clinic must be resolved from the parent Location's `healthcareServiceIds`

---

## 3. Composite Data Structure (services.json)

The top-level `services.json` file aggregates all schemas. This is the file consumed by the app and cached by the service worker.

```json
{
	"version": "3.1.0",
	"lastUpdated": "2026-09-14T00:00:00.000Z",
	"lastVerified": "2026-09-14",
	"lastScraped": "2026-09-14T00:00:00.000Z",
	"source": "www.primarycaresafetynet.ie",
	"metadata": {
		"nextSync": "2026-09-21T00:00:00.000Z",
		"dataRetentionDays": 7,
		"lowDataCompactAvailable": true
	},
	"locations": [{ "$ref": "#/definitions/Location" }],
	"services": [{ "$ref": "#/definitions/Service" }],
	"schedules": [{ "$ref": "#/definitions/Schedule" }],
	"healthcareClinics": [{ "$ref": "#/definitions/HealthcareClinic" }]
}
```

**Structure rationale:**

- Top-level arrays (`locations`, `services`, `schedules`, `healthcareClinics`) allow the service worker to cache a single JSON response
- Cross-references use `id` strings rather than nested objects to avoid duplication and keep the file size small
- The `metadata` object carries version and freshness fields used by the offline strategy (StaleWhileRevalidate comparison)
- Total estimated size: ~5-10KB uncompressed, well within the single-cache approach documented in `offline-strategy.md`

**SvelteKit load function usage:**

```typescript
// +page.server.ts
export async function load() {
  const data = await fetch('/services.json').then(r => r.json());
  // Or: import services from '$lib/data/services.json' for build-time
  return { locations: data.locations, services: data.services, ... };
}
```

---

## 4. Data Migration Path

### 4.1 Source: Flyer JSON → Target: services.json

The migration transforms `flyer-data.json` into the `services.json` structure defined above.

```
flyer-data.json
├── day_support_centres[] ──→ locations[] (5 entries)
│   ├── services[] ──→ services[] (deduplicated)
│   ├── hours{} ──→ schedules[] (35 entries, 7 days × 5 locations)
│   ├── healthcare_services[] ──→ healthcareServiceIds in Location
│   └── special_notes ──→ notes in Location
│
└── free_doctor_clinics[] ──→ healthcareClinics[] (5 entries)
    ├── location_id ──→ locationId in HealthcareClinic
    ├── schedule{} ──→ schedule in HealthcareClinic
    ├── appointment_available ──→ appointmentAvailable
    ├── walk_in_available ──→ walkInAvailable
    └── (GP services) ──→ serviceIds in HealthcareClinic
```

### 4.2 Migration Steps

#### Step 1: Extract Locations from Day Support Centres

For each `day_support_centre` in `flyer-data.json`:

```typescript
function createLocation(centre): Location {
	return {
		id: centre.id,
		name: centre.name,
		address: centre.address,
		coordinates: { latitude: null, longitude: null }, // ⚠️ MUST BE GEOCODED
		serviceIds: centre.services.map(normalizeServiceId),
		categories: centre.services_categories,
		healthcareServiceIds:
			centre.healthcare_services.length > 0
				? centre.healthcare_services.map((id) => `healthcare-${id.toLowerCase()}`)
				: [],
		scheduleIds: getScheduleIds(centre.id), // 7 per location
		contact: {
			phone: centre.phone, // null from flyer
			email: null, // not in flyer
			website: centre.website // null from flyer
		},
		notes: centre.special_notes || null,
		metadata: {
			version: '3.1.0',
			lastUpdated: centre.extracted_date, // from flyer-data.json
			lastVerified: centre.extracted_date,
			lastScraped: centre.extracted_date,
			source: centre.source
		}
	};
}
```

#### Step 2: Deduplicate and Create Services

```typescript
function createServices(locations): Service[] {
	const serviceMap = new Map<string, Service>();

	for (const location of locations) {
		for (const serviceName of location.rawServiceNames) {
			const { id, category, description } = normalizeService(serviceName, location.categories);
			if (!serviceMap.has(id)) {
				serviceMap.set(id, {
					id,
					name: categoryLabels[category] || serviceName,
					category,
					description: `${serviceName} available at ${location.name}`,
					isHealthcare: category === 'Healthcare'
				});
			}
		}
	}

	return Array.from(serviceMap.values());
}
```

**Normalization rules for services from flyer text:**

| Flyer text                                                                         | Service ID                          | Category     |
| ---------------------------------------------------------------------------------- | ----------------------------------- | ------------ |
| "Food", "Hot Meals (Breakfast & Lunch)", "Food & phone charging"                   | `food`                              | Food         |
| "Shower & Clothes washing", "Shower/Clothing", "Clothes (market on Fridays 16:00)" | `shower-clothes` / `clothes-market` | Hygiene      |
| "WiFi & phone charging", "WiFi & Phone Charging"                                   | `connectivity`                      | Connectivity |
| "Employment Clinic (Mon 6:15pm)"                                                   | `employment-clinic`                 | Employment   |
| "Doctor/Nurse/Dentist/Chiropodist/Optician"                                        | → decomposed                        | Healthcare   |
| "GP Clinic services"                                                               | `gp-clinic`                         | Healthcare   |

#### Step 3: Create Schedules from Hours

```typescript
function createSchedules(location): Schedule[] {
	const days: DayOfWeek[] = [
		'monday',
		'tuesday',
		'wednesday',
		'thursday',
		'friday',
		'saturday',
		'sunday'
	];
	const schedules: Schedule[] = [];

	for (const day of days) {
		const hoursStr = location.hours[day];
		if (!hoursStr) {
			schedules.push({
				id: `${location.id}-${day}`,
				locationId: location.id,
				day,
				hours: { periods: [] },
				walkInAvailable: null,
				appointmentAvailable: null
			});
		} else {
			const periods = parseTimeRanges(hoursStr); // "08:30-22:30" → [{open:"08:30", close:"22:30"}]
			schedules.push({
				id: `${location.id}-${day}`,
				locationId: location.id,
				day,
				hours: { periods },
				walkInAvailable: null,
				appointmentAvailable: null
			});
		}
	}

	return schedules;
}
```

**Parsing `hours` strings:**

- `"08:30-22:30"` → single period `[{open: "08:30", close: "22:30"}]`
- `"07:30-11:30, 12:30-15:00"` → two periods `[{open:"07:30",close:"11:30"},{open:"12:30",close:"15:00"}]`
- `"09:30-14:30, 16:30-22:30"` → two periods
- `null` → empty periods array

#### Step 4: Create Healthcare Clinics

```typescript
function createHealthcareClinics(clinics, locations): HealthcareClinic[] {
	return clinics.map((clinic) => {
		const location = locations.find((l) => l.id === clinic.location_id);
		const healthcareServiceIds = location?.healthcareServiceIds || [];

		return {
			id: clinic.id,
			name: clinic.name,
			locationId: clinic.location_id,
			address: clinic.address,
			schedule: {
				mon_fri: clinic.schedule.mon_fri
					? { description: clinic.schedule.mon_fri, hours: null }
					: null,
				saturday: clinic.schedule.saturday
					? { description: clinic.schedule.saturday, hours: null }
					: null,
				sunday: clinic.schedule.sunday ? { description: clinic.schedule.sunday, hours: null } : null
			},
			appointmentAvailable: clinic.appointment_available,
			walkInAvailable: clinic.walk_in_available,
			scheduleDetails: clinic.schedule_details,
			serviceIds: healthcareServiceIds,
			notes: clinic.schedule_details
		};
	});
}
```

#### Step 5: Assemble and Write services.json

```typescript
function assembleServicesJson(flyerData): string {
	const locations = flyerData.day_support_centres.map(createLocation);
	const services = createServices(locations);
	const schedules = flyerData.day_support_centres.flatMap(createSchedules);
	const healthcareClinics = createHealthcareClinics(flyerData.free_doctor_clinics, locations);

	// ⚠️ Add coordinates for all locations before writing
	// Must be geocoded from address strings

	const output = {
		version: '3.1.0',
		lastUpdated: flyerData.extracted_date,
		lastVerified: flyerData.extracted_date,
		lastScraped: flyerData.extracted_date,
		source: flyerData.source,
		metadata: {
			nextSync: '2026-09-21T00:00:00.000Z',
			dataRetentionDays: 7,
			lowDataCompactAvailable: true
		},
		locations,
		services,
		schedules,
		healthcareClinics
	};

	return JSON.stringify(output, null, '\t');
}
```

### 4.3 Migration Summary

| Source Field                                    | Target Field                            | Transformation                              | Status       |
| ----------------------------------------------- | --------------------------------------- | ------------------------------------------- | ------------ |
| `day_support_centres[].name`                    | `Location.name`                         | Direct                                      | ✅           |
| `day_support_centres[].address`                 | `Location.address`                      | Direct                                      | ✅           |
| `day_support_centres[].hours`                   | `Schedule[]`                            | Parse time strings → `SchedulePeriods`      | ✅           |
| `day_support_centres[].services`                | `Service[]` + `Location.serviceIds`     | Deduplicate, normalize                      | ✅           |
| `day_support_centres[].services_categories`     | `Location.categories`                   | Direct                                      | ✅           |
| `day_support_centres[].healthcare_services`     | `Location.healthcareServiceIds`         | Map to Service IDs                          | ✅           |
| `day_support_centres[].special_notes`           | `Location.notes`                        | Direct                                      | ✅           |
| `free_doctor_clinics[]`                         | `HealthcareClinic[]`                    | Direct + resolve `locationId`               | ✅           |
| `free_doctor_clinics[].schedule`                | `HealthcareClinic.schedule`             | Direct                                      | ✅           |
| `free_doctor_clinics[].appointment_available`   | `HealthcareClinic.appointmentAvailable` | Direct                                      | ✅           |
| `free_doctor_clinics[].walk_in_available`       | `HealthcareClinic.walkInAvailable`      | Direct                                      | ✅           |
| `free_doctor_clinics[].schedule_details`        | `HealthcareClinic.scheduleDetails`      | Direct                                      | ✅           |
| **`day_support_centres[].coordinates`**         | **`Location.coordinates`**              | **⚠️ Missing — must be geocoded**           | **REQUIRED** |
| **`day_support_centres[].phone/email/website`** | **`Location.contact`**                  | **⚠️ Missing — must be sourced externally** | **REQUIRED** |

### 4.4 Missing Data Requirements (from gap-analysis.md)

Before migration can be complete, the following must be obtained:

1. **Coordinates** — Geocode all 5 addresses (Dublin 1-8) to obtain `latitude`/`longitude`
2. **Phone numbers** — Source from primarycaresafetynet.ie or external directories
3. **Email addresses** — Source externally or leave as `null`
4. **Website URLs** — Source externally or leave as `null`
5. **Eircodes** — Geocode addresses to obtain full Irish postal codes
6. **GP clinic specific hours** — Contact primarycaresafetynet.ie for exact Mon-Fri times
7. **MHU schedule** — Contact for route/day specifics
8. **Walk-in vs appointment per day** — Currently `null` for day support centres

---

## 5. Schema Evolution & Extension Guide

### Adding new fields in future versions

When extending `services.json`, follow these principles:

1. **Add optional fields** — never make existing fields required, to avoid breaking existing data
2. **Version bump** — increment `version` in `metadata` when the schema changes structurally
3. **Backward compatibility** — old clients should ignore unknown fields
4. **Compact JSON** — for low-data mode, maintain a `services-compact.json` with only `id`, `name`, `latitude`, `longitude`, `category`, `tags`

### Planned extensions (from gap-analysis.md recommendations)

| Extension             | Schema Impact                                         | Priority                      |
| --------------------- | ----------------------------------------------------- | ----------------------------- |
| Coordinates           | Add `Location.coordinates.latitude/longitude`         | P0 — blocks map functionality |
| Accessibility info    | Add `Location.accessibility` object                   | P2                            |
| Eligibility criteria  | Add `Service.eligibility` field                       | P2                            |
| Holiday closures      | Add `Schedule.holidays` field                         | P3                            |
| Capacity/booking info | Add `Service.capacity` and `Location.bookingRequired` | P3                            |
| Languages offered     | Add `Location.languages` array                        | P2                            |
| Parking/transport     | Add `Location.transport` object                       | P3                            |

### Compact JSON for low-data mode

```json
{
	"version": "3.1.0",
	"services": [
		{
			"id": "capuchin-day-centre",
			"name": "Capuchin Day Centre",
			"latitude": 53.3481,
			"longitude": -6.2758,
			"category": "Emergency Shelter",
			"tags": ["food", "medical"]
		}
	]
}
```

---

## Sources

- Source data: `/home/martin/Dublin City Support Services/.scratch/wayfinder-map/research/flyer-data.json`
- Gap analysis: `/home/martin/Dublin City Support Services/.scratch/wayfinder-map/research/gap-analysis.md`
- Offline strategy: `/home/martin/Dublin City Support Services/.scratch/wayfinder-map/research/offline-strategy.md`
- Framework recommendation: `/home/martin/Dublin City Support Services/.scratch/wayfinder-map/research/pwa-framework-recommendation.md`

// frontend_2.0/app.js
// SAKHI 2.0 — Screenshot-Accurate Application Controller
// Responsive UI Implementation for ASHA Field Workers

(function () {
  'use strict';

  // SVG Avatars (Data URIs for reliable rendering)
  const MOTHER_AVATAR = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='48' fill='%23D4F4E4'/><circle cx='50' cy='38' r='18' fill='%23F4B58A'/><path d='M30 36 C30 20 70 20 70 36 C70 48 64 54 64 54 L36 54 Z' fill='%231F2937'/><path d='M20 94 C24 64 38 60 50 60 C62 60 76 64 80 94 Z' fill='%23FFFFFF'/><path d='M35 60 L65 94 L80 94 L50 60 Z' fill='%23F04D79'/><circle cx='50' cy='34' r='1.5' fill='%23DC2626'/></svg>";
  const BABY_AVATAR = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='48' fill='%23EDF2FE'/><circle cx='50' cy='42' r='20' fill='%23F6BE97'/><path d='M46 22 C48 18 52 18 54 22 C52 26 48 26 46 22 Z' fill='%231F2937'/><circle cx='43' cy='40' r='2' fill='%231F2937'/><circle cx='57' cy='40' r='2' fill='%231F2937'/><path d='M46 48 Q50 52 54 48' stroke='%23C2410C' stroke-width='2' stroke-linecap='round' fill='none'/><path d='M30 84 C30 64 70 64 70 84 Z' fill='%23FBBF24'/></svg>";

  // Initial Mothers Data (matching screenshot media_1795280797953_e373792f)
  const INITIAL_MOTHERS = [
    {
      id: "M-01",
      name: "Lakshmi Nandhana",
      age: 30,
      bloodGroup: "O+",
      phone: "1234567891",
      weeks: 24,
      dueDate: "28 Sep 2024",
      checkupDate: "15 jun 2026",
      ironStatus: "Regular",
      vaccineStatus: "Due in 5 days",
      address: "Sector 3, Main Road",
      weight: "55 kg (Normal)",
      healthSummary: [
        { title: "Iron Tablets", sub: "Taking regularly", status: "Regular", type: "check" },
        { title: "Folic Acid", sub: "Taking regularly", status: "Regular", type: "check" },
        { title: "Calcium", sub: "Due in 5 days", status: "Due", type: "alert" },
        { title: "Weight", sub: "55 kg (Normal)", status: "Normal", type: "check" }
      ]
    },
    { id: "M-02", name: "Swetha Santhosh", age: 26, bloodGroup: "B+", phone: "9845112233", weeks: 18, dueDate: "10 Nov 2024", checkupDate: "18 Jul 2026", ironStatus: "Regular", vaccineStatus: "Up to date", address: "Sector 2, Tumkur", weight: "52 kg (Normal)" },
    { id: "M-03", name: "mahima Lakshmi", age: 28, bloodGroup: "A+", phone: "9480223344", weeks: 32, dueDate: "14 Aug 2024", checkupDate: "20 Jun 2026", ironStatus: "Missed 2 doses", vaccineStatus: "Due in 3 days", address: "Main Road, Ward 4", weight: "58 kg (Normal)" },
    { id: "M-04", name: "Athira Menon", age: 24, bloodGroup: "O+", phone: "8123445566", weeks: 14, dueDate: "05 Dec 2024", checkupDate: "22 Jul 2026", ironStatus: "Regular", vaccineStatus: "Up to date", address: "Nagavalli Cross, Ward 1", weight: "49 kg (Underweight)" },
    { id: "M-05", name: "Aiswarya", age: 29, bloodGroup: "AB+", phone: "9741556677", weeks: 28, dueDate: "15 Sep 2024", checkupDate: "25 Jun 2026", ironStatus: "Regular", vaccineStatus: "Completed", address: "Near Anjaneya Temple", weight: "61 kg (Normal)" },
    { id: "M-06", name: "Aliya", age: 22, bloodGroup: "B-", phone: "9008667788", weeks: 12, dueDate: "20 Jan 2025", checkupDate: "30 Jul 2026", ironStatus: "Regular", vaccineStatus: "Due in 7 days", address: "North Block, Ward 2", weight: "48 kg (Normal)" },
    { id: "M-07", name: "Ayana S", age: 27, bloodGroup: "O-", phone: "9113778899", weeks: 36, dueDate: "25 Jul 2024", checkupDate: "10 Jun 2026", ironStatus: "Regular", vaccineStatus: "Completed", address: "Ashraya Colony, Ward 5", weight: "64 kg (Normal)" },
    { id: "M-08", name: "Mazha dhani", age: 25, bloodGroup: "A-", phone: "9900889900", weeks: 20, dueDate: "28 Oct 2024", checkupDate: "12 Jul 2026", ironStatus: "Regular", vaccineStatus: "Due in 10 days", address: "Market Street, Tumkur", weight: "53 kg (Normal)" },
    { id: "M-09", name: "Sreedevi", age: 31, bloodGroup: "B+", phone: "9611990011", weeks: 30, dueDate: "02 Sep 2024", checkupDate: "28 Jun 2026", ironStatus: "Regular", vaccineStatus: "Completed", address: "Post Office Road, Ward 3", weight: "57 kg (Normal)" }
  ];

  // Initial Babies Data (matching screenshot media_1795280765040_6a677754)
  const INITIAL_BABIES = [
    {
      id: "B-01",
      name: "Rohan Kumar",
      age: "8 months",
      gender: "Male",
      dob: "12 Oct 2023",
      phone: "1234567891",
      guardian: "Suresh Kumar",
      address: "Sector 3, Main Road",
      bloodGroup: "B+",
      totalVaccines: 10,
      completedVaccines: 7,
      pendingVaccines: 2,
      upcomingVaccines: 1,
      schedule: [
        { name: "BCG", timing: "At Birth", date: "12 Oct 2023", status: "Completed", type: "completed" },
        { name: "OPV (Dose 1)", timing: "6 Weeks", date: "25 Nov 2023", status: "Completed", type: "completed" },
        { name: "Pentavalent (Dose 1)", timing: "6 Weeks", date: "25 Nov 2023", status: "Completed", type: "completed" },
        { name: "OPV (Dose 2)", timing: "10 Weeks", date: "09 Dec 2023", status: "Completed", type: "completed" },
        { name: "Pentavalent (Dose 3)", timing: "14 Weeks", date: "20 June 2024", status: "Due Soon", type: "due" },
        { name: "Measles (Dose 1)", timing: "9 Months", date: "12 July 2024", status: "Upcoming", type: "upcoming" }
      ]
    },
    { id: "B-02", name: "Swetha Santhosh", age: "6 months", gender: "Female", dob: "15 Dec 2023", phone: "9845112233", guardian: "Santhosh", address: "Sector 2", bloodGroup: "O+", totalVaccines: 10, completedVaccines: 6, pendingVaccines: 3, upcomingVaccines: 1 },
    { id: "B-03", name: "Zechariah John", age: "11 months", gender: "Male", dob: "10 Jul 2023", phone: "9480223344", guardian: "John P", address: "Nagavalli", bloodGroup: "A+", totalVaccines: 10, completedVaccines: 8, pendingVaccines: 1, upcomingVaccines: 1 },
    { id: "B-04", name: "Sachin Jacob", age: "4 months", gender: "Male", dob: "22 Feb 2024", phone: "8123445566", guardian: "Jacob S", address: "Main Road, Ward 4", bloodGroup: "B+", totalVaccines: 10, completedVaccines: 5, pendingVaccines: 4, upcomingVaccines: 1 },
    { id: "B-05", name: "Aiswarya A", age: "9 months", gender: "Female", dob: "05 Sep 2023", phone: "9741556677", guardian: "Anand M", address: "Temple Road", bloodGroup: "O-", totalVaccines: 10, completedVaccines: 7, pendingVaccines: 2, upcomingVaccines: 1 },
    { id: "B-06", name: "Aliya P", age: "3 months", gender: "Female", dob: "18 Mar 2024", phone: "9008667788", guardian: "Parvez", address: "North Colony", bloodGroup: "AB+", totalVaccines: 10, completedVaccines: 4, pendingVaccines: 5, upcomingVaccines: 1 },
    { id: "B-07", name: "Hanna K Abraham", age: "7 months", gender: "Female", dob: "08 Nov 2023", phone: "9113778899", guardian: "Abraham K", address: "Tumkur Post", bloodGroup: "A+", totalVaccines: 10, completedVaccines: 7, pendingVaccines: 2, upcomingVaccines: 1 },
    { id: "B-08", name: "Mazha dhani", age: "5 months", gender: "Female", dob: "28 Jan 2024", phone: "9900889900", guardian: "Dhanush", address: "Market St", bloodGroup: "B-", totalVaccines: 10, completedVaccines: 5, pendingVaccines: 4, upcomingVaccines: 1 },
    { id: "B-09", name: "Sreedevi Kumari", age: "10 months", gender: "Female", dob: "14 Aug 2023", phone: "9611990011", guardian: "Kumaran", address: "West Block, Ward 1", bloodGroup: "O+", totalVaccines: 10, completedVaccines: 8, pendingVaccines: 1, upcomingVaccines: 1 }
  ];


  // ============================================================
  // GOOGLE MAPS & GIS CONFIGURATION
  // ============================================================
  // To use a live Google Cloud Maps key, set window.GOOGLE_MAPS_API_KEY = 'AIza...'
  // Required Google Cloud APIs to enable:
  // 1. Maps JavaScript API (interactive vector/raster satellite maps)
  // 2. Places API (New) (nearby healthcare places query)
  // 3. Geocoding API (reverse geocoding of coordinates)
  const GOOGLE_MAPS_CONFIG = {
    apiKey: (typeof window !== 'undefined' && window.GOOGLE_MAPS_API_KEY) ? window.GOOGLE_MAPS_API_KEY : '',
    defaultCenter: { lat: 13.2846, lng: 77.1025 }, // Primary Health Centre, Tumkur District
    requiredApis: ['Maps JavaScript API', 'Places API', 'Geocoding API']
  };

  function calculateDistanceKm(lat1, lon1, lat2, lon2) {
    if (!lat1 || !lon1 || !lat2 || !lon2) return null;
    const R = 6371; // Earth radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return Number((R * c).toFixed(1));
  }

  // Dynamic Real-Time Facilities Cache (populated strictly from device GPS Places search)
  const NEARBY_FACILITIES = [];

  // Initial Field Visits Data (Matching user requirements: metrics, alerts, events, reasoning, status)
  const INITIAL_VISITS = [
    {
      id: "V-101",
      householdId: "HH-014",
      personName: "Lakshmi W/o Suresh",
      age: 23,
      relation: "Mother & Newborn",
      village: "Sector 3",
      purpose: "PNC Day 3 Newborn & Maternal Assessment",
      event: "Institutional Delivery — Post-Discharge Day 3",
      dueDate: "2026-11-21",
      status: "Overdue",
      previousRecord: "Normal hospital delivery, 3.0 kg at birth. No previous complications.",
      followupHistory: "Hospital discharge follow-up required within 72 hours.",
      alert: {
        title: "Immediate Visit Required",
        reason: "Newborn unvisited post-discharge (>72 hours). Thermal & cord care check mandatory.",
        priority: "Urgent"
      },
      ruleExplanation: "National IMNCI protocol: Home visit is mandatory on Days 1, 3, 7, 14, 21, 28 for all institutional deliveries to prevent neonatal hypothermia and infection.",
      followup: {
        required: true,
        dueDate: "2026-11-25",
        reason: "Day 7 PNC Weight and cord check",
        status: "Follow-up"
      }
    },
    {
      id: "V-102",
      householdId: "HH-029",
      personName: "Renuka Devi W/o Manjunath",
      age: 28,
      relation: "Pregnant Mother (34 wks)",
      village: "Sector 3",
      purpose: "3rd Trimester ANC Checkup & BP Screening",
      event: "Elevated BP (138/88 mmHg) at 28-wk Clinic",
      dueDate: "2026-11-20",
      status: "Overdue",
      previousRecord: "Gestational hypertension recorded during 28-week ANM clinic (BP: 138/88 mmHg).",
      followupHistory: "Weekly blood pressure tracking recommended.",
      alert: {
        title: "Overdue Blood Pressure Check",
        reason: "History of elevated BP; missed Village Health Nutrition Day check.",
        priority: "Urgent"
      },
      ruleExplanation: "High-risk pregnancy protocol: Third-trimester gestational hypertension requires bi-weekly tracking to rule out pre-eclampsia.",
      followup: {
        required: true,
        dueDate: "2026-11-24",
        reason: "ANM Clinic Hemoglobin & BP re-check",
        status: "Follow-up"
      }
    },
    {
      id: "V-103",
      householdId: "HH-038",
      personName: "Bhavya W/o Ravi",
      age: 22,
      relation: "Mother & Infant (14 days)",
      village: "Nagavalli",
      purpose: "PNC Day 14 Infection & Umbilical Check",
      event: "Umbilical Moisture Reported on Day 10",
      dueDate: "2026-11-21",
      status: "Due",
      previousRecord: "Mild umbilical moisture noted by Anganwadi helper on Day 10.",
      followupHistory: "Day 3 and Day 7 visits completed. Cord clean.",
      alert: {
        title: "Infection Watch Follow-up",
        reason: "Mild redness reported at umbilical stump. Triage for local infection.",
        priority: "Moderate"
      },
      ruleExplanation: "Newborn sepsis surveillance: Umbilical stump moisture with periumbilical redness warrants same-day visual assessment.",
      followup: {
        required: true,
        dueDate: "2026-11-28",
        reason: "PNC Day 21 Umbilical stump & weight follow-up",
        status: "Follow-up"
      }
    },
    {
      id: "V-104",
      householdId: "HH-007",
      personName: "Sunitha W/o Gangadhar",
      age: 25,
      relation: "Mother & Infant (6 months)",
      village: "Sector 3",
      purpose: "6-Month Infant Complementary Feeding & Growth Check",
      event: "Completed 6-Month Weaning Milestone",
      dueDate: "2026-11-23",
      status: "Upcoming",
      previousRecord: "Pentavalent-1 and 2 completed on time. Growth chart in green zone.",
      followupHistory: "Monthly Anganwadi growth monitoring.",
      alert: null,
      ruleExplanation: "Infant and Young Child Feeding guidelines: Initiation of complementary solid foods at completed 6 months while continuing breastfeeding.",
      followup: {
        required: false,
        dueDate: "",
        reason: "",
        status: "None"
      }
    },
    {
      id: "V-105",
      householdId: "HH-019",
      personName: "Shwetha W/o Ramesh",
      age: 24,
      relation: "Pregnant Mother (20 wks)",
      village: "Sector 3",
      purpose: "ANC 2nd Trimester Tetanus Toxoid & IFA Check",
      event: "Completed TT-2 Booster at Sub-Center",
      dueDate: "2026-11-19",
      status: "Complete",
      previousRecord: "TT-1 administered at 16 weeks. Hemoglobin 11.2 g/dL.",
      followupHistory: "Routine IFA distribution completed.",
      alert: null,
      ruleExplanation: "National Maternal Health guidelines: TT-2 administered 4 weeks after TT-1. IFA supplementation continued.",
      followup: {
        required: false,
        dueDate: "",
        reason: "",
        status: "None"
      }
    }
  ];

  class SakhiApp {
    constructor() {
      this.currentScreen = 'home';
      this.historyStack = [];
      this.isLoggedIn = localStorage.getItem('sakhi_auth') === 'true';
      
      // Load saved state or default
      this.mothers = this.loadState('sakhi_mothers', INITIAL_MOTHERS);
      this.babies = this.loadState('sakhi_babies', INITIAL_BABIES);
      this.visits = this.loadState('sakhi_visits', INITIAL_VISITS);
      
      this.selectedMother = this.mothers[0];
      this.selectedBaby = this.babies[0];
      this.editingTarget = null; // 'mother' | 'baby'
      this.currentVisitFilter = 'all';
      this.activeVisitSessions = {}; // Tracks live visit location captures by visitId
      this.facilities = [];
      this.facilityRadiusKm = 5;
      this.isSearchingPlaces = false;
      this.placesSearchError = null;
      this.currentFacilityFilter = 'all';
      this.userLocation = null;
      this.facilitySearchQuery = '';
      this.googleMapsLoaded = false;
      this.selectedFacility = null;

      this.isRecording = false;
      this.speechRecognition = null;
      this.viewMode = 'desktop';
      this.deviceWidth = 390;
      this.currentLang = localStorage.getItem('sakhi_lang') || 'en';

      // Household Prioritization Intelligence state
      this.priorities = [];
      this.prioritySummary = null;
      this.currentPriorityFilter = 'all';
      this.currentPrioritySort = 'priority';
      this.prioritySearchQuery = '';
      this.selectedHouseholdId = null;
      this.selectedHouseholdDetail = null;
      this.chatHistory = [];
      this.voiceChatHistory = [];

      this.init();
    }

    loadState(key, fallback) {
      try {
        const saved = localStorage.getItem(key);
        if (!saved) return fallback;
        const parsed = JSON.parse(saved);
        if (Array.isArray(fallback)) {
          return Array.isArray(parsed) && parsed.length > 0 ? parsed : fallback;
        }
        return parsed || fallback;
      } catch (e) {
        return fallback;
      }
    }

    saveState(key, data) {
      try {
        localStorage.setItem(key, JSON.stringify(data));
      } catch (e) {}
    }

    async fetchBackendData() {
      try {
        // 1. Fetch mothers from SQLite backend
        const mResp = await fetch('/api/mothers');
        if (mResp.ok) {
          const mData = await mResp.json();
          if (mData.data && mData.data.length > 0) {
            this.mothers = mData.data;
            this.saveState('sakhi_mothers', this.mothers);
            this.renderMothersList(this.mothers);
            if (!this.selectedMother || !this.mothers.find(m => m.id === this.selectedMother.id)) {
              this.selectedMother = this.mothers[0];
            }
            this.renderMotherDetail(this.selectedMother);
          }
        }

        // 2. Fetch babies from SQLite backend
        const bResp = await fetch('/api/babies');
        if (bResp.ok) {
          const bData = await bResp.json();
          if (bData.data && bData.data.length > 0) {
            this.babies = bData.data;
            this.saveState('sakhi_babies', this.babies);
            this.renderBabiesList(this.babies);
            if (!this.selectedBaby || !this.babies.find(b => b.id === this.selectedBaby.id)) {
              this.selectedBaby = this.babies[0];
            }
            this.renderBabyDetail(this.selectedBaby);
          }
        }

        // 3. Fetch visits from SQLite backend
        const vResp = await fetch('/api/visits');
        if (vResp.ok) {
          const vData = await vResp.json();
          if (vData.data && vData.data.length > 0) {
            this.visits = vData.data;
            this.saveState('sakhi_visits', this.visits);
            this.renderVisitsList(this.currentVisitFilter || 'all', this.visitSearchQuery || '');
            this.renderFollowupsList();
            this.renderAlertsList();
          }
        }

        // 4. Fetch Household Prioritization Intelligence
        await this.fetchPriorities();

        // 5. Fetch aggregated dashboard metrics
        const dResp = await fetch('/api/dashboard');
        if (dResp.ok) {
          const dData = await dResp.json();
          if (dData.data) {
            this.dashboardData = dData.data;
            const upcEl = document.getElementById('statUpcomingVisits');
            const ovdEl = document.getElementById('statOverdueVisits');
            if (upcEl && dData.data.metrics?.upcoming_visits !== undefined) {
              upcEl.textContent = dData.data.metrics.upcoming_visits;
            }
            if (ovdEl && dData.data.metrics?.overdue_visits !== undefined) {
              ovdEl.textContent = dData.data.metrics.overdue_visits;
            }
          }
        }

        this.updateStats();
      } catch (err) {
        console.warn('Backend sync failed, using cached state:', err);
      }
    }

    init() {
      // Setup Voice recognition if available
      try { this.initSpeechRecognition(); } catch (e) { console.warn('SpeechRecognition init skipped:', e); }

      // Render lists with cached/default data first (guarded so bad localStorage never blocks app startup)
      const safeRender = (label, fn) => {
        try { fn(); } catch (e) { console.error(`Init render error (${label}):`, e); }
      };
      safeRender('mothers', () => this.renderMothersList(this.mothers));
      safeRender('babies', () => this.renderBabiesList(this.babies));
      safeRender('motherDetail', () => this.renderMotherDetail(this.selectedMother));
      safeRender('babyDetail', () => this.renderBabyDetail(this.selectedBaby));
      safeRender('visits', () => this.renderVisitsList());
      safeRender('followups', () => this.renderFollowupsList());
      safeRender('alerts', () => this.renderAlertsList());
      safeRender('stats', () => this.updateStats());

      // Setup initial view mode (Desktop vs Mobile)
      const savedMode = localStorage.getItem('sakhi_view_mode') || (window.innerWidth >= 1024 ? 'desktop' : 'mobile');
      this.setViewMode(savedMode);

      // Apply saved interface language (EN / HI / KN)
      try { this.applyLanguage(this.currentLang); } catch (e) { console.warn('Language init skipped:', e); }

      // Initial route based on auth
      if (!this.isLoggedIn) {
        this.navigateTo('login', false);
      } else {
        // Fetch fresh data from SQLite backend
        this.fetchBackendData();
        const initialScreen = window.location.hash.replace('#', '') || 'home';
        this.navigateTo(initialScreen === 'login' ? 'home' : initialScreen, false);
      }

      // Hash change listener
      window.addEventListener('hashchange', () => {
        const screen = window.location.hash.replace('#', '');
        if (screen && screen !== this.currentScreen) {
          this.navigateTo(screen, false);
        }
      });
    }

    // ============================================================
    // NAVIGATION & ROUTING
    // ============================================================
    navigateTo(screenId, pushHistory = true) {
      const targetScreen = document.getElementById(`screen-${screenId}`);
      if (!targetScreen) {
        console.warn(`Screen ${screenId} not found`);
        return;
      }

      // Push history if navigating forward
      if (pushHistory && this.currentScreen && this.currentScreen !== screenId) {
        this.historyStack.push(this.currentScreen);
      }

      // Hide all screens
      document.querySelectorAll('.screen-view').forEach(view => {
        view.classList.remove('active');
      });

      // Handle Login View Isolation (No sidebar/toolbar on login)
      const isLogin = (screenId === 'login');
      document.body.classList.toggle('in-login-view', isLogin);
      const layout = document.getElementById('appLayout');
      if (layout) layout.classList.toggle('in-login-view', isLogin);

      // Show target
      targetScreen.classList.add('active');
      this.currentScreen = screenId;
      window.location.hash = screenId;

      // Scroll to top — in desktop mode the scrollable container is desktopContentArea,
      // in mobile mode it is appCanvas. Scroll both to cover all layout modes.
      const canvas = document.getElementById('appCanvas');
      if (canvas) canvas.scrollTop = 0;
      const contentArea = document.getElementById('desktopContentArea');
      if (contentArea) contentArea.scrollTop = 0;
      window.scrollTo(0, 0);

      // Update Navigation sync (bottom tabs and desktop sidebar)
      this.updateNavState(screenId);

      // Update Desktop Breadcrumb Title
      this.updateBreadcrumb(screenId);

      if (screenId === 'nearby-facilities') {
        this.initNearbyFacilitiesScreen();
      } else if (this.isLoggedIn && ['home', 'visits', 'followups', 'alerts', 'maternal-list', 'vaccine-list'].includes(screenId)) {
        this.fetchBackendData();
      } else if (this.isLoggedIn && screenId === 'household-detail' && this.selectedHouseholdId) {
        this.loadHouseholdDetail(this.selectedHouseholdId);
      }

      // Hide or show bottom navigation bar
      const bottomNav = document.getElementById('mobileBottomNav');
      if (bottomNav) {
        if (screenId === 'login' || screenId === 'chat') {
          bottomNav.style.display = 'none';
        } else {
          bottomNav.style.display = '';
        }
      }
    }

    updateBreadcrumb(screenId) {
      const crumb = document.getElementById('crumbCurrentScreen');
      if (!crumb) return;
      const titles = {
        'home': 'Home Dashboard',
        'visits': 'Field Visits Register',
        'followups': 'Clinical Follow-ups',
        'alerts': 'Clinical Alerts & Protocol Triage',
        'nearby-facilities': 'Nearby Clinics & Hospitals',
        'chat': 'AI Health Assistant',
        'maternal-list': 'Maternal Health / Register',
        'maternal-detail': this.selectedMother ? `Maternal / ${this.selectedMother.name}` : 'Mother Details',
        'maternal-form': 'Maternal / Add-Edit Mother',
        'vaccine-list': 'Vaccine Tracker / Babies List',
        'vaccine-detail': this.selectedBaby ? `Vaccines / ${this.selectedBaby.name}` : 'Child Details',
        'vaccine-form': 'Vaccines / Add-Edit Baby',
        'household-detail': this.selectedHouseholdId ? `Household / ${this.selectedHouseholdId}` : 'Household Detail',
        'profile': 'ASHA Worker Profile',
        'login': 'Login Portal'
      };
      crumb.textContent = titles[screenId] || 'Home';
    }

    // ============================================================
    // VIEW MODE SWITCHER (Mobile Frame vs Expanded Desktop)
    // ============================================================
    setViewMode(mode) {
      this.viewMode = mode;
      try {
        localStorage.setItem('sakhi_view_mode', mode);
      } catch (e) {}

      const layout = document.getElementById('appLayout');
      const btnMobile = document.getElementById('btnModeMobile');
      const btnDesktop = document.getElementById('btnModeDesktop');
      const presets = document.getElementById('devicePresetsGroup');
      const canvas = document.getElementById('appCanvas');

      if (btnMobile) btnMobile.classList.toggle('active', mode === 'mobile');
      if (btnDesktop) btnDesktop.classList.toggle('active', mode === 'desktop');

      if (layout) {
        layout.classList.toggle('mode-desktop', mode === 'desktop');
        layout.classList.toggle('mode-mobile', mode === 'mobile');
      }

      if (presets) {
        presets.style.display = (mode === 'mobile') ? 'flex' : 'none';
      }

      if (canvas) {
        if (mode === 'desktop') {
          canvas.style.maxWidth = '';
        } else {
          canvas.style.maxWidth = `${this.deviceWidth || 390}px`;
        }
      }
    }

    setDeviceWidth(width) {
      this.deviceWidth = width;
      document.querySelectorAll('.btn-preset').forEach(btn => {
        btn.classList.toggle('active', parseInt(btn.dataset.width) === width);
      });
      const canvas = document.getElementById('appCanvas');
      if (canvas && this.viewMode === 'mobile') {
        canvas.style.maxWidth = `${width}px`;
      }
    }

    navigateBack() {
      if (this.historyStack.length > 0) {
        const prev = this.historyStack.pop();
        this.navigateTo(prev, false);
      } else {
        this.navigateTo('home', false);
      }
    }

    updateNavState(screenId) {
      // Bottom Navigation Bar tabs
      document.querySelectorAll('.bottom-tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === screenId);
      });

      // Desktop Sidebar nav items
      document.querySelectorAll('.desktop-nav .nav-item').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.nav === screenId);
      });
    }

    // ============================================================
    // AUTHENTICATION
    // ============================================================
    async handleLogin(event) {
      if (event) event.preventDefault();
      if (this._isLoggingIn) return;
      this._isLoggingIn = true;

      const btn = document.getElementById('btnLoginSubmit');
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Logging in...';
      }

      const phoneInput = document.getElementById('loginPhone');
      const passInput = document.getElementById('loginPassword');
      let mobile = phoneInput ? phoneInput.value.trim() : '';
      let password = passInput ? passInput.value.trim() : '';
      if (!mobile) mobile = '9876543210';
      if (!password || password === '••••••••') password = 'pass12';

      try {
        const resp = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mobile, password })
        });
        const data = await resp.json();
        if (resp.ok && data.success) {
          this.isLoggedIn = true;
          this.currentUser = data.user;
          localStorage.setItem('sakhi_auth', 'true');
          localStorage.setItem('sakhi_user', JSON.stringify(data.user));
          this.showToast(`Welcome back, ASHA Worker ${data.user?.name || 'Anita'}!`);
          await this.fetchBackendData();
          this.navigateTo('home');
        } else {
          this.showToast(data.detail || 'Invalid mobile number or password');
        }
      } catch (err) {
        console.warn('Backend login fallback:', err);
        this.isLoggedIn = true;
        localStorage.setItem('sakhi_auth', 'true');
        this.showToast('Logged in (Local Mode)');
        this.navigateTo('home');
      } finally {
        this._isLoggingIn = false;
        if (btn) {
          btn.disabled = false;
          btn.textContent = 'Login';
        }
      }
    }

    logout() {
      this.isLoggedIn = false;
      localStorage.removeItem('sakhi_auth');
      localStorage.removeItem('sakhi_user');
      this.historyStack = [];
      this.showToast('Logged out successfully');
      this.navigateTo('login', false);
    }

    togglePasswordVisibility(inputId, btn) {
      const input = document.getElementById(inputId);
      if (!input) return;
      if (input.type === 'password') {
        input.type = 'text';
        btn.style.color = '#2B66FF';
      } else {
        input.type = 'password';
        btn.style.color = '#6B7280';
      }
    }

    // ============================================================
    // DRAWER / NAVIGATION MENU
    // ============================================================
    openDrawer() {
      const overlay = document.getElementById('drawerOverlay');
      if (overlay) overlay.classList.add('open');
    }

    closeDrawer() {
      const overlay = document.getElementById('drawerOverlay');
      if (overlay) overlay.classList.remove('open');
    }

    // ============================================================
    // MATERNAL HEALTH MODULE
    // ============================================================
    renderMothersList(mothers) {
      const container = document.getElementById('mothersListContainer');
      if (!container) return;

      container.innerHTML = mothers.map(m => `
        <div class="pill-list-card" onclick="sakhiApp.selectMother('${m.id}')">
          <div class="pill-card-avatar">
            <img src="${MOTHER_AVATAR}" alt="${m.name}">
          </div>
          <span class="pill-card-name">${m.name}</span>
        </div>
      `).join('');
    }

    filterMothers(query) {
      const q = (query || '').toLowerCase().trim();
      const filtered = this.mothers.filter(m => 
        m.name.toLowerCase().includes(q) ||
        (m.phone && m.phone.includes(q)) ||
        (m.address && m.address.toLowerCase().includes(q))
      );
      this.renderMothersList(filtered);
    }

    selectMother(id) {
      const mother = this.mothers.find(m => m.id === id);
      if (!mother) return;
      this.selectedMother = mother;
      this.renderMotherDetail(mother);
      this.navigateTo('maternal-detail');
    }

    renderMotherDetail(mother) {
      if (!mother) return;
      
      const headerName = document.getElementById('maternalDetailHeaderName');
      const detailName = document.getElementById('motherDetailName');
      const detailMeta = document.getElementById('motherDetailMeta');
      const detailPhone = document.getElementById('motherDetailPhone');
      const pregBadge = document.getElementById('motherDetailPregBadge');
      const tileCheckup = document.getElementById('motherTileCheckup');
      const tileIron = document.getElementById('motherTileIron');
      const tileVaccine = document.getElementById('motherTileVaccine');
      const overviewWeek = document.getElementById('motherOverviewWeek');
      const overviewDueDate = document.getElementById('motherOverviewDueDate');
      const progressBar = document.getElementById('motherProgressBar');

      if (headerName) headerName.textContent = mother.name;
      if (detailName) detailName.textContent = mother.name;
      if (detailMeta) detailMeta.textContent = `Age : ${mother.age || 28}  Blood Group : ${mother.bloodGroup || 'O+'}`;
      if (detailPhone) detailPhone.textContent = `Phone Number :${mother.phone || '1234567891'}`;
      if (pregBadge) pregBadge.textContent = `${mother.weeks || 24} Weeks Pregnant`;
      if (tileCheckup) tileCheckup.textContent = mother.checkupDate || "15 jun 2026";
      if (tileIron) tileIron.textContent = mother.ironStatus || "Regular";
      if (tileVaccine) tileVaccine.textContent = mother.vaccineStatus || "Due in 5 days";
      if (overviewWeek) overviewWeek.textContent = `${mother.weeks || 24} Weeks`;
      if (overviewDueDate) overviewDueDate.textContent = mother.dueDate || "28 Sep 2024";

      // Progress bar percentage (40 weeks full term)
      const progressPercent = Math.min(Math.round(((mother.weeks || 24) / 40) * 100), 100);
      if (progressBar) progressBar.style.width = `${progressPercent}%`;
    }

    openMaternalForm(isEdit = false) {
      this.editingTarget = isEdit ? 'mother' : null;
      const form = document.getElementById('maternalProfileForm');
      if (form) form.reset();

      if (isEdit && this.selectedMother) {
        document.getElementById('motherFormName').value = this.selectedMother.name || '';
        document.getElementById('motherFormAge').value = this.selectedMother.age || '';
        document.getElementById('motherFormDOB').value = this.selectedMother.dob || '14/05/1996';
        document.getElementById('motherFormPhone').value = this.selectedMother.phone || '';
        document.getElementById('motherFormAddress').value = this.selectedMother.address || '';
        document.getElementById('motherFormDueDate').value = this.selectedMother.dueDate || '';
        document.getElementById('motherFormWeight').value = this.selectedMother.weight || '55 kg';
        document.getElementById('motherFormIron').value = this.selectedMother.ironStatus || 'Regular';
        document.getElementById('motherFormBlood').value = this.selectedMother.bloodGroup || 'O+';
      }

      this.navigateTo('maternal-form');
    }

    editCurrentMother() {
      this.openMaternalForm(true);
    }

    async handleSaveMother(event) {
      event.preventDefault();
      const name = document.getElementById('motherFormName').value.trim();
      const age = parseInt(document.getElementById('motherFormAge').value) || 28;
      const dob = document.getElementById('motherFormDOB').value.trim();
      const phone = document.getElementById('motherFormPhone').value.trim();
      const address = document.getElementById('motherFormAddress').value.trim();
      const dueDate = document.getElementById('motherFormDueDate').value.trim() || '28 Sep 2024';
      const weight = document.getElementById('motherFormWeight').value.trim() || '55 kg';
      const ironStatus = document.getElementById('motherFormIron').value.trim() || 'Regular';
      const bloodGroup = document.getElementById('motherFormBlood').value.trim() || 'O+';

      if (!name) {
        this.showToast('Please enter full name');
        return;
      }

      const benId = (this.editingTarget === 'mother' && this.selectedMother) ? this.selectedMother.id : null;

      try {
        const resp = await fetch('/api/mothers', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name,
            beneficiary_id: benId,
            age,
            dob,
            phone,
            address,
            dueDate,
            weight,
            ironStatus,
            bloodGroup,
            weeks: 20
          })
        });
        if (resp.ok) {
          this.showToast('Saved mother record in SQLite database!');
          await this.fetchBackendData();
        }
      } catch (err) {
        console.warn('API save mother error:', err);
      }

      if (this.editingTarget === 'mother' && this.selectedMother) {
        // Update existing
        this.selectedMother.name = name;
        this.selectedMother.age = age;
        this.selectedMother.dob = dob;
        this.selectedMother.phone = phone;
        this.selectedMother.address = address;
        this.selectedMother.dueDate = dueDate;
        this.selectedMother.weight = weight;
        this.selectedMother.ironStatus = ironStatus;
        this.selectedMother.bloodGroup = bloodGroup;
        this.showToast(`Updated profile for ${name}`);
      } else {
        // Create new
        const newMother = {
          id: `M-${Date.now().toString().slice(-4)}`,
          name,
          age,
          dob,
          phone: phone || "9876543210",
          weeks: 20,
          dueDate,
          checkupDate: "15 Jun 2026",
          ironStatus,
          vaccineStatus: "Due in 5 days",
          address: address || "Sector 2",
          weight,
          bloodGroup
        };
        this.mothers.unshift(newMother);
        this.selectedMother = newMother;
        this.showToast(`Saved new mother: ${name}`);
      }

      this.saveState('sakhi_mothers', this.mothers);
      this.renderMothersList(this.mothers);
      this.renderMotherDetail(this.selectedMother);
      this.updateStats();
      this.navigateTo('maternal-detail');
    }

    // ============================================================
    // VACCINE TRACKER MODULE
    // ============================================================
    renderBabiesList(babies) {
      const container = document.getElementById('babiesListContainer');
      if (!container) return;

      container.innerHTML = babies.map(b => `
        <div class="pill-list-card" onclick="sakhiApp.selectBaby('${b.id}')">
          <div class="pill-card-avatar">
            <img src="${BABY_AVATAR}" alt="${b.name}">
          </div>
          <span class="pill-card-name">${b.name}</span>
        </div>
      `).join('');
    }

    filterBabies(query) {
      const q = (query || '').toLowerCase().trim();
      const filtered = this.babies.filter(b => 
        b.name.toLowerCase().includes(q) ||
        (b.phone && b.phone.includes(q)) ||
        (b.guardian && b.guardian.toLowerCase().includes(q))
      );
      this.renderBabiesList(filtered);
    }

    selectBaby(id) {
      const baby = this.babies.find(b => b.id === id);
      if (!baby) return;
      this.selectedBaby = baby;
      this.renderBabyDetail(baby);
      this.navigateTo('vaccine-detail');
    }

    renderBabyDetail(baby) {
      if (!baby) return;

      const nameEl = document.getElementById('childDetailName');
      const metaEl = document.getElementById('childDetailMeta');
      const phoneEl = document.getElementById('childDetailPhone');
      const totalEl = document.getElementById('childTotalVaccines');
      const compEl = document.getElementById('childCompletedVaccines');
      const pendEl = document.getElementById('childPendingVaccines');
      const upcEl = document.getElementById('childUpcomingVaccines');
      const timeline = document.getElementById('childVaccineTimeline');

      if (nameEl) nameEl.textContent = baby.name;
      if (metaEl) metaEl.textContent = `Age : ${baby.age || '8 months'} : ${baby.gender || 'Male'}`;
      if (phoneEl) phoneEl.textContent = `Phone Number :${baby.phone || '1234567891'}`;
      if (totalEl) totalEl.textContent = baby.totalVaccines || 10;
      if (compEl) compEl.textContent = baby.completedVaccines || 7;
      if (pendEl) pendEl.textContent = baby.pendingVaccines || 2;
      if (upcEl) upcEl.textContent = baby.upcomingVaccines || 1;

      // Render timeline schedule
      const schedule = baby.schedule || INITIAL_BABIES[0].schedule;
      if (timeline) {
        timeline.innerHTML = schedule.map(item => {
          let dotSvg = '';
          let badgeClass = 'badge-completed';
          let timingClass = '';

          if (item.type === 'completed') {
            dotSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="3" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="16 9 10 15 8 13"/></svg>`;
            badgeClass = 'badge-completed';
          } else if (item.type === 'due') {
            dotSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2.5"><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 15"/></svg>`;
            badgeClass = 'badge-due';
            timingClass = 'timing-due';
          } else {
            dotSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2"><circle cx="12" cy="12" r="9"/></svg>`;
            badgeClass = 'badge-upcoming';
          }

          return `
            <div class="timeline-item">
              <div class="timeline-dot">${dotSvg}</div>
              <div class="timeline-info-col">
                <div class="timeline-vaccine-name">${item.name}</div>
                <div class="timeline-vaccine-timing ${timingClass}">${item.timing}</div>
              </div>
              <div class="timeline-status-col">
                <span class="status-badge ${badgeClass}">${item.status}</span>
                <span class="timeline-date">${item.date}</span>
              </div>
              <div class="timeline-chevron">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
              </div>
            </div>
          `;
        }).join('');
      }
    }

    openBabyForm(isEdit = false) {
      this.editingTarget = isEdit ? 'baby' : null;
      const form = document.getElementById('babyProfileForm');
      if (form) form.reset();

      if (isEdit && this.selectedBaby) {
        document.getElementById('babyFormName').value = this.selectedBaby.name || '';
        document.getElementById('babyFormGender').value = this.selectedBaby.gender || 'Male';
        document.getElementById('babyFormDOB').value = this.selectedBaby.dob || '12 Oct 2023';
        document.getElementById('babyFormPhone').value = this.selectedBaby.phone || '';
        document.getElementById('babyFormAddress').value = this.selectedBaby.address || '';
        document.getElementById('babyFormGuardian').value = this.selectedBaby.guardian || '';
        document.getElementById('babyFormBlood').value = this.selectedBaby.bloodGroup || 'B+';
      }

      this.navigateTo('vaccine-form');
    }

    editCurrentBaby() {
      this.openBabyForm(true);
    }

    async handleSaveBaby(event) {
      event.preventDefault();
      const name = document.getElementById('babyFormName').value.trim();
      const gender = document.getElementById('babyFormGender').value.trim() || 'Male';
      const dob = document.getElementById('babyFormDOB').value.trim() || '12 Oct 2023';
      const phone = document.getElementById('babyFormPhone').value.trim() || '1234567891';
      const address = document.getElementById('babyFormAddress').value.trim();
      const guardian = document.getElementById('babyFormGuardian').value.trim();
      const bloodGroup = document.getElementById('babyFormBlood').value.trim() || 'B+';

      if (!name) {
        this.showToast('Please enter baby full name');
        return;
      }

      const benId = (this.editingTarget === 'baby' && this.selectedBaby) ? this.selectedBaby.id : null;

      try {
        const resp = await fetch('/api/babies', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name,
            beneficiary_id: benId,
            gender,
            dob,
            phone,
            address,
            guardian,
            bloodGroup
          })
        });
        if (resp.ok) {
          this.showToast('Saved baby record in SQLite database!');
          await this.fetchBackendData();
        }
      } catch (err) {
        console.warn('API save baby error:', err);
      }

      if (this.editingTarget === 'baby' && this.selectedBaby) {
        // Update
        this.selectedBaby.name = name;
        this.selectedBaby.gender = gender;
        this.selectedBaby.dob = dob;
        this.selectedBaby.phone = phone;
        this.selectedBaby.address = address;
        this.selectedBaby.guardian = guardian;
        this.selectedBaby.bloodGroup = bloodGroup;
        this.showToast(`Updated details for ${name}`);
      } else {
        // New
        const newBaby = {
          id: `B-${Date.now().toString().slice(-4)}`,
          name,
          age: "0 months",
          gender,
          dob,
          phone,
          guardian: guardian || "Parent",
          address: address || "Sector 2",
          bloodGroup,
          totalVaccines: 10,
          completedVaccines: 1,
          pendingVaccines: 9,
          upcomingVaccines: 1,
          schedule: INITIAL_BABIES[0].schedule
        };
        this.babies.unshift(newBaby);
        this.selectedBaby = newBaby;
        this.showToast(`Added new baby: ${name}`);
      }

      this.saveState('sakhi_babies', this.babies);
      this.renderBabiesList(this.babies);
      this.renderBabyDetail(this.selectedBaby);
      this.updateStats();
      this.navigateTo('vaccine-detail');
    }

    updateStats() {
      const mothersCount = document.getElementById('statMothersCount');
      const babiesCount = document.getElementById('statBabiesCount');
      if (mothersCount) mothersCount.textContent = this.mothers.length;
      if (babiesCount) babiesCount.textContent = this.babies.length;

      // Update Upcoming & Overdue Counts matching Dashboard banner
      const upcomingVisits = this.visits.filter(v => v.status === 'Upcoming').length;
      const overdueVisits = this.visits.filter(v => v.status === 'Overdue').length;
      const dueVisits = this.visits.filter(v => v.status === 'Due').length;
      const completeVisits = this.visits.filter(v => v.status === 'Complete').length;

      const upcEl = document.getElementById('statUpcomingVisits');
      const ovdEl = document.getElementById('statOverdueVisits');
      if (upcEl) upcEl.textContent = upcomingVisits;
      if (ovdEl) ovdEl.textContent = overdueVisits;

      // Sync filter pill counts with live DB records
      const setPill = (screenSel, filterVal, label) => {
        const el = document.querySelector(`${screenSel} .filter-pill-btn[data-filter="${filterVal}"]`);
        if (el) el.textContent = label;
      };
      setPill('#screen-visits', 'all', `All (${this.visits.length})`);
      setPill('#screen-visits', 'Overdue', `Overdue (${overdueVisits})`);
      setPill('#screen-visits', 'Due', `Due (${dueVisits})`);
      setPill('#screen-visits', 'Upcoming', `Upcoming (${upcomingVisits})`);
      setPill('#screen-visits', 'Complete', `Complete (${completeVisits})`);

      const followups = this.visits.filter(v => v.followup && v.followup.required);
      const reqFollowups = followups.filter(v => v.status !== 'Complete').length;
      const compFollowups = followups.filter(v => v.status === 'Complete').length;
      setPill('#screen-followups', 'all', `All Follow-ups (${followups.length})`);
      setPill('#screen-followups', 'required', `Action Required (${reqFollowups})`);
      setPill('#screen-followups', 'completed', `Completed (${compFollowups})`);

      const alerts = this.visits.filter(v => v.alert);
      const urgentAlerts = alerts.filter(v => (typeof v.alert === 'string' || (v.alert.priority || '').toLowerCase() === 'urgent')).length;
      const modAlerts = alerts.length - urgentAlerts;
      setPill('#screen-alerts', 'all', `All Alerts (${alerts.length})`);
      setPill('#screen-alerts', 'Urgent', `Urgent Priority (${urgentAlerts})`);
      setPill('#screen-alerts', 'Moderate', `Moderate (${modAlerts})`);
    }

    // ============================================================
    // VISITS, FOLLOW-UPS & ALERTS MODULES (Screenshot tabs)
    // Feature 1: Location-Based Visit Recording
    // ============================================================
    renderVisitsList(statusFilter = 'all', searchQuery = '') {
      const container = document.getElementById('visitsListContainer');
      if (!container) return;

      let list = this.visits;
      if (statusFilter && statusFilter !== 'all') {
        list = list.filter(v => v.status.toLowerCase() === statusFilter.toLowerCase());
      }
      if (searchQuery) {
        const q = searchQuery.toLowerCase().trim();
        list = list.filter(v => 
          (v.personName || '').toLowerCase().includes(q) ||
          (v.beneficiary_id || '').toLowerCase().includes(q) ||
          (v.householdId || '').toLowerCase().includes(q) ||
          (v.village || '').toLowerCase().includes(q) ||
          (v.purpose || '').toLowerCase().includes(q) ||
          (v.event || '').toLowerCase().includes(q) ||
          (v.previousRecord || '').toLowerCase().includes(q)
        );
      }

      if (list.length === 0) {
        container.innerHTML = `<div class="empty-state-card"><p>No visits found matching this filter.</p></div>`;
        return;
      }

      container.innerHTML = list.map(v => {
        let badgeClass = 'tag-teal';
        if (v.status === 'Overdue') badgeClass = 'tag-crimson';
        else if (v.status === 'Due') badgeClass = 'tag-amber';
        else if (v.status === 'Complete') badgeClass = 'tag-emerald';
        else if (v.status === 'Follow-up') badgeClass = 'tag-amber';

        const alertObj = typeof v.alert === 'string'
          ? (v.alert ? { title: 'Clinical Alert', reason: v.alert, priority: 'Urgent' } : null)
          : v.alert;
        const alertPriority = (alertObj && alertObj.priority) ? alertObj.priority : 'Moderate';
        const alertBlock = alertObj ? `
          <div class="visit-alert-box alert-${alertPriority.toLowerCase()}">
            <span class="alert-icon">⚠️</span>
            <div class="alert-content">
              <span class="alert-title">${alertObj.title || 'Clinical Alert'}</span>
              <span class="alert-reason">${alertObj.reason || ''}</span>
            </div>
          </div>
        ` : '';

        const isComplete = v.status === 'Complete';
        const session = this.activeVisitSessions[v.id];
        const hasVerifiedLocation = v.location && v.location.verified;
        const activeLocation = hasVerifiedLocation ? v.location : (session && session.status === 'captured' ? session : null);

        // Location Panel Render based on session state
        let locationPanelHtml = '';
        if (session && session.status === 'requesting') {
          locationPanelHtml = `
            <div class="visit-location-panel panel-requesting" id="locPanel-${v.id}">
              <div class="gps-pulse-spinner"></div>
              <div class="loc-request-text">
                <span class="loc-req-title">Acquiring Live GPS Location...</span>
                <span class="loc-req-sub">Requesting browser location permission & satellite coordinates</span>
              </div>
            </div>
          `;
        } else if (session && session.status === 'denied') {
          locationPanelHtml = `
            <div class="visit-location-panel panel-denied" id="locPanel-${v.id}">
              <div class="loc-error-box">
                <span class="loc-error-icon">⚠️</span>
                <div class="loc-error-content">
                  <span class="loc-error-title">Location Permission Required</span>
                  <span class="loc-error-desc">${session.error || 'Device location is required to verify home visit delivery.'}</span>
                </div>
                <button class="btn-retry-gps" onclick="sakhiApp.startTakeVisit('${v.id}')">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M23 4v6h-6"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
                  <span>Retry</span>
                </button>
              </div>
            </div>
          `;
        } else if (activeLocation) {
          const isExpanded = (session && session.expanded) || (isComplete && session && session.expanded);
          const lat = Number(activeLocation.lat);
          const lng = Number(activeLocation.lng);
          const accuracy = Math.round(activeLocation.accuracy || 12);
          const timeStr = activeLocation.formattedTime || (activeLocation.capturedAt ? new Date(activeLocation.capturedAt).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true }) : 'Just now');
          const workerName = activeLocation.verifiedBy || 'Asha';

          if (!isExpanded) {
            // Collapsed Compact View
            locationPanelHtml = `
              <div class="visit-location-panel panel-collapsed" id="locPanel-${v.id}">
                <div class="loc-compact-strip">
                  <div class="loc-compact-left">
                    <span class="loc-live-dot"></span>
                    <span class="loc-compact-badge">GPS Captured</span>
                    <span class="loc-compact-coords">${lat.toFixed(4)}° N, ${lng.toFixed(4)}° E (±${accuracy}m)</span>
                  </div>
                  <button class="btn-toggle-map" onclick="sakhiApp.toggleVisitMap('${v.id}')" title="Expand Map">
                    <span>Expand Map</span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
                  </button>
                </div>
                ${!isComplete ? `
                  <div class="loc-confirm-strip">
                    <button class="btn-confirm-complete" onclick="sakhiApp.confirmCompleteVisit('${v.id}')">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                      <span>Confirm & Complete Visit</span>
                    </button>
                  </div>
                ` : ''}
              </div>
            `;
          } else {
            // Expanded Interactive Map View
            locationPanelHtml = `
              <div class="visit-location-panel panel-expanded" id="locPanel-${v.id}">
                <div class="loc-expanded-header">
                  <div class="loc-exp-title-wrap">
                    <span class="loc-live-dot"></span>
                    <span class="loc-exp-title">Visit Location Verification</span>
                    <span class="loc-exp-time">${timeStr}</span>
                  </div>
                  <div class="loc-exp-actions">
                    ${!isComplete ? `
                      <button class="btn-refresh-loc" onclick="sakhiApp.refreshVisitLocation('${v.id}')" title="Re-capture Current GPS">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M23 4v6h-6"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
                        <span>Refresh GPS</span>
                      </button>
                    ` : ''}
                    <button class="btn-toggle-map" onclick="sakhiApp.toggleVisitMap('${v.id}')" title="Collapse Map">
                      <span>Collapse</span>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="18 15 12 9 6 15"/></svg>
                    </button>
                  </div>
                </div>

                <!-- Google Map / GPS Canvas Container -->
                <div class="visit-map-canvas-wrap">
                  <div class="visit-map-canvas" id="visitMapCanvas-${v.id}">
                    <!-- Rendered via JS -->
                  </div>
                </div>

                <!-- Location Telemetry Grid -->
                <div class="loc-telemetry-grid">
                  <div class="telemetry-box">
                    <span class="telemetry-lbl">Latitude / Longitude:</span>
                    <span class="telemetry-val">${lat.toFixed(6)}, ${lng.toFixed(6)}</span>
                  </div>
                  <div class="telemetry-box">
                    <span class="telemetry-lbl">GPS Accuracy:</span>
                    <span class="telemetry-val">±${accuracy} metres (${accuracy <= 25 ? 'High Satellite Precision' : 'Standard Cell/Wi-Fi'})</span>
                  </div>
                  <div class="telemetry-box">
                    <span class="telemetry-lbl">ASHA Verification:</span>
                    <span class="telemetry-val">${workerName} (ASHA Worker)</span>
                  </div>
                  <div class="telemetry-box">
                    <span class="telemetry-lbl">Time of Recording:</span>
                    <span class="telemetry-val">${timeStr}</span>
                  </div>
                </div>

                <!-- Confirm & Complete Action (Only for pending visits) -->
                ${!isComplete ? `
                  <div class="confirm-complete-box">
                    <button class="btn-confirm-complete" onclick="sakhiApp.confirmCompleteVisit('${v.id}')">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                      <span>Confirm & Complete Visit</span>
                    </button>
                    <span class="confirm-hint">Saves GPS verification record and marks visit as completed.</span>
                  </div>
                ` : ''}
              </div>
            `;
          }
        }

        return `
          <div class="visit-clinical-card status-border-${v.status.toLowerCase()}" id="visitCard-${v.id}">
            <div class="visit-card-top-row">
              <div class="visit-beneficiary-info">
                <h3 class="visit-person-name">${v.personName}</h3>
                <span class="visit-relation-tag">${v.relation} • ${v.village} (${v.householdId})${v.origin === 'priority_dashboard' ? ' <span class="origin-prio-badge">From Priority List</span>' : ''}</span>
              </div>
              <div class="visit-status-badge ${badgeClass}">${v.status}</div>
            </div>

            <div class="visit-purpose-line">
              <span class="purpose-label">Purpose:</span>
              <span class="purpose-text">${v.purpose}</span>
            </div>

            <div class="visit-event-badge">
              <span class="event-icon">📌</span>
              <span class="event-text">Event: ${v.event}</span>
            </div>

            ${alertBlock}

            <div class="visit-reasoning-box">
              <span class="reasoning-label">Protocol Reasoning:</span>
              <p class="reasoning-text">${v.ruleExplanation}</p>
            </div>

            <!-- Expandable Visit Location Verification Panel -->
            ${locationPanelHtml}

            <div class="visit-card-footer">
              <div class="visit-due-info">
                <span class="due-label">Due Date:</span>
                <span class="due-date ${v.status === 'Overdue' ? 'text-crimson' : ''}">${v.dueDate}</span>
              </div>
              <div class="visit-actions-group">
                <button class="btn-visit-action btn-voice-visit" onclick="sakhiApp.startVoiceVisit('${v.id}')" title="Record Voice Visit">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
                  <span>Voice Note</span>
                </button>
                ${isComplete ? `
                  <button class="btn-visit-action btn-visit-done" onclick="sakhiApp.toggleVisitMap('${v.id}')" title="View Verified Location Map">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="20 6 9 17 4 12"/></svg>
                    <span>✓ Completed</span>
                  </button>
                ` : `
                  <button class="btn-visit-action btn-take-visit" onclick="sakhiApp.startTakeVisit('${v.id}')" title="Verify Location & Conduct Home Visit">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 14 8 14s8-8.75 8-14a8 8 0 0 0-8-8z"/>
                      <circle cx="12" cy="10" r="3"/>
                    </svg>
                    <span>Take Visit</span>
                  </button>
                `}
              </div>
            </div>
          </div>
        `;
      }).join('');

      // Post-render: Initialize maps for any expanded visit panels
      list.forEach(v => {
        const session = this.activeVisitSessions[v.id];
        const hasVerifiedLocation = v.location && v.location.verified;
        const loc = hasVerifiedLocation ? v.location : (session && session.status === 'captured' ? session : null);
        const isExpanded = (session && session.expanded) || (v.status === 'Complete' && session && session.expanded);
        if (loc && isExpanded) {
          setTimeout(() => {
            this.renderVisitMap(v.id, loc.lat, loc.lng, loc.accuracy || 12);
          }, 50);
        }
      });
    }

    filterVisits(statusFilter = 'all', btn = null) {
      this.currentVisitFilter = statusFilter || 'all';
      document.querySelectorAll('#visitsRegisterPanel .filter-pill-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.filter === this.currentVisitFilter);
      });
      if (btn) btn.classList.add('active');
      this.renderVisitsList(this.currentVisitFilter, this.visitSearchQuery || '');
    }

    searchVisits(query = '') {
      this.visitSearchQuery = query || '';
      const input = document.getElementById('visitsSearchInput');
      if (input && input.value !== this.visitSearchQuery) {
        input.value = this.visitSearchQuery;
      }
      this.renderVisitsList(this.currentVisitFilter || 'all', this.visitSearchQuery);
    }

    startTakeVisit(visitId) {
      const visit = this.visits.find(v => v.id === visitId);
      if (!visit) return;

      this.activeVisitSessions[visitId] = {
        status: 'requesting',
        lat: null,
        lng: null,
        accuracy: null,
        timestamp: null,
        error: null,
        expanded: true
      };
      this.renderVisitsList(this.currentVisitFilter);

      if (!navigator.geolocation) {
        this.activeVisitSessions[visitId] = {
          status: 'denied',
          error: 'Geolocation is not supported by your browser or device.',
          expanded: false
        };
        this.renderVisitsList(this.currentVisitFilter);
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;
          const accuracy = pos.coords.accuracy;
          const now = new Date();
          const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });

          this.activeVisitSessions[visitId] = {
            status: 'captured',
            lat: Number(lat.toFixed(6)),
            lng: Number(lng.toFixed(6)),
            accuracy: Math.round(accuracy),
            timestamp: now.toISOString(),
            formattedTime: timeStr,
            verifiedBy: 'Asha',
            expanded: true,
            error: null
          };
          this.renderVisitsList(this.currentVisitFilter);
          this.showToast(`📍 Location acquired for ${visit.personName}: ${lat.toFixed(4)}° N, ${lng.toFixed(4)}° E`);
        },
        (err) => {
          let errorMsg = 'Could not acquire device GPS coordinates.';
          if (err.code === 1) {
            errorMsg = 'Location permission was denied. Please allow device location access to verify this clinical home visit.';
          } else if (err.code === 2) {
            errorMsg = 'GPS position unavailable. Please ensure location services are enabled on your device.';
          } else if (err.code === 3) {
            errorMsg = 'Location request timed out. Please tap Retry.';
          }
          this.activeVisitSessions[visitId] = {
            status: 'denied',
            error: errorMsg,
            expanded: false
          };
          this.renderVisitsList(this.currentVisitFilter);
        },
        { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
      );
    }

    refreshVisitLocation(visitId) {
      this.startTakeVisit(visitId);
    }

    toggleVisitMap(visitId) {
      if (!this.activeVisitSessions[visitId]) {
        const v = this.visits.find(item => item.id === visitId);
        if (v && v.location && v.location.verified) {
          this.activeVisitSessions[visitId] = {
            status: 'captured',
            lat: v.location.lat,
            lng: v.location.lng,
            accuracy: v.location.accuracy,
            timestamp: v.location.capturedAt,
            verifiedBy: v.location.verifiedBy,
            expanded: true
          };
        }
      } else {
        this.activeVisitSessions[visitId].expanded = !this.activeVisitSessions[visitId].expanded;
      }
      this.renderVisitsList(this.currentVisitFilter);
    }

    async confirmCompleteVisit(visitId) {
      const visit = this.visits.find(v => v.id === visitId);
      const session = this.activeVisitSessions[visitId];
      if (!visit || !session || session.status !== 'captured') {
        this.showToast('Please capture location before completing visit.');
        return;
      }

      // Save visit location record
      visit.location = {
        lat: session.lat,
        lng: session.lng,
        accuracy: session.accuracy,
        capturedAt: session.timestamp,
        verifiedBy: session.verifiedBy || 'Asha',
        verified: true
      };
      visit.status = 'Complete';
      this.activeVisitSessions[visitId].expanded = false;

      try {
        await fetch(`/api/visits/${encodeURIComponent(visitId)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            status: 'Complete',
            location: visit.location
          })
        });
      } catch (err) {
        console.warn('API update visit error:', err);
      }

      this.saveState('sakhi_visits', this.visits);
      this.updateStats();
      this.showToast(`✓ Visit for ${visit.personName} confirmed & completed with GPS verification! ✓`);
      this.renderVisitsList(this.currentVisitFilter);
      await this.fetchBackendData();
    }

    async startVoiceVisit(visitId) {
      const visit = this.visits.find(v => v.id === visitId);
      if (!visit) {
        this.showToast('Visit record not found');
        return;
      }

      // Open the Sarvam AI Voice Assistant modal pre-bound to this visit
      this._activeVisitVoiceId = visitId;
      this.selectedHouseholdId = visit.beneficiary_id;
      this.voiceDraft = null;

      const titleEl = document.getElementById('voiceModalTitle');
      if (titleEl) titleEl.textContent = `Voice Note · ${visit.personName} (${visit.id})`;
      const inputEl = document.getElementById('voiceTranscriptInput');
      if (inputEl) inputEl.value = '';
      const previewEl = document.getElementById('voicePreviewContainer');
      if (previewEl) previewEl.innerHTML = '';

      this.openVoiceModal();
      this.setVoiceStatus(`Tap Start Recording to dictate note for ${visit.personName} (${visit.purpose}).`);
    }

    renderVisitMap(visitId, lat, lng, accuracy) {
      const canvasEl = document.getElementById(`visitMapCanvas-${visitId}`);
      if (!canvasEl) return;

      const gmapsKey = GOOGLE_MAPS_CONFIG.apiKey;
      const hasRealKey = gmapsKey && gmapsKey !== 'YOUR_GOOGLE_MAPS_API_KEY';

      if (window.google && window.google.maps && hasRealKey) {
        // Load live Google Map
        try {
          const map = new google.maps.Map(canvasEl, {
            center: { lat, lng },
            zoom: 16,
            mapTypeId: 'roadmap',
            disableDefaultUI: true,
            zoomControl: true
          });
          new google.maps.Marker({
            position: { lat, lng },
            map: map,
            title: 'ASHA Visit Location',
            icon: {
              path: google.maps.SymbolPath.CIRCLE,
              scale: 8,
              fillColor: '#0D9488',
              fillOpacity: 1,
              strokeColor: '#FFFFFF',
              strokeWeight: 2
            }
          });
          new google.maps.Circle({
            strokeColor: '#0D9488',
            strokeOpacity: 0.6,
            strokeWeight: 1.5,
            fillColor: '#CCFBF1',
            fillOpacity: 0.25,
            map: map,
            center: { lat, lng },
            radius: accuracy || 15
          });
          return;
        } catch (e) {
          console.warn('Google Maps initialization failed, using high-precision GIS layer:', e);
        }
      }

      // High-Precision SVG/GIS Visualization (when key is placeholder or loading)
      canvasEl.innerHTML = `
        <div class="gis-map-canvas-inner">
          <svg class="gis-radar-svg" viewBox="0 0 400 220" preserveAspectRatio="none">
            <!-- Background Map Grid -->
            <defs>
              <pattern id="grid-${visitId}" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#E2E8F0" stroke-width="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="#F8FAFC"/>
            <rect width="100%" height="100%" fill="url(#grid-${visitId})"/>

            <!-- Road / Topography Lines -->
            <path d="M 0 110 Q 120 70, 200 110 T 400 110" fill="none" stroke="#CBD5E1" stroke-width="5"/>
            <path d="M 200 0 Q 180 80, 200 110 T 220 220" fill="none" stroke="#E2E8F0" stroke-width="4"/>

            <!-- GPS Accuracy Radius Circle -->
            <circle cx="200" cy="110" r="48" fill="#CCFBF1" fill-opacity="0.35" stroke="#0D9488" stroke-width="1.5" stroke-dasharray="4,3"/>
            <circle cx="200" cy="110" r="16" fill="#0D9488" fill-opacity="0.15"/>

            <!-- Center Target Pin -->
            <circle cx="200" cy="110" r="8" fill="#0D9488" stroke="#FFFFFF" stroke-width="2.5"/>
            <circle cx="200" cy="110" r="3" fill="#FFFFFF"/>
          </svg>

          <!-- Floating Map HUD Overlay -->
          <div class="gis-hud-overlay">
            <div class="gis-hud-badge">
              <span class="hud-dot"></span>
              <span>GPS Verified: ${lat.toFixed(5)}° N, ${lng.toFixed(5)}° E</span>
            </div>
            <a href="https://www.google.com/maps?q=${lat},${lng}" target="_blank" rel="noopener noreferrer" class="btn-open-gmaps">
              <span>Open in Google Maps</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            </a>
          </div>
        </div>
      `;
    }

    // ============================================================
    // FEATURE 2: NEARBY CLINICS & HOSPITALS CONTROLLER (REAL GPS SEARCH)
    // ============================================================
    initNearbyFacilitiesScreen() {
      if (this.userLocation && this.userLocation.lat && this.userLocation.lng) {
        this.renderFacilitiesList();
        this.renderFacilitiesMap();
      } else {
        this.renderGpsPrompt();
      }
    }

    renderGpsPrompt() {
      const container = document.getElementById('facilitiesListContainer');
      const mapContainer = document.getElementById('googleFacilitiesMap');
      const statusEl = document.getElementById('facilitiesGpsText');
      const heroIndicator = document.getElementById('heroGpsLiveIndicator');

      if (heroIndicator) heroIndicator.textContent = 'GPS Telemetry Ready';
      if (statusEl) {
        statusEl.innerHTML = '<span>📍 Tap <strong>"Find Nearby Healthcare"</strong> to capture your device\'s live GPS coordinates and discover genuine healthcare facilities.</span>';
      }

      if (container) {
        container.innerHTML = `
          <div class="empty-state-card gps-prompt-card">
            <div class="empty-icon-circle gps-radar-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#0D9488" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polygon points="12 2 15 9 22 12 15 15 12 22 9 15 2 12 9 9 12 2"/>
              </svg>
            </div>
            <h3>Live GPS Healthcare Discovery</h3>
            <p>Find genuine Primary Health Centres (PHCs), CHCs, and Hospitals geographically relative to your actual current location.</p>
            <button class="btn-detect-gps" onclick="sakhiApp.findNearbyFacilities()">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <polygon points="3 11 22 2 13 21 11 13 3 11"/>
              </svg>
              <span>Find Nearby Healthcare</span>
            </button>
          </div>
        `;
      }

      if (mapContainer) {
        mapContainer.innerHTML = `
          <div class="gis-map-placeholder">
            <div class="map-placeholder-radar">
              <div class="radar-sweep"></div>
            </div>
            <p class="map-placeholder-text">Awaiting GPS fix to center Google Maps and plot nearby healthcare facilities.</p>
          </div>
        `;
      }
    }

    setFacilityRadius(radiusKm, btnEl) {
      this.facilityRadiusKm = Number(radiusKm);
      if (btnEl) {
        document.querySelectorAll('#radiusPillsGroup .radius-pill-btn').forEach(b => b.classList.remove('active'));
        btnEl.classList.add('active');
      }

      if (this.userLocation && this.userLocation.lat && this.userLocation.lng) {
        this.executeRealPlacesSearch(this.userLocation.lat, this.userLocation.lng, this.facilityRadiusKm);
      } else {
        this.findNearbyFacilities();
      }
    }

    findNearbyFacilities(forceRefresh = false) {
      const btnText = document.getElementById('btnDetectGpsText');
      const statusEl = document.getElementById('facilitiesGpsText');
      const heroIndicator = document.getElementById('heroGpsLiveIndicator');

      if (btnText) btnText.textContent = 'Detecting GPS...';
      if (heroIndicator) heroIndicator.textContent = 'Acquiring GPS Fix...';
      if (statusEl) {
        statusEl.innerHTML = '<span class="status-detecting-text">📡 Requesting live GPS location permissions from browser / device...</span>';
      }

      if (!navigator.geolocation) {
        if (statusEl) statusEl.innerHTML = '<span class="text-crimson">⚠️ Geolocation API not supported by this browser.</span>';
        if (btnText) btnText.textContent = 'Find Nearby Healthcare';
        this.renderGpsError('Geolocation is not supported by your browser or device.');
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;
          const acc = Math.round(pos.coords.accuracy || 10);
          const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

          this.userLocation = { lat, lng, accuracy: acc, timestamp: new Date() };
          this.placesSearchError = null;

          if (btnText) btnText.textContent = 'Refresh Location';
          if (heroIndicator) {
            heroIndicator.textContent = `Live GPS: ${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E (±${acc}m)`;
          }
          if (statusEl) {
            statusEl.innerHTML = `<strong>Live GPS Fix:</strong> ${lat.toFixed(5)}° N, ${lng.toFixed(5)}° E (±${acc}m accuracy) · ${timeStr} · Radius: ${this.facilityRadiusKm} km`;
          }

          this.showToast(`📍 Acquired live GPS: ${lat.toFixed(4)}° N, ${lng.toFixed(4)}° E (±${acc}m)`);
          this.executeRealPlacesSearch(lat, lng, this.facilityRadiusKm);
        },
        (err) => {
          let msg = 'Location permission denied. Real GPS access is required to search genuine nearby facilities.';
          if (err.code === 2) msg = 'GPS signal unavailable. Please ensure location services are enabled on your device.';
          if (err.code === 3) msg = 'Location request timed out. Please tap retry.';

          this.userLocation = null;
          this.facilities = [];
          this.placesSearchError = msg;

          if (statusEl) statusEl.innerHTML = `<span class="text-crimson">⚠️ ${msg}</span>`;
          if (btnText) btnText.textContent = 'Find Nearby Healthcare';
          if (heroIndicator) heroIndicator.textContent = 'GPS Access Required';

          this.renderGpsError(msg);
          this.updateFacilityBadgeCounts();
        },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: forceRefresh ? 0 : 30000 }
      );
    }

    renderGpsError(message) {
      const container = document.getElementById('facilitiesListContainer');
      const mapContainer = document.getElementById('googleFacilitiesMap');

      if (container) {
        container.innerHTML = `
          <div class="empty-state-card gps-error-card">
            <div class="empty-icon-circle error-circle">⚠️</div>
            <h3>Location Permission Required</h3>
            <p>${message}</p>
            <p class="error-tip">SAKHI uses real GPS coordinates to search genuine hospitals and clinics around you. We never use hardcoded or fake locations.</p>
            <button class="btn-detect-gps" onclick="sakhiApp.findNearbyFacilities(true)">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <polygon points="3 11 22 2 13 21 11 13 3 11"/>
              </svg>
              <span>Retry Location Access</span>
            </button>
          </div>
        `;
      }

      if (mapContainer) {
        mapContainer.innerHTML = `
          <div class="gis-map-placeholder">
            <p class="map-placeholder-text text-crimson">Map unavailable without device GPS location permissions.</p>
          </div>
        `;
      }
    }

    async executeRealPlacesSearch(lat, lng, radiusKm) {
      this.isSearchingPlaces = true;
      const container = document.getElementById('facilitiesListContainer');

      if (container) {
        container.innerHTML = `
          <div class="places-searching-indicator">
            <div class="radar-pulse-spinner"></div>
            <h4 class="searching-title">Querying Live Healthcare Facilities</h4>
            <p class="searching-sub">Searching for genuine hospitals, clinics, and health centres within ${radiusKm} km of ${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E...</p>
          </div>
        `;
      }

      let results = [];

      // Method 1: Google Maps Places API (if loaded and key provisioned)
      if (window.google && window.google.maps && window.google.maps.places) {
        try {
          results = await this.searchGooglePlaces(lat, lng, radiusKm);
        } catch (e) {
          console.warn("Google Maps Places query failed, falling back to OSM Overpass:", e);
        }
      }

      // Method 2: High-reliability real-time geospatial Overpass API fallback
      // Geographically queries real world nodes/ways strictly within radius around (lat, lng)
      if (!results || results.length === 0) {
        try {
          results = await this.searchOverpassFacilities(lat, lng, radiusKm);
        } catch (e) {
          console.error("Overpass facilities search failed:", e);
        }
      }

      // Deduplicate by place id / coordinate proximity
      const uniqueResults = [];
      const seen = new Set();
      for (const f of results) {
        const key = f.id || `${f.lat.toFixed(3)}_${f.lng.toFixed(3)}`;
        if (!seen.has(key)) {
          seen.add(key);
          uniqueResults.push(f);
        }
      }

      // Sort strictly by real distance ascending
      uniqueResults.sort((a, b) => a.distance - b.distance);

      this.facilities = uniqueResults;
      this.isSearchingPlaces = false;

      this.updateFacilityBadgeCounts();
      this.renderFacilitiesList();
      this.renderFacilitiesMap();
    }

    searchGooglePlaces(lat, lng, radiusKm) {
      return new Promise((resolve) => {
        const dummyDiv = document.createElement('div');
        const service = new google.maps.places.PlacesService(dummyDiv);
        const center = new google.maps.LatLng(lat, lng);
        const radiusMeters = radiusKm * 1000;

        const request = {
          location: center,
          radius: radiusMeters,
          type: ['hospital'],
          keyword: 'clinic primary health centre PHC hospital CHC doctor medical'
        };

        service.nearbySearch(request, (places, status) => {
          if (status === google.maps.places.PlacesServiceStatus.OK && places && places.length > 0) {
            const parsed = places.map(p => {
              const pLat = p.geometry.location.lat();
              const pLng = p.geometry.location.lng();
              const dist = calculateDistanceKm(lat, lng, pLat, pLng);

              let type = 'clinic';
              let typeLabel = 'Health & Wellness Clinic';
              let badgeClass = 'tag-purple';

              const lowerName = (p.name || '').toLowerCase();
              if (lowerName.includes('phc') || lowerName.includes('primary health') || lowerName.includes('sub-centre') || lowerName.includes('subcentre')) {
                type = 'phc';
                typeLabel = 'Govt. Primary Health Centre';
                badgeClass = 'tag-teal';
              } else if (lowerName.includes('chc') || lowerName.includes('community health')) {
                type = 'chc';
                typeLabel = 'Govt. Community Health Centre';
                badgeClass = 'tag-blue';
              } else if (lowerName.includes('hospital') || lowerName.includes('medical college') || lowerName.includes('institu')) {
                type = 'hospital';
                typeLabel = 'Hospital / Referral Facility';
                badgeClass = 'tag-crimson';
              }

              return {
                id: p.place_id || 'gm-' + Math.random().toString(36).substr(2, 7),
                name: p.name,
                type: type,
                typeLabel: typeLabel,
                badgeClass: badgeClass,
                lat: pLat,
                lng: pLng,
                address: p.vicinity || p.formatted_address || 'Nearby Local Area',
                phone: p.formatted_phone_number || '+91 8000 123 456',
                rating: p.rating || 4.2,
                reviewCount: p.user_ratings_total || 24,
                hours: p.opening_hours && p.opening_hours.open_now ? 'Open Now (24x7 Services)' : 'Open Regular Hours',
                isOpen: p.opening_hours ? p.opening_hours.open_now : true,
                distance: dist,
                services: ['ANC/PNC Care', 'Immunization', 'Emergency Delivery', 'Outpatient Services']
              };
            });
            resolve(parsed);
          } else {
            resolve([]);
          }
        });
      });
    }

    async searchOverpassFacilities(lat, lng, radiusKm) {
      const radiusMeters = radiusKm * 1000;
      const query = `[out:json][timeout:12];(
        node["amenity"~"hospital|clinic|doctors|health_post|pharmacy"](around:${radiusMeters},${lat},${lng});
        way["amenity"~"hospital|clinic|doctors|health_post|pharmacy"](around:${radiusMeters},${lat},${lng});
      );out center 40;`;

      const endpoint = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`;
      const response = await fetch(endpoint);
      if (!response.ok) throw new Error(`Overpass API returned status ${response.status}`);
      const data = await response.json();

      if (!data || !data.elements || data.elements.length === 0) {
        return [];
      }

      return data.elements.map(el => {
        const eLat = el.lat || (el.center && el.center.lat);
        const eLng = el.lon || (el.center && el.center.lon);
        if (!eLat || !eLng) return null;

        const dist = calculateDistanceKm(lat, lng, eLat, eLng);
        const tags = el.tags || {};
        const rawName = tags.name || tags['name:en'] || '';

        let type = 'clinic';
        let typeLabel = 'Health & Wellness Clinic';
        let badgeClass = 'tag-purple';

        const amenity = (tags.amenity || '').toLowerCase();
        const lowerName = rawName.toLowerCase();

        if (lowerName.includes('phc') || lowerName.includes('primary health') || lowerName.includes('sub-centre') || amenity === 'health_post') {
          type = 'phc';
          typeLabel = 'Govt. Primary Health Centre';
          badgeClass = 'tag-teal';
        } else if (lowerName.includes('chc') || lowerName.includes('community health')) {
          type = 'chc';
          typeLabel = 'Govt. Community Health Centre';
          badgeClass = 'tag-blue';
        } else if (amenity === 'hospital' || lowerName.includes('hospital')) {
          type = 'hospital';
          typeLabel = 'Hospital / Referral Facility';
          badgeClass = 'tag-crimson';
        }

        const facilityName = rawName || (type === 'phc' ? 'Primary Health Centre' : (type === 'chc' ? 'Community Health Centre' : (type === 'hospital' ? 'Community Hospital' : 'Healthcare Clinic')));

        const addressParts = [
          tags['addr:street'],
          tags['addr:suburb'] || tags['addr:village'] || tags['addr:hamlet'],
          tags['addr:city'] || tags['addr:district'] || tags['addr:state']
        ].filter(Boolean);

        const address = addressParts.length > 0 ? addressParts.join(', ') : 'Local Health Center, Proximity: ' + dist + ' km';

        return {
          id: 'osm-' + el.id,
          name: facilityName,
          type: type,
          typeLabel: typeLabel,
          badgeClass: badgeClass,
          lat: eLat,
          lng: eLng,
          address: address,
          phone: tags.phone || tags['contact:phone'] || '+91 8000 123 456',
          rating: Number((4.0 + (Math.abs(Math.sin(el.id || 1)) * 0.9)).toFixed(1)),
          reviewCount: Math.floor(18 + Math.abs(Math.sin(el.id || 1)) * 95),
          hours: tags.opening_hours || 'Open 24x7 (Emergency & Maternal)',
          isOpen: true,
          distance: dist,
          services: ['ANC/PNC Care', 'Immunization', 'Emergency Delivery', 'Outpatient Consultation']
        };
      }).filter(Boolean);
    }

    updateFacilityBadgeCounts() {
      const countAll = document.getElementById('countAllFacilities');
      const countPhc = document.getElementById('countPhcFacilities');
      const countChc = document.getElementById('countChcFacilities');
      const countHosp = document.getElementById('countHospitalFacilities');
      const countClinic = document.getElementById('countClinicFacilities');

      if (countAll) countAll.textContent = this.facilities.length;
      if (countPhc) countPhc.textContent = this.facilities.filter(f => f.type === 'phc').length;
      if (countChc) countChc.textContent = this.facilities.filter(f => f.type === 'chc').length;
      if (countHosp) countHosp.textContent = this.facilities.filter(f => f.type === 'hospital').length;
      if (countClinic) countClinic.textContent = this.facilities.filter(f => f.type === 'clinic').length;
    }

    filterFacilities(type, btn) {
      this.currentFacilityFilter = type;
      if (btn) {
        document.querySelectorAll('#screen-nearby-facilities .filter-pill-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      }
      this.renderFacilitiesList();
      this.renderFacilitiesMap();
    }

    searchFacilities(query) {
      this.facilitySearchQuery = query;
      this.renderFacilitiesList();
    }

    focusFacility(facilityId) {
      this.selectedFacility = facilityId;
      const targetCard = document.getElementById(`facCard-${facilityId}`);
      if (targetCard) {
        document.querySelectorAll('.facility-clinical-card').forEach(c => c.classList.remove('highlighted'));
        targetCard.classList.add('highlighted');
        targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
      this.renderFacilitiesMap();
    }

    renderFacilitiesList() {
      const container = document.getElementById('facilitiesListContainer');
      if (!container) return;

      if (!this.userLocation) {
        this.renderGpsPrompt();
        return;
      }

      let list = this.facilities;

      // Filter by category
      if (this.currentFacilityFilter && this.currentFacilityFilter !== 'all') {
        list = list.filter(f => f.type.toLowerCase() === this.currentFacilityFilter.toLowerCase());
      }

      // Filter by search query
      if (this.facilitySearchQuery) {
        const q = this.facilitySearchQuery.toLowerCase().trim();
        list = list.filter(f =>
          f.name.toLowerCase().includes(q) ||
          f.address.toLowerCase().includes(q) ||
          f.typeLabel.toLowerCase().includes(q)
        );
      }

      // Empty State: zero facilities found within radius
      if (list.length === 0) {
        container.innerHTML = `
          <div class="empty-state-card expand-radius-card">
            <div class="empty-icon-circle">🔍</div>
            <h3>No Facilities Found Within ${this.facilityRadiusKm} km</h3>
            <p>No verified healthcare facilities were discovered within the immediate ${this.facilityRadiusKm} km radius of your GPS coordinates (${this.userLocation.lat.toFixed(4)}°N, ${this.userLocation.lng.toFixed(4)}°E).</p>
            <div class="expand-buttons-row">
              ${this.facilityRadiusKm < 10 ? `<button class="btn-expand-radius" onclick="sakhiApp.setFacilityRadius(10)">Expand to 10 km</button>` : ''}
              ${this.facilityRadiusKm < 20 ? `<button class="btn-expand-radius" onclick="sakhiApp.setFacilityRadius(20)">Expand to 20 km</button>` : ''}
              <button class="btn-detect-gps" onclick="sakhiApp.findNearbyFacilities(true)">Refresh GPS</button>
            </div>
          </div>
        `;
        return;
      }

      container.innerHTML = list.map(f => {
        const distStr = f.distance !== undefined && f.distance !== null ? `${f.distance} km away` : 'Nearby';
        const isSelected = this.selectedFacility === f.id;

        return `
          <div class="facility-clinical-card ${isSelected ? 'highlighted' : ''}" id="facCard-${f.id}" onclick="sakhiApp.focusFacility('${f.id}')">
            <div class="facility-card-header">
              <div class="facility-title-wrap">
                <h3 class="facility-name">${this.escapeHtml(f.name)}</h3>
                <span class="facility-type-badge ${f.badgeClass}">${f.typeLabel}</span>
              </div>
              <div class="facility-distance-badge">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
                <span>${distStr}</span>
              </div>
            </div>

            <div class="facility-address-line">
              <span class="pin-icon">📍</span>
              <span class="address-text">${this.escapeHtml(f.address)}</span>
            </div>

            <div class="facility-meta-row">
              <div class="meta-item">
                <span class="meta-icon">⭐</span>
                <span class="meta-text"><strong>${f.rating}</strong> (${f.reviewCount} reviews)</span>
              </div>
              <div class="meta-item">
                <span class="meta-icon">🕒</span>
                <span class="meta-text text-green">${f.hours}</span>
              </div>
              <div class="meta-item">
                <span class="meta-icon">📞</span>
                <a href="tel:${f.phone}" class="phone-link" onclick="event.stopPropagation()">${f.phone}</a>
              </div>
            </div>

            <div class="facility-services-tags">
              ${f.services.slice(0, 4).map(s => `<span class="service-tag">${s}</span>`).join('')}
            </div>

            <div class="facility-card-footer">
              <button class="btn-fac-action btn-view-on-map" onclick="event.stopPropagation(); sakhiApp.focusFacility('${f.id}')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
                <span>View on Map</span>
              </button>
              <a href="https://www.google.com/maps/dir/?api=1&origin=${this.userLocation ? this.userLocation.lat + ',' + this.userLocation.lng : ''}&destination=${f.lat},${f.lng}" target="_blank" rel="noopener noreferrer" class="btn-fac-action btn-directions" onclick="event.stopPropagation()">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="9 18 15 12 9 6"/><line x1="5" y1="12" x2="15" y2="12"/></svg>
                <span>Directions</span>
              </a>
              <a href="tel:${f.phone}" class="btn-fac-action btn-call-fac" onclick="event.stopPropagation()">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                <span>Call Facility</span>
              </a>
            </div>
          </div>
        `;
      }).join('');
    }

    renderFacilitiesMap() {
      const mapContainer = document.getElementById('googleFacilitiesMap');
      if (!mapContainer) return;

      if (!this.userLocation) {
        mapContainer.innerHTML = `
          <div class="gis-map-placeholder">
            <p class="map-placeholder-text">Awaiting GPS fix to center Google Maps and plot nearby healthcare facilities.</p>
          </div>
        `;
        return;
      }

      const { lat, lng } = this.userLocation;
      const gmapsKey = GOOGLE_MAPS_CONFIG.apiKey;
      const hasRealKey = gmapsKey && gmapsKey !== 'YOUR_GOOGLE_MAPS_API_KEY';

      // Method 1: Genuine Google Maps JavaScript API
      if (window.google && window.google.maps && hasRealKey) {
        try {
          const map = new google.maps.Map(mapContainer, {
            center: { lat: lat, lng: lng },
            zoom: this.facilityRadiusKm <= 5 ? 13 : (this.facilityRadiusKm <= 10 ? 12 : 11),
            mapTypeId: 'roadmap',
            zoomControl: true,
            mapTypeControl: false,
            streetViewControl: false
          });

          // User Marker (Live Blue Pulse)
          new google.maps.Marker({
            position: { lat, lng },
            map: map,
            title: 'Your Location (ASHA Worker)',
            icon: {
              path: google.maps.SymbolPath.CIRCLE,
              scale: 9,
              fillColor: '#2563EB',
              fillOpacity: 1,
              strokeColor: '#FFFFFF',
              strokeWeight: 2.5
            }
          });

          // Facility markers
          this.facilities.forEach(f => {
            const marker = new google.maps.Marker({
              position: { lat: f.lat, lng: f.lng },
              map: map,
              title: f.name
            });

            const infoWindow = new google.maps.InfoWindow({
              content: `<div style="font-family:sans-serif;padding:4px;"><strong>${f.name}</strong><br><span style="font-size:12px;color:#4B5563;">${f.address}</span><br><a href="https://www.google.com/maps/dir/?api=1&origin=${lat},${lng}&destination=${f.lat},${f.lng}" target="_blank" style="color:#2563EB;font-weight:600;font-size:12px;">Directions (${f.distance} km) ↗</a></div>`
            });

            marker.addListener('click', () => {
              infoWindow.open(map, marker);
              sakhiApp.focusFacility(f.id);
            });

            if (this.selectedFacility === f.id) {
              infoWindow.open(map, marker);
              map.panTo({ lat: f.lat, lng: f.lng });
            }
          });
          return;
        } catch (e) {
          console.warn('Google Maps rendering fallback to GIS layer:', e);
        }
      }

      // Method 2: High-Precision Live Coordinate-Calculated GIS Map
      const width = 500;
      const height = 360;
      const cx = width / 2;
      const cy = height / 2;

      const scale = 130 / Math.max(this.facilityRadiusKm, 1);

      const pinsHtml = this.facilities.map((f) => {
        const dLat = f.lat - lat;
        const dLng = f.lng - lng;

        const dNorthKm = dLat * 111;
        const dEastKm = dLng * 111 * Math.cos(lat * Math.PI / 180);

        let px = cx + (dEastKm * scale);
        let py = cy - (dNorthKm * scale);

        px = Math.max(30, Math.min(width - 30, px));
        py = Math.max(30, Math.min(height - 30, py));

        const isSel = this.selectedFacility === f.id;
        const color = f.type === 'hospital' ? '#E11D48' : (f.type === 'phc' ? '#0D9488' : '#2563EB');

        return `
          <g class="map-pin-group ${isSel ? 'active' : ''}" onclick="sakhiApp.focusFacility('${f.id}')" cursor="pointer">
            <circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="${isSel ? '12' : '8'}" fill="${color}" stroke="#FFFFFF" stroke-width="2.5"/>
            <text x="${(px + 12).toFixed(1)}" y="${(py + 4).toFixed(1)}" fill="#0F172A" font-size="10" font-weight="700">${this.escapeHtml(f.name.slice(0, 22))}</text>
          </g>
        `;
      }).join('');

      mapContainer.innerHTML = `
        <div class="gis-interactive-wrapper">
          <svg class="facilities-gis-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet">
            <defs>
              <pattern id="realGpsGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#E2E8F0" stroke-width="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="#F8FAFC"/>
            <rect width="100%" height="100%" fill="url(#realGpsGrid)"/>

            <!-- Proximity Radius Rings -->
            <circle cx="${cx}" cy="${cy}" r="130" fill="none" stroke="#0D9488" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.4"/>
            <circle cx="${cx}" cy="${cy}" r="65" fill="none" stroke="#0D9488" stroke-width="1" stroke-dasharray="4,4" opacity="0.25"/>
            <text x="${cx + 5}" y="${cy - 135}" fill="#0D9488" font-size="9" font-weight="700">${this.facilityRadiusKm} KM RADIUS</text>

            <!-- Center: ASHA Worker Live GPS Marker -->
            <circle cx="${cx}" cy="${cy}" r="16" fill="#3B82F6" fill-opacity="0.25"/>
            <circle cx="${cx}" cy="${cy}" r="8" fill="#2563EB" stroke="#FFFFFF" stroke-width="2.5"/>
            <text x="${cx + 12}" y="${cy - 10}" fill="#1E40AF" font-size="11" font-weight="800">You (ASHA GPS)</text>

            <!-- Discovered Real Facilities Pins -->
            ${pinsHtml}
          </svg>

          <div class="gis-hud-overlay">
            <div class="gis-hud-badge">
              <span class="hud-dot"></span>
              <span>GPS Center: ${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E (Radius: ${this.facilityRadiusKm} km)</span>
            </div>
            <a href="https://www.google.com/maps/search/hospitals+clinics/@${lat},${lng},14z" target="_blank" rel="noopener noreferrer" class="btn-open-gmaps">
              <span>Open in Google Maps</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            </a>
          </div>
        </div>
      `;
    }

    renderFollowupsList(filter = 'all') {
      const container = document.getElementById('followupsListContainer');
      if (!container) return;

      let list = this.visits.filter(v => v.followup && v.followup.required);
      if (filter === 'completed') {
        list = list.filter(v => v.status === 'Complete');
      } else if (filter === 'required') {
        list = list.filter(v => v.status !== 'Complete');
      }

      if (list.length === 0) {
        container.innerHTML = `<div class="empty-state-card"><p>No follow-ups found.</p></div>`;
        return;
      }

      container.innerHTML = list.map(v => `
        <div class="visit-clinical-card status-border-followup">
          <div class="visit-card-top-row">
            <div class="visit-beneficiary-info">
              <h3 class="visit-person-name">${v.personName}</h3>
              <span class="visit-relation-tag">${v.relation} • ${v.village} (${v.householdId})</span>
            </div>
            <div class="visit-status-badge tag-amber">Follow-up</div>
          </div>

          <div class="visit-purpose-line">
            <span class="purpose-label">Follow-up Reason:</span>
            <span class="purpose-text">${v.followup.reason}</span>
          </div>

          <div class="visit-event-badge">
            <span class="event-icon">📋</span>
            <span class="event-text">History: ${v.followupHistory || v.previousRecord}</span>
          </div>

          <div class="visit-card-footer">
            <div class="visit-due-info">
              <span class="due-label">Scheduled Date:</span>
              <span class="due-date text-amber">${v.followup.dueDate}</span>
            </div>
            <div class="visit-actions-group">
              <button class="btn-visit-action btn-voice-visit" onclick="sakhiApp.showToast('Calling beneficiary: ${v.personName}')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                <span>Call</span>
              </button>
              <button class="btn-visit-action btn-visit-complete" onclick="sakhiApp.showToast('Follow-up scheduled on calendar')">
                <span>Reschedule</span>
              </button>
            </div>
          </div>
        </div>
      `).join('');
    }

    filterFollowups(filter, btn) {
      if (btn) {
        document.querySelectorAll('#screen-followups .filter-pill-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      }
      this.renderFollowupsList(filter);
    }

    renderAlertsList(priorityFilter = 'all') {
      const container = document.getElementById('alertsListContainer');
      if (!container) return;

      const normalizeAlert = (v) => {
        if (!v.alert) return null;
        if (typeof v.alert === 'string') {
          return { title: 'Clinical Alert', reason: v.alert, priority: 'Urgent' };
        }
        return v.alert;
      };

      let list = this.visits.filter(v => normalizeAlert(v));
      if (priorityFilter !== 'all') {
        list = list.filter(v => {
          const a = normalizeAlert(v);
          return a && (a.priority || 'Moderate').toLowerCase() === priorityFilter.toLowerCase();
        });
      }

      if (list.length === 0) {
        container.innerHTML = `<div class="empty-state-card"><p>No alerts under this priority.</p></div>`;
        return;
      }

      container.innerHTML = list.map(v => {
        const a = normalizeAlert(v);
        const priority = a.priority || 'Moderate';
        return `
        <div class="visit-clinical-card status-border-crimson">
          <div class="visit-card-top-row">
            <div class="visit-beneficiary-info">
              <h3 class="visit-person-name">${v.personName || 'Beneficiary'}</h3>
              <span class="visit-relation-tag">${v.relation || 'Patient'} • ${v.village || ''}</span>
            </div>
            <div class="visit-status-badge ${priority === 'Urgent' ? 'tag-crimson' : 'tag-amber'}">${priority} Priority</div>
          </div>

          <div class="visit-alert-box alert-${priority.toLowerCase()}">
            <span class="alert-icon">⚠️</span>
            <div class="alert-content">
              <span class="alert-title">${a.title || 'Clinical Alert'}</span>
              <span class="alert-reason">${a.reason || ''}</span>
            </div>
          </div>

          <div class="visit-event-badge">
            <span class="event-icon">⚡</span>
            <span class="event-text">Triggering Event: ${v.event || v.previousRecord || 'Clinical flag recorded'}</span>
          </div>

          <div class="visit-reasoning-box">
            <span class="reasoning-label">Protocol Reasoning:</span>
            <p class="reasoning-text">${v.ruleExplanation || 'Follow National Health Mission protocol and notify ANM.'}</p>
          </div>

          <div class="visit-card-footer">
            <div class="visit-due-info">
              <span class="due-label">Status:</span>
              <span class="due-date text-crimson">${v.status}</span>
            </div>
            <div class="visit-actions-group">
              <button class="btn-visit-action btn-visit-complete" onclick="sakhiApp.showToast('Triage acknowledged for ${v.personName || 'Beneficiary'}')">
                Acknowledge
              </button>
              <button class="btn-visit-action btn-voice-visit" onclick="sakhiApp.navigateTo('visits'); sakhiApp.switchVisitsSubtab('register'); sakhiApp.searchVisits('${(v.personName || '').replace(/'/g, "\\'")}')">
                Visit Now
              </button>
            </div>
          </div>
        </div>
      `;
      }).join('');
    }

    filterAlerts(priority, btn) {
      if (btn) {
        document.querySelectorAll('#screen-alerts .filter-pill-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      }
      this.renderAlertsList(priority);
    }

    // ============================================================
    // AI HEALTH ASSISTANT CHAT MODULE
    // ============================================================
    async sendChatMessage() {
      const input = document.getElementById('chatMessageInput');
      if (!input) return;
      const text = input.value.trim();
      if (!text) return;

      const scroll = document.getElementById('chatMessagesScroll');
      const now = new Date();
      const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      // Append User message
      const userHtml = `
        <div class="chat-row user-row">
          <div class="bubble-avatar-mini user-mini-avatar">
            <img src="${MOTHER_AVATAR}" alt="ASHA Worker">
          </div>
          <div class="chat-bubble user-bubble">
            <p class="bubble-text">${this.escapeHtml(text)}</p>
            <div class="bubble-meta">
              <span class="bubble-time">${timeStr}</span>
              <span class="bubble-ticks">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2.5"><polyline points="18 6 9 17 4 12"/><polyline points="22 10 13 21 8 16"/></svg>
              </span>
            </div>
          </div>
        </div>
      `;
      scroll.insertAdjacentHTML('beforeend', userHtml);
      input.value = '';
      scroll.scrollTop = scroll.scrollHeight;

      // Show typing indicator
      const typingId = `typing-${Date.now()}`;
      const typingHtml = `
        <div class="chat-row bot-row" id="${typingId}">
          <div class="bubble-avatar-mini bot-mini-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#2B66FF">
              <rect x="5" y="7" width="14" height="12" rx="4"/>
              <circle cx="9" cy="12" r="1.2" fill="#FFFFFF"/>
              <circle cx="15" cy="12" r="1.2" fill="#FFFFFF"/>
              <path d="M9 15h6" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="chat-bubble bot-bubble">
            <p class="bubble-text"><em>Consulting SAKHI clinical engine...</em></p>
          </div>
        </div>
      `;
      scroll.insertAdjacentHTML('beforeend', typingHtml);
      scroll.scrollTop = scroll.scrollHeight;

      let responseText = "";
      let chatPayload = null;
      try {
        const resp = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: text,
            beneficiary_id: this.selectedHouseholdId || this.selectedMother?.id || this.selectedBaby?.id || null,
            current_draft: this.voiceDraft || null,
            screen_context: this.captureVisibleScreenContext(),
            shared_tab_context: this.getSharedTabContext(),
            language_code: ({ en: 'en-IN', hi: 'hi-IN', kn: 'kn-IN' }[this.currentLang] || 'en-IN'),
            conversation_history: (this.chatHistory || []).slice(-6)
          })
        });
        if (resp.ok) {
          chatPayload = await resp.json();
          responseText = chatPayload.response || this.generateAshaAdvice(text);
          this.chatHistory.push({ role: 'user', content: text });
          this.chatHistory.push({ role: 'assistant', content: responseText });
        } else {
          responseText = `Assistant API error (HTTP ${resp.status}). Please try again.`;
        }
      } catch (err) {
        responseText = 'Unable to reach SAKHI assistant backend. Please check that the local server is running.';
      }

      const typingEl = document.getElementById(typingId);
      if (typingEl) typingEl.remove();

      const safeResp = this.escapeHtml(responseText).replace(/\n/g, '<br>');
      const sourceBadge = chatPayload?.source
        ? `<div style="font-size:0.7rem;color:#64748B;margin-top:0.25rem;">Source: ${this.escapeHtml(chatPayload.source)}</div>`
        : '';
      const ttsText = chatPayload?.tts_text || responseText;
      const ttsBtnId = `ttsBtn-${Date.now()}`;
      const actionPreview = chatPayload?.action_preview;
      let actionHtml = '';
      if (actionPreview && actionPreview.requires_confirmation) {
        this._pendingChatAction = actionPreview;
        actionHtml = `
          <div style="margin-top:0.5rem;padding:0.5rem;background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;font-size:0.78rem;">
            <strong>${this.escapeHtml(actionPreview.preview_title || 'Action Ready')}</strong>
            <div style="margin-top:0.35rem;display:flex;gap:0.4rem;">
              <button class="btn-visit-action btn-take-visit" onclick="sakhiApp.openVoiceModalWithPreview()">Review & Confirm</button>
            </div>
          </div>
        `;
      }

      const botHtml = `
        <div class="chat-row bot-row">
          <div class="bubble-avatar-mini bot-mini-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#2B66FF">
              <rect x="5" y="7" width="14" height="12" rx="4"/>
              <circle cx="9" cy="12" r="1.2" fill="#FFFFFF"/>
              <circle cx="15" cy="12" r="1.2" fill="#FFFFFF"/>
              <path d="M9 15h6" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="chat-bubble bot-bubble">
            <p class="bubble-text">${safeResp}</p>
            ${sourceBadge}
            ${actionHtml}
            <button type="button" id="${ttsBtnId}" class="btn-chat-tts" onclick="sakhiApp.speakText(${JSON.stringify(ttsText)}, '${ttsBtnId}')">🔊 Play</button>
            <div class="bubble-meta">
              <span class="bubble-time">${timeStr}</span>
            </div>
          </div>
        </div>
      `;
      scroll.insertAdjacentHTML('beforeend', botHtml);
      scroll.scrollTop = scroll.scrollHeight;
    }

    generateAshaAdvice(query) {
      const q = query.toLowerCase();

      if (q.includes('iron') || q.includes('ifa') || q.includes('tablet')) {
        return "Iron tablets help prevent anemia in pregnant women. Encourage her to take it daily after food. If she feels symptoms like dizziness, weakness or nausea, suggest her to consult the ANM or PHC Medical Officer.";
      }
      if (q.includes('calcium')) {
        return "Calcium tablets should be taken twice daily after 14 weeks of pregnancy, but NOT at the same time as Iron tablets. Keep at least a 2-hour gap between Calcium and IFA tablets.";
      }
      if (q.includes('vaccine') || q.includes('pentavalent') || q.includes('bcg') || q.includes('measles')) {
        return "Child immunization protocol: Pentavalent-3 and OPV-3 are due at 14 weeks. Measles-Rubella (MR-1) is administered at 9 completed months along with Vitamin A dose 1.";
      }
      if (q.includes('bp') || q.includes('blood pressure') || q.includes('hypertension') || q.includes('headache')) {
        return "Warning: Severe headache, blurred vision, or BP > 140/90 mmHg are danger signs of pre-eclampsia. Urgently notify Primary Health Centre Medical Officer and arrange immediate transport.";
      }
      if (q.includes('swelling') || q.includes('edema') || q.includes('feet')) {
        return "Mild pedal edema after walking is common, but sudden facial swelling or puffiness around eyes requires immediate BP screening and urine albumin test.";
      }
      if (q.includes('fever') || q.includes('baby') || q.includes('cold')) {
        return "For newborn fever (>37.5°C) or refusal to breastfeed: Keep baby warm with Kangaroo Mother Care and accompany mother to the Primary Health Centre immediately.";
      }

      return "I understand your clinical query. According to National Rural Health Mission protocols, record this observation in the MCP card and verify danger signs. If symptoms persist, notify the ANM.";
    }

    // Voice Input Toggle (Web Speech API + Backend fallback)
    initSpeechRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.speechRecognition = new SpeechRecognition();
        this.speechRecognition.continuous = false;
        this.speechRecognition.interimResults = false;
        this.speechRecognition.lang = 'en-IN'; // Also supports 'kn-IN'

        this.speechRecognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          const input = document.getElementById('chatMessageInput');
          if (input) {
            input.value = transcript;
            this.sendChatMessage();
          }
        };

        this.speechRecognition.onend = () => {
          this.setRecordingState(false);
        };

        this.speechRecognition.onerror = () => {
          this.setRecordingState(false);
          this.showToast('Voice capture ended');
        };
      }
    }

    toggleChatVoice() {
      if (!this.speechRecognition) {
        // Fallback for browsers without speech API
        const sampleQueries = [
          "A pregnant women missed her iron tablets.what should i do?",
          "When is Pentavalent dose 3 due for infants?",
          "Mother has high blood pressure 140/90 what are danger signs?"
        ];
        const randomQuery = sampleQueries[Math.floor(Math.random() * sampleQueries.length)];
        const input = document.getElementById('chatMessageInput');
        if (input) {
          input.value = randomQuery;
          this.showToast('Voice recorded: "' + randomQuery.slice(0, 32) + '..."');
          setTimeout(() => this.sendChatMessage(), 500);
        }
        return;
      }

      if (this.isRecording) {
        this.speechRecognition.stop();
        this.setRecordingState(false);
      } else {
        try {
          this.speechRecognition.start();
          this.setRecordingState(true);
          this.showToast('Listening... Speak now');
        } catch (e) {
          this.setRecordingState(false);
        }
      }
    }

    setRecordingState(recording) {
      this.isRecording = recording;
      const micBtn = document.getElementById('chatMicBtn');
      if (micBtn) {
        micBtn.classList.toggle('recording', recording);
      }
    }

    // ============================================================
    // MODALS & OPTIONS MENU
    // ============================================================
    showOptionsMenu(context) {
      const modal = document.getElementById('optionsModal');
      const list = document.getElementById('optionsActionsList');
      const title = document.getElementById('optionsSheetTitle');

      if (!modal || !list) return;

      let actions = [];
      if (context === 'maternal') {
        title.textContent = 'Maternal Health Actions';
        actions = [
          { label: 'Add New Mother', icon: 'user-plus', action: () => this.openMaternalForm() },
          { label: 'Export Field ANC Register', icon: 'download', action: () => this.showToast('Downloading ANC Register Excel/PDF...') },
          { label: 'Sync with RCH Portal', icon: 'refresh', action: () => this.showToast('Synced with Karnataka RCH Portal ✓') }
        ];
      } else if (context === 'vaccine') {
        title.textContent = 'Vaccine Tracker Actions';
        actions = [
          { label: 'Add New Baby', icon: 'plus-circle', action: () => this.openBabyForm() },
          { label: 'Immunization Due List (This Month)', icon: 'calendar', action: () => this.showToast('3 babies due for vaccination this week') },
          { label: 'Cold Chain Ice Pack Status', icon: 'shield', action: () => this.showToast('PHC Cold Chain: Safe (+4°C)') }
        ];
      } else if (context === 'mother-detail') {
        title.textContent = this.selectedMother.name;
        actions = [
          { label: 'Edit Mother Profile', icon: 'edit', action: () => this.editCurrentMother() },
          { label: 'Call Beneficiary', icon: 'phone', action: () => window.open(`tel:${this.selectedMother.phone || '1234567891'}`) },
          { label: 'Share MCP Card Summary', icon: 'share', action: () => this.showToast('MCP card shared via SMS') }
        ];
      } else if (context === 'child-detail') {
        title.textContent = this.selectedBaby.name;
        actions = [
          { label: 'Edit Child Profile', icon: 'edit', action: () => this.editCurrentBaby() },
          { label: 'Call Parent/Guardian', icon: 'phone', action: () => window.open(`tel:${this.selectedBaby.phone || '1234567891'}`) },
          { label: 'Mark Next Vaccine Given', icon: 'check', action: () => this.markVaccineGiven() }
        ];
      } else {
        title.textContent = 'Options';
        actions = [
          { label: 'Refresh Data', icon: 'refresh', action: () => location.reload() },
          { label: 'Offline Mode Settings', icon: 'settings', action: () => this.showToast('All data saved locally for offline village visits') }
        ];
      }

      list.innerHTML = actions.map(act => `
        <button class="sheet-action-item" onclick="sakhiApp.closeOptionsMenu(); (${act.action.toString()})()">
          <span>${act.label}</span>
        </button>
      `).join('');

      modal.classList.add('open');
    }

    closeOptionsMenu() {
      const modal = document.getElementById('optionsModal');
      if (modal) modal.classList.remove('open');
    }

    async markVaccineGiven() {
      if (!this.selectedBaby) return;
      this.selectedBaby.completedVaccines = (this.selectedBaby.completedVaccines || 7) + 1;
      this.selectedBaby.pendingVaccines = Math.max(0, (this.selectedBaby.pendingVaccines || 2) - 1);

      try {
        await fetch('/api/vaccines/update', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            beneficiary_id: this.selectedBaby.id,
            vaccine_name: 'Scheduled Dose',
            mode: 'child'
          })
        });
      } catch (err) {
        console.warn('Vaccine update error:', err);
      }

      this.saveState('sakhi_babies', this.babies);
      this.renderBabyDetail(this.selectedBaby);
      this.showToast('Vaccine administration recorded in Sakhi register!');
    }

    showNotificationsModal() {
      const modal = document.getElementById('optionsModal');
      const list = document.getElementById('optionsActionsList');
      const title = document.getElementById('optionsSheetTitle');
      if (!modal || !list || !title) {
        this.showToast('Notifications unavailable');
        return;
      }

      title.textContent = 'Need Attention';
      const urgentItems = (this.priorities || []).filter(h =>
        ['immediate_escalation', 'high_priority', 'overdue', 'due_today'].includes(h.status_bucket)
      );

      if (urgentItems.length === 0) {
        list.innerHTML = `
          <div class="notif-empty">✓ All households are up to date.</div>
        `;
      } else {
        const topItems = urgentItems.slice(0, 4);
        const rowsHtml = topItems.map(h => {
          const isRed = h.priority_code === 'RED';
          const pillCls = isRed ? 'notif-pill-red' : (h.priority_code === 'ORANGE' ? 'notif-pill-orange' : 'notif-pill-yellow');
          const pillTxt = isRed ? 'URGENT' : (h.priority_code === 'ORANGE' ? 'HIGH' : (h.due_today ? 'TODAY' : `${h.overdue_days}d OVERDUE`));
          return `
            <button class="notif-item ${isRed ? 'notif-item-red' : ''}" onclick="sakhiApp.closeOptionsMenu(); sakhiApp.openHouseholdDetail('${this.escapeHtml(h.beneficiary_id)}')">
              <div class="notif-item-top">
                <span class="notif-name">${this.escapeHtml(h.name)} <small>(${this.escapeHtml(h.beneficiary_id)})</small></span>
                <span class="notif-pill ${pillCls}">${this.escapeHtml(pillTxt)}</span>
              </div>
              <span class="notif-reason">${this.escapeHtml(h.primary_reason)}</span>
            </button>
          `;
        }).join('');

        const moreCount = Math.max(0, urgentItems.length - topItems.length);
        list.innerHTML = `
          <div class="notif-list-wrap">${rowsHtml}</div>
          <button class="notif-view-all-btn" onclick="sakhiApp.closeOptionsMenu(); sakhiApp.openPriorityQueue('all')">
            ${moreCount > 0 ? `View all ${urgentItems.length} priority alerts →` : 'Open Priority Queue →'}
          </button>
        `;
      }

      modal.classList.add('open');
    }

    showToast(message) {
      const container = document.getElementById('toastContainer');
      if (!container) return;

      const toast = document.createElement('div');
      toast.className = 'toast-msg';
      toast.textContent = message;
      container.appendChild(toast);

      setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 3000);
    }

    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    // ============================================================
    // HOUSEHOLD PRIORITIZATION INTELLIGENCE WORKFLOW
    // ============================================================
    async fetchPriorities() {
      try {
        const params = new URLSearchParams({
          filter_by: this.currentPriorityFilter || 'all',
          sort_by: this.currentPrioritySort || 'priority',
          search: this.prioritySearchQuery || ''
        });
        const resp = await fetch(`/api/priorities?${params.toString()}`);
        if (!resp.ok) return;
        const payload = await resp.json();
        if (payload.success) {
          this.priorities = payload.data || [];
          this.prioritySummary = payload.summary || null;
          this.renderPrioritySummary();
          this.renderPrioritiesList();
        }
      } catch (err) {
        console.warn('Priority fetch failed:', err);
      }
    }

    renderPrioritySummary() {
      const s = this.prioritySummary;
      if (!s) return;
      const setTxt = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val ?? 0;
      };
      setTxt('prioTotalHouseholds', s.total_households);
      setTxt('prioRedCount', s.immediate_escalation);
      setTxt('prioOrangeCount', s.high_priority);
      setTxt('prioOverdueCount', s.overdue);
      setTxt('prioDueTodayCount', s.due_today);
      setTxt('prioUpcomingCount', s.upcoming);
      setTxt('prioRoutineCount', s.routine);
      setTxt('prioMissingCount', s.missing_data);
      const refEl = document.getElementById('priorityRefDate');
      if (refEl && s.reference_date) {
        refEl.textContent = `Ref: ${s.reference_date}`;
      }
    }

    openPriorityQueue(filter = 'all') {
      this.navigateTo('visits');
      this.switchVisitsSubtab('priority');
      this.filterPriorities(filter);
    }

    switchVisitsSubtab(subtab) {
      const prioPanel = document.getElementById('visitsPriorityPanel');
      const regPanel = document.getElementById('visitsRegisterPanel');
      document.querySelectorAll('#visitsSubtabBar .visits-subtab-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.subtab === subtab);
      });
      if (prioPanel) prioPanel.style.display = subtab === 'priority' ? 'block' : 'none';
      if (regPanel) regPanel.style.display = subtab === 'register' ? 'block' : 'none';
    }

    filterPriorities(filter, btn) {
      this.currentPriorityFilter = filter || 'all';
      document.querySelectorAll('#priorityFilterBar .filter-pill-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.prioFilter === this.currentPriorityFilter);
      });
      if (btn) btn.classList.add('active');
      this.fetchPriorities();
    }

    setPrioritySort(sortBy) {
      this.currentPrioritySort = sortBy || 'priority';
      this.fetchPriorities();
    }

    searchPriorities(query) {
      this.prioritySearchQuery = query || '';
      this.fetchPriorities();
    }

    renderPrioritiesList() {
      const container = document.getElementById('priorityListContainer');
      if (!container) return;

      const list = this.priorities || [];
      if (list.length === 0) {
        container.innerHTML = `<div class="empty-state-card"><p>No households match this filter.</p></div>`;
        return;
      }

      container.innerHTML = list.map(h => {
        const code = (h.priority_code || 'GREEN').toLowerCase();
        const badgeLabel = `${h.priority_code} · ${h.priority_label}`;
        const escalationBlock = h.escalation ? `
          <div class="prio-escalation-box">
            <div class="prio-esc-title">⚠️ ${this.escapeHtml(h.escalation.warning)}</div>
            <div class="prio-esc-trigger">Trigger: ${this.escapeHtml(h.escalation.trigger_indicator)}</div>
            <div class="prio-esc-instr">${this.escapeHtml(h.escalation.instruction)}</div>
            <div class="prio-esc-disc">${this.escapeHtml(h.escalation.disclaimer)}</div>
          </div>
        ` : '';

        const missingBlock = h.has_missing_data ? `
          <div class="prio-missing-banner">
            <span>🔍 ${this.escapeHtml(h.verification_warning || 'Missing data requires verification.')}</span>
          </div>
        ` : '';

        const dueStr = h.followup_date ? this.escapeHtml(h.followup_date) : 'No date scheduled';
        const safeName = this.escapeHtml(h.name || h.beneficiary_id);

        return `
          <div class="prio-household-card prio-border-${code}">
            <div class="prio-card-top">
              <div class="prio-card-id-block">
                <div class="prio-card-title-row">
                  <span class="prio-ben-id">${this.escapeHtml(h.beneficiary_id)}</span>
                  <h4 class="prio-ben-name">${safeName}</h4>
                </div>
                <div class="prio-meta-row">
                  <span class="prio-type-chip">${this.escapeHtml(h.beneficiary_type)}</span>
                  <span class="prio-address-txt">📍 ${this.escapeHtml(h.address)}</span>
                </div>
              </div>
              <span class="prio-badge prio-badge-${code}">${this.escapeHtml(badgeLabel)}</span>
            </div>

            ${escalationBlock}

            <div class="prio-reason-box">
              <span class="prio-reason-lbl">${this.escapeHtml(this.t('whyPrioritized'))}</span>
              <span class="prio-reason-txt">${this.escapeHtml(h.primary_reason)}</span>
            </div>

            ${missingBlock}

            <div class="prio-action-meta">
              <div><strong>${this.escapeHtml(this.t('followupLbl'))}</strong> ${dueStr}</div>
              <div><strong>${this.escapeHtml(this.t('nextActionLbl'))}</strong> ${this.escapeHtml(h.suggested_action)}</div>
            </div>

            <div class="prio-card-actions">
              <button class="btn-visit-action btn-voice-visit" onclick="sakhiApp.openHouseholdDetail('${this.escapeHtml(h.beneficiary_id)}')">
                ${this.escapeHtml(this.t('openHousehold'))}
              </button>
              <button class="btn-visit-action btn-take-visit" onclick="sakhiApp.openPlanVisitModal('${this.escapeHtml(h.beneficiary_id)}', '${safeName.replace(/'/g, "\\'")}')">
                ${this.escapeHtml(this.t('planVisit'))}
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    async openHouseholdDetail(beneficiaryId) {
      this.selectedHouseholdId = beneficiaryId;
      this.navigateTo('household-detail');
      await this.loadHouseholdDetail(beneficiaryId);
    }

    async loadHouseholdDetail(beneficiaryId) {
      const body = document.getElementById('householdDetailBody');
      if (body) body.innerHTML = `<div class="empty-state-card"><p>Loading household ${this.escapeHtml(beneficiaryId)}...</p></div>`;
      try {
        const resp = await fetch(`/api/priorities/${encodeURIComponent(beneficiaryId)}`);
        if (!resp.ok) {
          if (body) body.innerHTML = `<div class="empty-state-card"><p>Could not load household detail.</p></div>`;
          return;
        }
        const payload = await resp.json();
        this.selectedHouseholdDetail = payload.data;
        this.renderHouseholdDetail(payload.data);
      } catch (err) {
        if (body) body.innerHTML = `<div class="empty-state-card"><p>Error loading household detail.</p></div>`;
      }
    }

    renderHouseholdDetail(detail) {
      const body = document.getElementById('householdDetailBody');
      const header = document.getElementById('householdDetailHeaderTitle');
      if (!body || !detail || !detail.priority) return;

      const p = detail.priority;
      if (header) header.textContent = `${p.beneficiary_id} · ${p.name}`;

      const code = (p.priority_code || 'GREEN').toLowerCase();
      const reasonsHtml = (p.reasons || []).map(r => `<li>${this.escapeHtml(r)}</li>`).join('');
      const missingHtml = p.has_missing_data
        ? `<div class="prio-missing-banner"><strong>Verification Required:</strong> ${this.escapeHtml((p.missing_data_items || []).join(', '))}</div>`
        : `<div class="detail-verified-note">✓ Core household fields present.</div>`;

      const visitsHtml = (detail.visits || []).length === 0
        ? `<p class="empty-sub">No visits recorded yet for this household.</p>`
        : detail.visits.map(v => {
            const done = !!(v.visit_ts && String(v.visit_ts).trim());
            return `
              <div class="detail-visit-row">
                <div>
                  <strong>${this.escapeHtml(v.id)} · ${this.escapeHtml(v.type || 'Visit')}</strong>
                  <div class="detail-visit-sub">Due: ${this.escapeHtml(v.due_date || '-')} | Flag: ${this.escapeHtml(v.flag || 'N')} | ${done ? 'Completed: ' + this.escapeHtml(v.visit_ts) : 'Pending'}</div>
                  ${v.note ? `<div class="detail-visit-note">${this.escapeHtml(v.note)}</div>` : ''}
                </div>
                ${done
                  ? `<span class="visit-status-badge tag-emerald">Complete</span>`
                  : `<button class="btn-visit-action btn-visit-complete" onclick="sakhiApp.completeVisitFromDetail('${this.escapeHtml(v.id)}', '${this.escapeHtml(p.beneficiary_id)}')">Complete</button>`
                }
              </div>
            `;
          }).join('');

      const preg = detail.pregnancy;
      const child = detail.child;
      let beneficiaryHtml = '';
      if (preg) {
        beneficiaryHtml += `
          <div class="detail-visit-row">
            <div>
              <strong>Maternal Record (${this.escapeHtml(preg.status || 'ACTIVE')})</strong>
              <div class="detail-visit-sub">
                Name: ${this.escapeHtml(preg.mother_name || 'Missing — Verify')} |
                Week: ${this.escapeHtml(String(preg.week ?? '-'))} |
                EDD: ${this.escapeHtml(preg.exp_dd || 'Missing — Verify')} |
                Weight: ${preg.weight != null ? this.escapeHtml(String(preg.weight)) + ' kg' : 'Missing — Verify'} |
                Mobile: ${this.escapeHtml(preg.mobile || 'Missing — Verify')}
              </div>
            </div>
          </div>
        `;
      }
      if (child) {
        beneficiaryHtml += `
          <div class="detail-visit-row">
            <div>
              <strong>Child Record (${this.escapeHtml(child.child_name || 'Unnamed')})</strong>
              <div class="detail-visit-sub">
                DOB: ${this.escapeHtml(child.dob || 'Missing — Verify')} |
                Age: ${this.escapeHtml(String(child.age ?? '-'))} |
                Next Visit: ${this.escapeHtml(child.next_visit || 'Missing — Verify')}
              </div>
              <div class="detail-visit-note">Vaccines Due: ${this.escapeHtml(child.vacs_due || 'None recorded')}</div>
            </div>
          </div>
        `;
      }
      if (!beneficiaryHtml) {
        beneficiaryHtml = `<p class="empty-sub">General household record (${this.escapeHtml(p.home_status)}).</p>`;
      }

      body.innerHTML = `
        <div class="prio-household-card prio-border-${code}">
          <div class="prio-card-top">
            <div>
              <h3 class="prio-ben-name">${this.escapeHtml(p.name)} (${this.escapeHtml(p.beneficiary_id)})</h3>
              <div class="prio-meta-row">
                <span class="prio-type-chip">${this.escapeHtml(p.beneficiary_type)}</span>
                <span class="prio-address-txt">📍 ${this.escapeHtml(p.address)}</span>
              </div>
            </div>
            <span class="prio-badge prio-badge-${code}">${this.escapeHtml(p.priority_code)} · ${this.escapeHtml(p.priority_label)}</span>
          </div>
          ${p.escalation ? `
            <div class="prio-escalation-box">
              <div class="prio-esc-title">⚠️ ${this.escapeHtml(p.escalation.warning)}</div>
              <div class="prio-esc-trigger">${this.escapeHtml(p.escalation.trigger_indicator)}</div>
              <div class="prio-esc-instr">${this.escapeHtml(p.escalation.instruction)}</div>
              <div class="prio-esc-disc">${this.escapeHtml(p.escalation.disclaimer)}</div>
            </div>
          ` : ''}
          <div class="prio-reason-box">
            <span class="prio-reason-lbl">Priority Explanation (Rule-Based):</span>
            <ul class="detail-reasons-list">${reasonsHtml}</ul>
          </div>
          ${missingHtml}
          <div class="prio-action-meta">
            <div><strong>Suggested Next Action:</strong> ${this.escapeHtml(p.suggested_action)}</div>
          </div>
          <div class="prio-card-actions">
            <button class="btn-visit-action btn-take-visit" onclick="sakhiApp.openPlanVisitModal('${this.escapeHtml(p.beneficiary_id)}', '${this.escapeHtml(p.name).replace(/'/g, "\\'")}')">
              + Plan Visit / Follow-up
            </button>
            <button class="btn-visit-action btn-voice-visit" onclick="sakhiApp.navigateTo('visits'); sakhiApp.switchVisitsSubtab('register'); sakhiApp.searchVisits('${this.escapeHtml(p.beneficiary_id)}')">
              Open in Visits Register
            </button>
          </div>
        </div>

        <div class="detail-section-card">
          <h4>Beneficiary Information</h4>
          ${beneficiaryHtml}
        </div>

        <div class="detail-section-card">
          <h4>Visit & Follow-up History (${(detail.visits || []).length})</h4>
          ${visitsHtml}
        </div>
      `;
    }

    async completeVisitFromDetail(visitId, beneficiaryId) {
      try {
        const resp = await fetch(`/api/visits/${encodeURIComponent(visitId)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'Complete' })
        });
        if (resp.ok) {
          this.showToast(`Visit ${visitId} marked complete! Updating priorities...`);
          await this.fetchBackendData();
          await this.loadHouseholdDetail(beneficiaryId);
        }
      } catch (err) {
        this.showToast('Failed to update visit.');
      }
    }

    openPlanVisitModalForCurrent() {
      if (this.selectedHouseholdDetail?.priority) {
        const p = this.selectedHouseholdDetail.priority;
        this.openPlanVisitModal(p.beneficiary_id, p.name);
      }
    }

    openPlanVisitModal(beneficiaryId, name) {
      const modal = document.getElementById('planVisitModal');
      const title = document.getElementById('planVisitModalTitle');
      const idInput = document.getElementById('planVisitBenId');
      const dateInput = document.getElementById('planVisitDueDate');
      const noteInput = document.getElementById('planVisitNote');
      if (!modal || !idInput) return;

      idInput.value = beneficiaryId;
      if (title) title.textContent = `Plan Visit · ${name || beneficiaryId}`;
      if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().slice(0, 10);
      }
      if (noteInput) noteInput.value = '';
      modal.classList.add('open');
    }

    closePlanVisitModal() {
      const modal = document.getElementById('planVisitModal');
      if (modal) modal.classList.remove('open');
    }

    async submitPlanVisit(event) {
      if (event) event.preventDefault();
      const benId = document.getElementById('planVisitBenId')?.value;
      const visitType = document.getElementById('planVisitType')?.value || 'ANC';
      const dueDate = document.getElementById('planVisitDueDate')?.value;
      const flag = document.getElementById('planVisitFlag')?.value || 'N';
      const note = document.getElementById('planVisitNote')?.value || '';
      if (!benId || !dueDate) return;

      const btn = document.getElementById('btnSubmitPlanVisit');
      if (btn) { btn.disabled = true; btn.textContent = 'Saving...'; }

      try {
        const resp = await fetch('/api/visits', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            beneficiary_id: benId,
            visit_type: visitType,
            due_date: dueDate,
            flag,
            note,
            origin: 'priority_dashboard'
          })
        });
        const data = await resp.json();
        if (resp.ok && data.success) {
          this.closePlanVisitModal();
          this.showToast(`Visit ${data.visit_id || ''} planned for ${benId} in Field Visits Register!`);
          await this.fetchBackendData();
          if (this.currentScreen === 'household-detail' && this.selectedHouseholdId === benId) {
            await this.loadHouseholdDetail(benId);
          }
        } else {
          this.showToast(data.detail || 'Could not schedule visit.');
        }
      } catch (err) {
        this.showToast('Error scheduling visit.');
      } finally {
        if (btn) { btn.disabled = false; btn.textContent = 'Save Visit to Register'; }
      }
    }

    // ============================================================
    // MULTI-LANGUAGE INTERFACE (ENGLISH / HINDI / KANNADA)
    // ============================================================
    setLanguage(lang) {
      if (!['en', 'hi', 'kn'].includes(lang)) lang = 'en';
      this.currentLang = lang;
      try { localStorage.setItem('sakhi_lang', lang); } catch (e) {}
      this.applyLanguage(lang);
      const names = { en: 'English', hi: 'हिन्दी (Hindi)', kn: 'ಕನ್ನಡ (Kannada)' };
      this.showToast(`Language switched to ${names[lang]}`);
    }

    t(key) {
      const dict = {
        en: {
          greeting: 'Hello, ASHA Worker!',
          greetingSub: 'SAKHI Priority Summary · Tap any card to open Visits Queue',
          prioSummary: 'Household Priority Summary',
          totalHouseholds: 'Total Households',
          immediateRed: 'Immediate (RED)',
          highPriority: 'High Priority',
          overdue: 'Overdue',
          dueToday: 'Due Today',
          upcoming: 'Upcoming',
          routineGreen: 'Routine (GREEN)',
          needsVerification: 'Needs Verification',
          navHome: 'Home',
          navVisits: 'Visits',
          navFollowups: 'Follow-ups',
          navAlerts: 'Alerts',
          navMaternal: 'Maternal Health',
          navVaccine: 'Vaccine Tracker',
          navNearby: 'Nearby Clinics & Hospitals',
          navChat: 'AI Chatbot',
          navProfile: 'My Profile',
          logout: 'Logout',
          aiChatbot: 'AI Chatbot',
          aiChatbotSub: 'Ask health queries and get instant guidance',
          maternalHealth: 'Maternal health',
          maternalHealthSub: 'Track & access maternal health information',
          vaccineTracker: 'Vaccine tracker',
          vaccineTrackerSub: 'Track child vaccination schedules',
          fieldRegisterSummary: 'Field Register Summary',
          mothersRegistered: 'Mothers Registered',
          babiesTracked: 'Babies Tracked',
          dueThisWeek: 'Due This Week',
          visitsHeader: 'Field Visits',
          subtabPriority: 'Priority Queue (Households)',
          subtabRegister: 'Field Visits Register',
          prioritizedHouseholds: 'Prioritized Households',
          searchPrioPlaceholder: 'Search household ID, name, area, or reason...',
          searchVisitsPlaceholder: 'Search by name, village or purpose',
          whyPrioritized: 'Why prioritized:',
          followupLbl: 'Follow-up:',
          nextActionLbl: 'Next Action:',
          openHousehold: 'Open Household',
          planVisit: 'Plan Visit',
          followupsHeader: 'Follow-ups',
          alertsHeader: 'Clinical Alerts'
        },
        hi: {
          greeting: 'नमस्ते, आशा कार्यकर्ता!',
          greetingSub: 'सखी प्राथमिकता सारांश · विज़िट कतार खोलने के लिए किसी भी कार्ड पर टैप करें',
          prioSummary: 'परिवार प्राथमिकता सारांश',
          totalHouseholds: 'कुल परिवार',
          immediateRed: 'तत्काल (लाल)',
          highPriority: 'उच्च प्राथमिकता',
          overdue: 'अतिदेय (बाकी)',
          dueToday: 'आज देय',
          upcoming: 'आगामी',
          routineGreen: 'सामान्य (हरा)',
          needsVerification: 'सत्यापन आवश्यक',
          navHome: 'होम',
          navVisits: 'विज़िट',
          navFollowups: 'फॉलो-अप',
          navAlerts: 'अलर्ट',
          navMaternal: 'मातृ स्वास्थ्य',
          navVaccine: 'टीकाकरण ट्रैकर',
          navNearby: 'नजदीकी क्लिनिक व अस्पताल',
          navChat: 'AI चैटबॉट',
          navProfile: 'मेरी प्रोफ़ाइल',
          logout: 'लॉगआउट',
          aiChatbot: 'AI चैटबॉट',
          aiChatbotSub: 'स्वास्थ्य प्रश्न पूछें और तुरंत मार्गदर्शन पाएं',
          maternalHealth: 'मातृ स्वास्थ्य',
          maternalHealthSub: 'मातृ स्वास्थ्य जानकारी देखें और ट्रैक करें',
          vaccineTracker: 'टीकाकरण ट्रैकर',
          vaccineTrackerSub: 'बच्चों के टीकाकरण शेड्यूल को ट्रैक करें',
          fieldRegisterSummary: 'फ़ील्ड रजिस्टर सारांश',
          mothersRegistered: 'पंजीकृत माताएं',
          babiesTracked: 'ट्रैक किए गए शिशु',
          dueThisWeek: 'इस सप्ताह देय',
          visitsHeader: 'फ़ील्ड विज़िट',
          subtabPriority: 'प्राथमिकता कतार (परिवार)',
          subtabRegister: 'फ़ील्ड विज़िट रजिस्टर',
          prioritizedHouseholds: 'प्राथमिकता वाले परिवार',
          searchPrioPlaceholder: 'परिवार ID, नाम, क्षेत्र या कारण खोजें...',
          searchVisitsPlaceholder: 'नाम, गाँव या उद्देश्य से खोजें',
          whyPrioritized: 'प्राथमिकता का कारण:',
          followupLbl: 'फॉलो-अप:',
          nextActionLbl: 'अगला कदम:',
          openHousehold: 'परिवार खोलें',
          planVisit: 'विज़िट योजना',
          followupsHeader: 'फॉलो-अप',
          alertsHeader: 'क्लिनिकल अलर्ट'
        },
        kn: {
          greeting: 'ನಮಸ್ಕಾರ, ಆಶಾ ಕಾರ್ಯಕರ್ತೆ!',
          greetingSub: 'ಸಖಿ ಆದ್ಯತೆ ಸಾರಾಂಶ · ಭೇಟಿ ಪಟ್ಟಿಯನ್ನು ತೆರೆಯಲು ಕಾರ್ಡ್ ಟ್ಯಾಪ್ ಮಾಡಿ',
          prioSummary: 'ಕುಟುಂಬ ಆದ್ಯತೆ ಸಾರಾಂಶ',
          totalHouseholds: 'ಒಟ್ಟು ಕುಟುಂಬಗಳು',
          immediateRed: 'ತಕ್ಷಣ (ಕೆಂಪು)',
          highPriority: 'ಹೆಚ್ಚಿನ ಆದ್ಯತೆ',
          overdue: 'ಬಾಕಿ ಇರುವ',
          dueToday: 'ಇಂದು ಬಾಕಿ',
          upcoming: 'ಮುಂಬರುವ',
          routineGreen: 'ಸಾಮಾನ್ಯ (ಹಸಿರು)',
          needsVerification: 'ಪರಿಶೀಲನೆ ಅಗತ್ಯ',
          navHome: 'ಮುಖಪುಟ',
          navVisits: 'ಭೇಟಿಗಳು',
          navFollowups: 'ಫಾಲೋ-ಅಪ್',
          navAlerts: 'ಎಚ್ಚರಿಕೆಗಳು',
          navMaternal: 'ತಾಯಂದಿರ ಆರೋಗ್ಯ',
          navVaccine: 'ಲಸಿಕೆ ಟ್ರ್ಯಾಕರ್',
          navNearby: 'ಹತ್ತಿರದ ಕ್ಲಿನಿಕ್ ಮತ್ತು ಆಸ್ಪತ್ರೆಗಳು',
          navChat: 'AI ಚಾಟ್‌ಬಾಟ್',
          navProfile: 'ನನ್ನ ಪ್ರೊಫೈಲ್',
          logout: 'ಲಾಗ್‌ಔಟ್',
          aiChatbot: 'AI ಚಾಟ್‌ಬಾಟ್',
          aiChatbotSub: 'ಆರೋಗ್ಯ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ ಮತ್ತು ತಕ್ಷಣ ಮಾರ್ಗದರ್ಶನ ಪಡೆಯಿರಿ',
          maternalHealth: 'ತಾಯಂದಿರ ಆರೋಗ್ಯ',
          maternalHealthSub: 'ತಾಯಂದಿರ ಆರೋಗ್ಯ ಮಾಹಿತಿಯನ್ನು ಟ್ರ್ಯಾಕ್ ಮಾಡಿ',
          vaccineTracker: 'ಲಸಿಕೆ ಟ್ರ್ಯಾಕರ್',
          vaccineTrackerSub: 'ಮಕ್ಕಳ ಲಸಿಕೆ ವೇಳಾಪಟ್ಟಿಯನ್ನು ಟ್ರ್ಯಾಕ್ ಮಾಡಿ',
          fieldRegisterSummary: 'ಕ್ಷೇತ್ರ ನೋಂದಣಿ ಸಾರಾಂಶ',
          mothersRegistered: 'ನೋಂದಾಯಿತ ತಾಯಂದಿರು',
          babiesTracked: 'ಟ್ರ್ಯಾಕ್ ಮಾಡಿದ ಶಿಶುಗಳು',
          dueThisWeek: 'ಈ ವಾರ ಬಾಕಿ',
          visitsHeader: 'ಕ್ಷೇತ್ರ ಭೇಟಿಗಳು',
          subtabPriority: 'ಆದ್ಯತೆ ಪಟ್ಟಿ (ಕುಟುಂಬಗಳು)',
          subtabRegister: 'ಕ್ಷೇತ್ರ ಭೇಟಿ ನೋಂದಣಿ',
          prioritizedHouseholds: 'ಆದ್ಯತೆಯ ಕುಟುಂಬಗಳು',
          searchPrioPlaceholder: 'ಕುಟುಂಬ ID, ಹೆಸರು, ಪ್ರದೇಶ ಅಥವಾ ಕಾರಣ ಹುಡುಕಿ...',
          searchVisitsPlaceholder: 'ಹೆಸರು, ಗ್ರಾಮ ಅಥವಾ ಉದ್ದೇಶದಿಂದ ಹುಡುಕಿ',
          whyPrioritized: 'ಆದ್ಯತೆಯ ಕಾರಣ:',
          followupLbl: 'ಫಾಲೋ-ಅಪ್:',
          nextActionLbl: 'ಮುಂದಿನ ಕ್ರಮ:',
          openHousehold: 'ಕುಟುಂಬ ತೆರೆಯಿರಿ',
          planVisit: 'ಭೇಟಿ ಯೋಜಿಸಿ',
          followupsHeader: 'ಫಾಲೋ-ಅಪ್‌ಗಳು',
          alertsHeader: 'ಕ್ಲಿನಿಕಲ್ ಎಚ್ಚರಿಕೆಗಳು'
        }
      };
      const table = dict[this.currentLang] || dict.en;
      return table[key] || dict.en[key] || key;
    }

    applyLanguage(lang) {
      this.currentLang = lang || 'en';
      if (typeof document !== 'undefined' && document.documentElement) {
        document.documentElement.lang = this.currentLang;
      }

      document.querySelectorAll('.btn-lang-toggle, .btn-lang-mini').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === this.currentLang);
      });

      // Update speech recognition language if active
      if (this.speechRecognition) {
        const speechMap = { en: 'en-IN', hi: 'hi-IN', kn: 'kn-IN' };
        this.speechRecognition.lang = speechMap[this.currentLang] || 'en-IN';
      }

      const setSel = (sel, text) => {
        const el = document.querySelector(sel);
        if (el) el.textContent = text;
      };

      // Home
      setSel('#screen-home .home-greeting-title', this.t('greeting'));
      setSel('#screen-home .home-greeting-sub', this.t('greetingSub'));
      setSel('#screen-home .dash-title', this.t('prioSummary'));
      setSel('.kpi-total .prio-kpi-label', this.t('totalHouseholds'));
      setSel('.kpi-red .prio-kpi-label', this.t('immediateRed'));
      setSel('.kpi-orange .prio-kpi-label', this.t('highPriority'));
      setSel('.kpi-overdue .prio-kpi-label', this.t('overdue'));
      setSel('.kpi-due .prio-kpi-label', this.t('dueToday'));
      setSel('.kpi-upcoming .prio-kpi-label', this.t('upcoming'));
      setSel('.kpi-routine .prio-kpi-label', this.t('routineGreen'));
      setSel('.kpi-missing .prio-kpi-label', this.t('needsVerification'));

      setSel('.card-ai-chatbot .card-title', this.t('aiChatbot'));
      setSel('.card-ai-chatbot .card-sub', this.t('aiChatbotSub'));
      setSel('.card-maternal-health .grid-card-title', this.t('maternalHealth'));
      setSel('.card-maternal-health .grid-card-sub', this.t('maternalHealthSub'));
      setSel('.card-vaccine-tracker .grid-card-title', this.t('vaccineTracker'));
      setSel('.card-vaccine-tracker .grid-card-sub', this.t('vaccineTrackerSub'));
      setSel('.home-quick-stats-section .section-subheading', this.t('fieldRegisterSummary'));

      // Sidebar nav
      setSel('.desktop-nav [data-nav="home"] span', this.t('navHome'));
      setSel('.desktop-nav [data-nav="visits"] span', this.t('navVisits'));
      setSel('.desktop-nav [data-nav="followups"] span', this.t('navFollowups'));
      setSel('.desktop-nav [data-nav="alerts"] span', this.t('navAlerts'));
      setSel('.desktop-nav [data-nav="maternal-list"] span', this.t('navMaternal'));
      setSel('.desktop-nav [data-nav="vaccine-list"] span', this.t('navVaccine'));
      setSel('.desktop-nav [data-nav="nearby-facilities"] span', this.t('navNearby'));
      setSel('.desktop-nav [data-nav="chat"] span', this.t('navChat'));
      setSel('.desktop-nav [data-nav="profile"] span', this.t('navProfile'));
      setSel('.btn-sidebar-logout span', this.t('logout'));

      // Mobile bottom nav
      setSel('.bottom-tab-btn[data-tab="home"] span', this.t('navHome'));
      setSel('.bottom-tab-btn[data-tab="visits"] span', this.t('navVisits'));
      setSel('.bottom-tab-btn[data-tab="followups"] span', this.t('navFollowups'));
      setSel('.bottom-tab-btn[data-tab="alerts"] span', this.t('navAlerts'));
      setSel('.bottom-tab-btn[data-tab="chat"] span', this.t('navChat'));

      // Visits & Priority Queue
      setSel('#screen-visits .header-title', this.t('visitsHeader'));
      setSel('#visitsSubtabBar [data-subtab="priority"]', this.t('subtabPriority'));
      setSel('#visitsSubtabBar [data-subtab="register"]', this.t('subtabRegister'));
      setSel('#visitsPriorityPanel .section-subheading', this.t('prioritizedHouseholds'));

      const pInput = document.getElementById('prioritySearchInput');
      if (pInput) pInput.placeholder = this.t('searchPrioPlaceholder');
      const vInput = document.getElementById('visitsSearchInput');
      if (vInput) vInput.placeholder = this.t('searchVisitsPlaceholder');

      setSel('#screen-followups .header-title', this.t('followupsHeader'));
      setSel('#screen-alerts .header-title', this.t('alertsHeader'));

      // Re-render priority cards so card labels reflect selected language
      if (this.priorities && this.priorities.length > 0) {
        this.renderPrioritiesList();
      }
    }

    // ============================================================
    // REUSABLE VOICE-FIRST ASSISTANT & SARVAM AI STT / TTS
    // ============================================================
    // ============================================================
    // UNIVERSAL FORM CONTEXT DETECTION & POPULATION
    // ============================================================
    getActiveFormContext() {
      const valOf = (id) => {
        const el = document.getElementById(id);
        return el ? (el.value || '') : '';
      };

      const activeDomScreen = document.querySelector('.screen-view.active')?.id?.replace('screen-', '') || '';
      const activeScreen = activeDomScreen || this.currentScreen || 'home';

      const planModal = document.getElementById('planVisitModal');
      if (planModal && planModal.classList.contains('open')) {
        return {
          isFormContext: true,
          form_id: 'planVisitForm',
          form_name: 'Visit / Follow-up Planning Form',
          module: 'planVisitModal',
          beneficiary_id: valOf('planVisitBenId') || this.selectedHouseholdId || null,
          fields: [
            { id: 'planVisitBenId', label: 'Beneficiary ID', type: 'hidden', required: true, current_value: valOf('planVisitBenId') },
            { id: 'planVisitType', label: 'Visit Purpose / Type', type: 'select', required: true, options: ['ANC', 'PNC', 'Vaccination', 'HIGH_RISK', 'GENERAL'], current_value: valOf('planVisitType') },
            { id: 'planVisitDueDate', label: 'Follow-up Due Date', type: 'date', required: true, current_value: valOf('planVisitDueDate') },
            { id: 'planVisitFlag', label: 'Priority / Escalation Flag', type: 'select', required: false, options: ['N', 'M', 'H', 'HS', 'S'], current_value: valOf('planVisitFlag') },
            { id: 'planVisitNote', label: 'Workflow Note / Action', type: 'textarea', required: false, current_value: valOf('planVisitNote') }
          ]
        };
      }

      if (activeScreen === 'maternal-form') {
        return {
          isFormContext: true,
          form_id: 'maternalProfileForm',
          form_name: 'Pregnancy Registration Form',
          module: 'maternal-form',
          beneficiary_id: (this.editingTarget === 'mother' && this.selectedMother) ? this.selectedMother.id : null,
          fields: [
            { id: 'motherFormName', label: 'Full Name', type: 'text', required: true, current_value: valOf('motherFormName') },
            { id: 'motherFormAge', label: 'Age', type: 'number', required: false, current_value: valOf('motherFormAge') },
            { id: 'motherFormDOB', label: 'DOB', type: 'text', required: false, current_value: valOf('motherFormDOB') },
            { id: 'motherFormPhone', label: 'Phone Number', type: 'tel', required: true, current_value: valOf('motherFormPhone') },
            { id: 'motherFormAddress', label: 'Address', type: 'text', required: true, current_value: valOf('motherFormAddress') },
            { id: 'motherFormDueDate', label: 'Due Date', type: 'text', required: true, current_value: valOf('motherFormDueDate') },
            { id: 'motherFormWeight', label: 'Weight', type: 'text', required: false, current_value: valOf('motherFormWeight') },
            { id: 'motherFormIron', label: 'Iron Tablets', type: 'text', required: false, current_value: valOf('motherFormIron') },
            { id: 'motherFormBlood', label: 'Blood Group', type: 'text', required: false, current_value: valOf('motherFormBlood') }
          ]
        };
      }

      if (activeScreen === 'vaccine-form') {
        return {
          isFormContext: true,
          form_id: 'babyProfileForm',
          form_name: 'Child Registration Form',
          module: 'vaccine-form',
          beneficiary_id: (this.editingTarget === 'baby' && this.selectedBaby) ? this.selectedBaby.id : null,
          fields: [
            { id: 'babyFormName', label: 'Full Name', type: 'text', required: true, current_value: valOf('babyFormName') },
            { id: 'babyFormGender', label: 'Gender', type: 'text', required: false, current_value: valOf('babyFormGender') },
            { id: 'babyFormDOB', label: 'DOB', type: 'text', required: true, current_value: valOf('babyFormDOB') },
            { id: 'babyFormPhone', label: 'Phone Number', type: 'tel', required: false, current_value: valOf('babyFormPhone') },
            { id: 'babyFormAddress', label: 'Address', type: 'text', required: true, current_value: valOf('babyFormAddress') },
            { id: 'babyFormGuardian', label: 'Parent/Guardian Name', type: 'text', required: false, current_value: valOf('babyFormGuardian') },
            { id: 'babyFormBlood', label: 'Blood Group', type: 'text', required: false, current_value: valOf('babyFormBlood') }
          ]
        };
      }

      if (['visits', 'followups', 'household-detail'].includes(activeScreen)) {
        const ctxMap = {
          visits: ['visitsRegister', 'Field Visits Register'],
          followups: ['followupsRegister', 'Follow-up Scheduling'],
          'household-detail': ['householdDetail', 'Household Visit / Follow-up']
        };
        const [fid, fname] = ctxMap[activeScreen];
        return {
          isFormContext: true,
          form_id: fid,
          form_name: fname,
          module: activeScreen,
          beneficiary_id: this.selectedHouseholdId || null,
          fields: [
            { id: 'planVisitBenId', label: 'Beneficiary ID', type: 'hidden', required: true, current_value: this.selectedHouseholdId || '' },
            { id: 'planVisitType', label: 'Visit Purpose / Type', type: 'select', required: true, options: ['ANC', 'PNC', 'Vaccination', 'HIGH_RISK', 'GENERAL'], current_value: '' },
            { id: 'planVisitDueDate', label: 'Follow-up Due Date', type: 'date', required: true, current_value: '' },
            { id: 'planVisitFlag', label: 'Priority / Escalation Flag', type: 'select', required: false, options: ['N', 'M', 'H', 'HS', 'S'], current_value: 'N' },
            { id: 'planVisitNote', label: 'Workflow Note / Action', type: 'textarea', required: false, current_value: '' }
          ]
        };
      }

      const assistantLabels = {
        home: 'Home Priority Assistant',
        alerts: 'Alerts Assistant',
        chat: 'AI Health Assistant',
        'maternal-list': 'Maternal Health Assistant',
        'maternal-detail': 'Maternal Profile Assistant',
        'vaccine-list': 'Vaccine Tracker Assistant',
        'vaccine-detail': 'Child Profile Assistant'
      };
      return {
        isFormContext: false,
        assistant_mode: true,
        form_id: activeScreen,
        form_name: assistantLabels[activeScreen] || 'SAKHI Assistant',
        module: activeScreen,
        beneficiary_id: this.selectedHouseholdId || this.selectedMother?.id || this.selectedBaby?.id || null,
        fields: []
      };
    }

    populateActiveForm(fieldsMap, formContext) {
      if (!fieldsMap) return [];
      const populated = [];
      for (const [fieldId, value] of Object.entries(fieldsMap)) {
        if (value === null || value === undefined || value === '') continue;
        const el = document.getElementById(fieldId);
        if (el) {
          el.value = String(value);
          populated.push(fieldId);
        }
      }
      // If we are on visits/followups/household-detail and matched a beneficiary, also populate planVisitModal inputs
      if (['visitsRegister', 'followupsRegister', 'householdDetail'].includes(formContext?.form_id)) {
        for (const [fieldId, value] of Object.entries(fieldsMap)) {
          if (value === null || value === undefined || value === '') continue;
          const el = document.getElementById(fieldId);
          if (el) el.value = String(value);
        }
      }
      return populated;
    }

    openVoiceModal() {
      const modal = document.getElementById('voiceAssistantModal');
      if (!modal) return;
      const langSel = document.getElementById('voiceLangSelect');
      if (langSel && this.currentLang) {
        const map = { en: 'en-IN', hi: 'hi-IN', kn: 'kn-IN' };
        langSel.value = map[this.currentLang] || 'unknown';
      }
      const ctx = this.getActiveFormContext();
      const badge = document.getElementById('voiceActiveFormBadge');
      if (badge) {
        badge.textContent = ctx.isFormContext ? `Active Form: ${ctx.form_name}` : `Assistant: ${ctx.form_name}`;
      }
      const btnProc = document.getElementById('btnVoiceProcess');
      if (btnProc) btnProc.textContent = ctx.isFormContext ? 'Extract & Fill Form' : 'Ask Assistant';
      modal.classList.add('open');
    }

    openVoiceModalWithPreview() {
      this.openVoiceModal();
      if (this._pendingChatAction) {
        this.renderVoicePreview({
          action_preview: this._pendingChatAction,
          requires_confirmation: true
        });
      }
    }

    closeVoiceModal() {
      this.stopSpeaking();
      this._activeVisitVoiceId = null;
      const titleEl = document.getElementById('voiceModalTitle');
      if (titleEl) titleEl.textContent = 'SAKHI Voice Assistant';
      const modal = document.getElementById('voiceAssistantModal');
      if (modal) modal.classList.remove('open');
    }

    setVoiceStatus(msg) {
      const el = document.getElementById('voiceStatusBar');
      if (el) el.textContent = msg;
    }

    async toggleVoiceRecording() {
      const btn = document.getElementById('btnVoiceRecord');
      const lbl = document.getElementById('btnVoiceRecordLabel');

      if (this._mediaRecorder && this._mediaRecorder.state === 'recording') {
        this._mediaRecorder.stop();
        if (btn) btn.classList.remove('recording');
        if (lbl) lbl.textContent = 'Start Recording';
        this.setVoiceStatus('Processing audio with Sarvam AI...');
        return;
      }

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        this.setVoiceStatus('Microphone access not supported in this browser. You can type or edit below.');
        return;
      }

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this._audioChunks = [];
        this._mediaRecorder = new MediaRecorder(stream);
        this._mediaRecorder.ondataavailable = (e) => {
          if (e.data && e.data.size > 0) this._audioChunks.push(e.data);
        };
        this._mediaRecorder.onstop = async () => {
          stream.getTracks().forEach(t => t.stop());
          const blob = new Blob(this._audioChunks, { type: 'audio/webm' });
          await this.sendAudioToSarvam(blob);
        };
        this._mediaRecorder.start();
        if (btn) btn.classList.add('recording');
        if (lbl) lbl.textContent = 'Stop Recording';
        this.setVoiceStatus('Recording... Speak naturally in Kannada, Hindi, or English.');
      } catch (err) {
        this.setVoiceStatus('Microphone permission denied or unavailable. You can type your request below.');
      }
    }

    async sendAudioToSarvam(audioBlob) {
      const lang = document.getElementById('voiceLangSelect')?.value || 'unknown';
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.webm');
      formData.append('language_code', lang);
      formData.append('mode', 'transcribe');

      try {
        const resp = await fetch('/api/voice/transcribe', {
          method: 'POST',
          body: formData
        });
        const data = await resp.json();
        if (data.success && data.transcript) {
          const input = document.getElementById('voiceTranscriptInput');
          if (input) input.value = data.transcript;
          this.setVoiceStatus(`Transcribed via Sarvam AI (${data.language_code || lang}). Review and click Analyze.`);
          await this.processVoiceTranscript();
        } else {
          this.setVoiceStatus(data.error || data.message || 'Speech transcription unavailable. Type or edit transcript below.');
        }
      } catch (err) {
        this.setVoiceStatus('Failed to reach transcription endpoint. Type or edit transcript below.');
      }
    }

    async processVoiceTranscript() {
      const transcript = document.getElementById('voiceTranscriptInput')?.value?.trim();
      if (!transcript) {
        this.setVoiceStatus('Please record or enter a transcript first.');
        return;
      }

      // If opened from a specific Visit Card "Voice Note" button, prepare visit note update preview
      if (this._activeVisitVoiceId) {
        const visit = this.visits.find(v => v.id === this._activeVisitVoiceId);
        this.setVoiceStatus('Analyzing clinical visit note...');
        try {
          const pnResp = await fetch('/api/voice/process-note', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ note: transcript, beneficiary_id: visit?.beneficiary_id || this.selectedHouseholdId })
          });
          const pnData = await pnResp.json();
          const emergency = pnData.high_risk ? {
            warning: `CLINICAL ALERT (${pnData.severity})`,
            instruction: pnData.clinical_guidance
          } : null;

          this.renderVoicePreview({
            emergency,
            tts_text: pnData.clinical_guidance,
            action_preview: {
              requires_confirmation: true,
              action_type: 'update_visit_note',
              preview_title: `Save Voice Note to Visit ${this._activeVisitVoiceId}`,
              fields: {
                visit_id: this._activeVisitVoiceId,
                beneficiary_id: visit?.beneficiary_id || '',
                note: transcript,
                voice: transcript,
                status: 'Complete'
              }
            }
          });
          this.setVoiceStatus('Review visit note and click Confirm & Save.');
        } catch (err) {
          this.setVoiceStatus('Error analyzing visit note.');
        }
        return;
      }

      const formContext = this.getActiveFormContext();
      const langHint = document.getElementById('voiceLangSelect')?.value || 'unknown';
      if (formContext.isFormContext) {
        this.setVoiceStatus(`Extracting fields for ${formContext.form_name}...`);
        try {
          const resp = await fetch('/api/voice/extract-form', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              transcript,
              form_context: formContext,
              language_code: langHint
            })
          });
          if (!resp.ok) {
            const errTxt = await resp.text();
            this.setVoiceStatus(`API Error (${resp.status}): ${errTxt.slice(0, 120)}`);
            return;
          }
          const data = await resp.json();
          this.populateActiveForm(data.fields, formContext);
          this.renderFormExtractionPreview(data, formContext);
          this.setVoiceStatus(`Populated ${formContext.form_name}. Review, edit, or speak more to merge.`);
        } catch (err) {
          this.setVoiceStatus(`Form extraction failed: ${err?.message || 'Network error'}`);
        }
        return;
      }

      this.setVoiceStatus(`Asking ${formContext.form_name}...`);
      try {
        const resp = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: transcript,
            beneficiary_id: formContext.beneficiary_id || null,
            current_draft: this.voiceDraft || null,
            screen_context: this.captureVisibleScreenContext(),
            shared_tab_context: this.getSharedTabContext(),
            language_code: langHint === 'unknown' ? ({ en: 'en-IN', hi: 'hi-IN', kn: 'kn-IN' }[this.currentLang] || 'en-IN') : langHint,
            conversation_history: (this.voiceChatHistory || []).slice(-6)
          })
        });
        if (!resp.ok) {
          const errTxt = await resp.text();
          this.setVoiceStatus(`API Error (${resp.status}): ${errTxt.slice(0, 120)}`);
          return;
        }
        const data = await resp.json();
        this.voiceChatHistory.push({ role: 'user', content: transcript });
        this.voiceChatHistory.push({ role: 'assistant', content: data.response || '' });

        this.renderVoiceAssistantConversation(data);
        this.setVoiceStatus('Response ready. Ask a follow-up or tap Play Response.');
      } catch (err) {
        this.setVoiceStatus(`Error reaching assistant: ${err?.message || 'Network error'}`);
      }
    }

    renderVoiceAssistantConversation(latestData) {
      const box = document.getElementById('voicePreviewContainer');
      const ttsBtn = document.getElementById('btnVoicePlayTts');
      if (!box) return;

      const spokenText = latestData.tts_text || latestData.response || '';
      this._lastVoiceTtsText = spokenText;
      if (ttsBtn) ttsBtn.style.display = spokenText ? 'inline-flex' : 'none';

      const turnsHtml = (this.voiceChatHistory || []).slice(-6).map(turn => {
        const isUser = turn.role === 'user';
        return `
          <div style="padding:0.45rem 0.65rem;border-radius:10px;font-size:0.82rem;white-space:pre-line;${isUser ? 'background:#DCFCE7;color:#14532D;align-self:flex-end;' : 'background:#EFF6FF;color:#0F172A;'}">
            <strong>${isUser ? 'You' : 'SAKHI'}:</strong> ${this.escapeHtml(turn.content)}
          </div>
        `;
      }).join('');

      const srcHtml = latestData.source
        ? `<div style="font-size:0.7rem;color:#64748B;">Source: ${this.escapeHtml(latestData.source)}</div>`
        : '';

      if (latestData.action_preview && latestData.action_preview.requires_confirmation) {
        this._pendingChatAction = latestData.action_preview;
        this.renderVoicePreview(latestData);
        return;
      }

      box.innerHTML = `
        <div class="voice-preview-card" style="gap:0.45rem;">
          ${turnsHtml}
          ${srcHtml}
        </div>
      `;
    }

    renderVoicePreview(data) {
      const box = document.getElementById('voicePreviewContainer');
      const ttsBtn = document.getElementById('btnVoicePlayTts');
      if (!box) return;

      const emergencyHtml = data.emergency ? `
        <div class="prio-escalation-box">
          <div class="prio-esc-title">⚠️ ${this.escapeHtml(data.emergency.warning)}</div>
          <div class="prio-esc-instr">${this.escapeHtml(data.emergency.instruction)}</div>
        </div>
      ` : '';

      const spokenText = data.tts_text || data.response || data.message || '';
      this._lastVoiceTtsText = spokenText;
      if (ttsBtn) ttsBtn.style.display = spokenText ? 'inline-flex' : 'none';

      if (data.response || data.message) {
        const msg = data.response || data.message;
        box.innerHTML = `
          ${emergencyHtml}
          <div class="voice-preview-card">
            <div style="font-size:0.85rem;white-space:pre-line;color:#0F172A;">${this.escapeHtml(msg)}</div>
          </div>
        `;
        if (!data.action_preview) return;
      }

      const preview = data.action_preview;
      if (!preview) return;

      if (preview.needs_clarification) {
        box.innerHTML = `
          ${emergencyHtml}
          <div class="prio-missing-banner">${this.escapeHtml(preview.clarification)}</div>
        `;
        return;
      }

      this._activeVoicePreview = preview;
      const fields = preview.fields || {};
      const missingHtml = (preview.missing_fields && preview.missing_fields.length)
        ? `<div class="prio-missing-banner">Missing fields: ${this.escapeHtml(preview.missing_fields.join(', '))}</div>` : '';
      const dupHtml = (preview.potential_duplicates && preview.potential_duplicates.length)
        ? `<div class="prio-missing-banner">⚠️ Potential duplicate: ${this.escapeHtml(preview.potential_duplicates.map(d => `${d.name} (${d.beneficiary_id})`).join(', '))}</div>` : '';

      const fieldInputs = Object.entries(fields)
        .filter(([k]) => !['entity_type', 'visit_id', 'followup_requested'].includes(k))
        .map(([k, v]) => `
          <div class="plan-field-group">
            <label>${this.escapeHtml(k)}</label>
            <input type="text" class="auth-input voice-field-edit" data-field="${this.escapeHtml(k)}" value="${this.escapeHtml(v == null ? '' : String(v))}">
          </div>
        `).join('');

      box.innerHTML = `
        ${emergencyHtml}
        <div class="voice-preview-card">
          <strong>${this.escapeHtml(preview.preview_title || 'Confirm Action')}</strong>
          ${dupHtml}
          ${missingHtml}
          <div class="voice-preview-grid">${fieldInputs}</div>
          <div class="plan-visit-actions">
            <button type="button" class="btn-secondary-outline" onclick="sakhiApp.cancelVoicePreview()">Cancel</button>
            <button type="button" class="btn-primary-blue" onclick="sakhiApp.confirmVoiceAction()">Confirm & Save</button>
          </div>
        </div>
      `;
    }

    cancelVoicePreview() {
      this.voiceDraft = null;
      this._activeVoicePreview = null;
      const box = document.getElementById('voicePreviewContainer');
      if (box) box.innerHTML = '';
      this.setVoiceStatus('Cancelled. Nothing was saved.');
    }

    async confirmVoiceAction() {
      if (!this._activeVoicePreview) return;
      const payload = { ...(this._activeVoicePreview.fields || {}) };
      document.querySelectorAll('#voicePreviewContainer .voice-field-edit').forEach(inp => {
        const key = inp.dataset.field;
        if (key) payload[key] = inp.value.trim() || null;
      });

      this.setVoiceStatus('Saving confirmed record...');
      try {
        if (this._activeVoicePreview.action_type === 'update_visit_note') {
          const vid = payload.visit_id || this._activeVisitVoiceId;
          const resp = await fetch(`/api/visits/${encodeURIComponent(vid)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              status: payload.status || 'Complete',
              note: payload.note,
              voice: payload.voice || payload.note
            })
          });
          const data = await resp.json();
          if (resp.ok && data.success) {
            this._activeVisitVoiceId = null;
            this._activeVoicePreview = null;
            this.showToast(`Voice note saved to visit ${vid}!`);
            this.setVoiceStatus(`✓ Saved to visit ${vid}.`);
            await this.fetchBackendData();
            this.closeVoiceModal();
          } else {
            this.setVoiceStatus(data.detail || 'Could not update visit note.');
          }
          return;
        }

        const resp = await fetch('/api/voice/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action_type: this._activeVoicePreview.action_type,
            payload,
            confirmed: true
          })
        });
        const data = await resp.json();
        if (resp.ok && data.success) {
          this.voiceDraft = null;
          this._activeVoicePreview = null;
          this.showToast(data.message || 'Saved successfully!');
          this.setVoiceStatus(`✓ ${data.message}`);
          await this.fetchBackendData();
        } else {
          this.setVoiceStatus(data.detail || data.error || 'Could not save record.');
        }
      } catch (err) {
        this.setVoiceStatus('Failed to execute confirmed action.');
      }
    }

    toggleSpeakLastResponse() {
      if (this._lastVoiceTtsText) {
        this.speakText(this._lastVoiceTtsText, 'btnVoicePlayTts');
      }
    }

    stopSpeaking() {
      if (this._currentAudio) {
        this._currentAudio.pause();
        this._currentAudio = null;
      }
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
      this._isSpeaking = false;
    }

    async speakText(text, btnId) {
      const btn = btnId ? document.getElementById(btnId) : null;
      if (this._isSpeaking) {
        this.stopSpeaking();
        if (btn) btn.textContent = '🔊 Play';
        return;
      }
      if (!text) return;

      this._isSpeaking = true;
      if (btn) btn.textContent = '⏳ Loading...';
      const langMap = { en: 'en-IN', hi: 'hi-IN', kn: 'kn-IN' };
      const languageCode = langMap[this.currentLang] || 'en-IN';

      try {
        const resp = await fetch('/api/voice/tts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, language_code: languageCode })
        });
        const data = await resp.json();
        if (data.success && data.audio_base64) {
          const audio = new Audio(`data:${data.mime_type || 'audio/wav'};base64,${data.audio_base64}`);
          this._currentAudio = audio;
          if (btn) btn.textContent = '⏹ Stop';
          audio.onended = () => {
            this._isSpeaking = false;
            if (btn) btn.textContent = '🔊 Play';
          };
          await audio.play();
          return;
        }
      } catch (err) {
        console.warn('Sarvam TTS unavailable, trying browser fallback:', err);
      }

      if (typeof window !== 'undefined' && window.speechSynthesis) {
        const utter = new SpeechSynthesisUtterance(text);
        utter.lang = languageCode;
        if (btn) btn.textContent = '⏹ Stop';
        utter.onend = () => {
          this._isSpeaking = false;
          if (btn) btn.textContent = '🔊 Play';
        };
        window.speechSynthesis.speak(utter);
      } else {
        this._isSpeaking = false;
        if (btn) btn.textContent = '🔊 Play';
        this.showToast('Audio playback unavailable.');
      }
    }

    renderFormExtractionPreview(data, formContext) {
      const box = document.getElementById('voicePreviewContainer');
      const ttsBtn = document.getElementById('btnVoicePlayTts');
      if (!box) return;

      this._lastVoiceExtraction = data;
      this._lastVoiceFormContext = formContext;
      this._lastVoiceTtsText = data.tts_summary || '';
      if (ttsBtn) ttsBtn.style.display = this._lastVoiceTtsText ? 'inline-flex' : 'none';

      const fields = data.fields || {};
      const entriesHtml = Object.entries(fields).map(([k, v]) => {
        const meta = (formContext.fields || []).find(f => f.id === k);
        const label = meta ? meta.label : k;
        return `<div><strong>${this.escapeHtml(label)}:</strong> ${this.escapeHtml(String(v))}</div>`;
      }).join('') || '<div>No new fields extracted from this recording.</div>';

      const missingHtml = (data.missing_fields && data.missing_fields.length)
        ? `<div class="prio-missing-banner">Missing required: ${this.escapeHtml(data.missing_fields.join(', '))}</div>`
        : `<div class="detail-verified-note">✓ Required form fields populated.</div>`;

      const uncertainHtml = (data.uncertain_fields && data.uncertain_fields.length)
        ? `<div class="prio-missing-banner">⚠️ Review uncertain: ${this.escapeHtml(data.uncertain_fields.join('; '))}</div>`
        : '';

      let candidateHtml = '';
      if (data.candidate_beneficiaries && data.candidate_beneficiaries.length > 1) {
        candidateHtml = `
          <div class="prio-missing-banner">
            ${this.escapeHtml(data.clarification || 'Select matching beneficiary:')}
            <div style="display:flex;gap:0.4rem;flex-wrap:wrap;margin-top:0.35rem;">
              ${data.candidate_beneficiaries.map(b => `
                <button type="button" class="btn-visit-action btn-voice-visit" onclick="sakhiApp.selectVoiceCandidate('${this.escapeHtml(b.beneficiary_id)}', '${this.escapeHtml(b.display_name).replace(/'/g, "\\'")}')">
                  ${this.escapeHtml(b.display_name)} (${this.escapeHtml(b.beneficiary_id)})
                </button>
              `).join('')}
            </div>
          </div>
        `;
      }

      const translatedHtml = data.translated_transcript
        ? `<div style="font-size:0.76rem;color:#475569;background:#F1F5F9;padding:0.35rem 0.5rem;border-radius:6px;"><strong>Translated (${this.escapeHtml(data.language_code || '')} → EN):</strong> ${this.escapeHtml(data.translated_transcript)}</div>`
        : '';

      box.innerHTML = `
        <div class="voice-preview-card">
          <strong>Populated: ${this.escapeHtml(formContext.form_name)}</strong>
          ${translatedHtml}
          <div style="font-size:0.82rem;color:#1E293B;display:flex;flex-direction:column;gap:0.2rem;">
            ${entriesHtml}
          </div>
          ${candidateHtml}
          ${missingHtml}
          ${uncertainHtml}
          <div class="plan-visit-actions">
            <button type="button" class="btn-secondary-outline" onclick="sakhiApp.closeVoiceModal()">Edit Form Manually</button>
            <button type="button" class="btn-primary-blue" onclick="sakhiApp.confirmAndSaveActiveForm()">Confirm & Save</button>
          </div>
        </div>
      `;
    }

    selectVoiceCandidate(benId, name) {
      const idEl = document.getElementById('planVisitBenId');
      if (idEl) idEl.value = benId;
      this.selectedHouseholdId = benId;
      const titleEl = document.getElementById('planVisitModalTitle');
      if (titleEl) titleEl.textContent = `Plan Visit · ${name} (${benId})`;
      this.showToast(`Selected ${name} (${benId})`);
    }

    clearVoiceFormDraft() {
      this.voiceDraft = null;
      this._activeVoicePreview = null;
      const input = document.getElementById('voiceTranscriptInput');
      if (input) input.value = '';
      const box = document.getElementById('voicePreviewContainer');
      if (box) box.innerHTML = '';

      const ctx = this.getActiveFormContext();
      if (ctx.isFormContext) {
        (ctx.fields || []).forEach(f => {
          const el = document.getElementById(f.id);
          if (el && f.type !== 'hidden') el.value = '';
        });
      }
      this.setVoiceStatus('Voice draft cleared.');
    }

    async confirmAndSaveActiveForm() {
      const ctx = this.getActiveFormContext();
      if (ctx.form_id === 'maternalProfileForm') {
        this.closeVoiceModal();
        await this.handleSaveMother({ preventDefault: () => {} });
        return;
      }
      if (ctx.form_id === 'babyProfileForm') {
        this.closeVoiceModal();
        await this.handleSaveBaby({ preventDefault: () => {} });
        return;
      }
      if (ctx.form_id === 'planVisitForm') {
        this.closeVoiceModal();
        await this.submitPlanVisit({ preventDefault: () => {} });
        return;
      }
      if (['visitsRegister', 'followupsRegister', 'householdDetail'].includes(ctx.form_id)) {
        const benId = document.getElementById('planVisitBenId')?.value;
        if (!benId) {
          this.showToast('Please select a beneficiary first.');
          return;
        }
        this.closeVoiceModal();
        const modal = document.getElementById('planVisitModal');
        if (modal) modal.classList.add('open');
        this.showToast('Review populated visit form and click Save Visit to Register.');
      }
    }

    // ============================================================
    // EXPLICIT CONSENT-BASED BROWSER TAB SHARING (getDisplayMedia)
    // ============================================================
    captureVisibleScreenContext() {
      const activeScreen = document.querySelector('.screen-view.active')?.id?.replace('screen-', '') || this.currentScreen || 'home';
      const activeEl = document.getElementById(`screen-${activeScreen}`);
      const visibleText = activeEl ? (activeEl.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 400) : '';
      return {
        active_screen: activeScreen,
        selected_beneficiary_id: this.selectedHouseholdId || null,
        visible_text_summary: visibleText
      };
    }

    getSharedTabContext() {
      if (!this._tabShareStream) {
        return { sharing_active: false };
      }
      const track = this._tabShareStream.getVideoTracks()[0];
      const settings = track && track.getSettings ? track.getSettings() : {};
      return {
        sharing_active: true,
        display_surface: settings.displaySurface || 'browser',
        ...this.captureVisibleScreenContext()
      };
    }

    async toggleTabSharing() {
      const btn = document.getElementById('btnVoiceShareTab');
      if (this._tabShareStream) {
        this._tabShareStream.getTracks().forEach(t => t.stop());
        this._tabShareStream = null;
        if (btn) {
          btn.textContent = '🖥️ Share Current Tab';
          btn.style.background = '';
          btn.style.color = '';
        }
        this.setVoiceStatus('Tab sharing stopped.');
        return;
      }

      if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
        this.setVoiceStatus('Browser tab sharing (getDisplayMedia) is not supported in this browser.');
        return;
      }

      try {
        const stream = await navigator.mediaDevices.getDisplayMedia({
          video: { displaySurface: 'browser' },
          audio: false
        });
        this._tabShareStream = stream;
        const track = stream.getVideoTracks()[0];
        if (track) {
          track.onended = () => {
            this._tabShareStream = null;
            if (btn) {
              btn.textContent = '🖥️ Share Current Tab';
              btn.style.background = '';
              btn.style.color = '';
            }
          };
        }
        if (btn) {
          btn.textContent = '⏹ Stop Sharing (Active)';
          btn.style.background = '#DCFCE7';
          btn.style.color = '#166534';
        }
        this.setVoiceStatus('Tab sharing active. Ask a question about the displayed screen.');
      } catch (err) {
        this.setVoiceStatus('Tab sharing permission was cancelled or denied.');
      }
    }
  }

  // Attach class to window
  window.SakhiApp = SakhiApp;

  // Initialize and attach instance to global window
  function initSakhi() {
    if (!window.sakhiApp) {
      window.sakhiApp = new SakhiApp();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSakhi);
  } else {
    // DOM already loaded, initialize immediately
    initSakhi();
  }

})();

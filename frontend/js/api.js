const API_BASE = window.location.origin.includes("localhost")
  ? "http://localhost:8000"
  : window.location.origin;

const DEFAULT_AVATAR = "/appphoto.png";

function getProfileImageUrl(img) {
  if (!img) return DEFAULT_AVATAR;
  if (img.startsWith("http")) return img;
  return `${API_BASE}/photos/${img}`;
}

const Auth = {
  saveToken(data) {
    localStorage.setItem("se_token", data.access_token);
    localStorage.setItem("se_user_id", String(data.user_id));
    localStorage.setItem("se_username", data.username);
    localStorage.setItem("se_role", data.role || "");
    localStorage.setItem("se_verified", data.is_verified ? "1" : "0");
  },
  getToken() { return localStorage.getItem("se_token"); },
  getUserId() { return parseInt(localStorage.getItem("se_user_id") || "0", 10); },
  getUsername() { return localStorage.getItem("se_username"); },
  getRole() { return localStorage.getItem("se_role"); },
  isVerified() { return localStorage.getItem("se_verified") === "1"; },
  isLoggedIn() { return !!localStorage.getItem("se_token"); },
  logout() {
    ["se_token", "se_user_id", "se_username", "se_role", "se_verified"]
      .forEach(k => localStorage.removeItem(k));
    window.location.href = "login.html";
  },
  requireAuth() {
    if (!this.isLoggedIn()) { window.location.href = "login.html"; }
  },
  redirectIfAuth() {
    if (this.isLoggedIn()) { window.location.href = "dashboard.html"; }
  },
};

async function apiFetch(path, options = {}) {
  const headers = Object.assign({ "Content-Type": "application/json" }, options.headers || {});
  const token = Auth.getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { message: text }; }

  if (!res.ok) {
    let msg = `Erreur ${res.status}`;
    if (data) {
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          msg = data.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join("\n");
        } else {
          msg = data.detail;
        }
      }
      else if (data.message) msg = data.message;
    }
    throw new Error(msg);
  }
  return data;
}


async function apiFetchForm(path, formData, method = "POST") {
  const headers = {};
  const token = Auth.getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: formData,
  });

  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { message: text }; }

  if (!res.ok) {
    let msg = `Erreur ${res.status}`;
    if (data) {
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          msg = data.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join("\n");
        } else {
          msg = data.detail;
        }
      }
      else if (data.message) msg = data.message;
    }
    throw new Error(msg);
  }
  return data;
}

const API = {
  async register(payload) {
    return apiFetch("/api/auth/register", { method: "POST", body: payload });
  },
  async verifyOtp(email, otp) {
    const data = await apiFetch("/api/auth/verify-otp", { method: "POST", body: { email, otp } });
    Auth.saveToken(data);
    return data;
  },
  async resendOtp(email) {
    return apiFetch("/api/auth/resend-otp", { method: "POST", body: { email } });
  },
  async login(username_or_email, password) {
    const data = await apiFetch("/api/auth/login", { method: "POST", body: { username_or_email, password } });
    Auth.saveToken(data);
    return data;
  },
  async forgotPassword(username_or_email) {
    return apiFetch("/api/auth/forgot-password", { method: "POST", body: { username_or_email } });
  },
  async resetPassword(username_or_email, otp, new_password) {
    return apiFetch("/api/auth/reset-password", { method: "POST", body: { username_or_email, otp, new_password } });
  },
  async changeUnverifiedEmail(old_email, new_email) {
    return apiFetch("/api/auth/change-unverified-email", { method: "POST", body: { old_email, new_email } });
  },
  async setRole(role) {
    return apiFetch("/api/auth/set-role", { method: "POST", body: { role } });
  },
  async saveAthletePreferences(practice_sport, selected_sports, interest_levels) {
    return apiFetch("/api/auth/athlete-preferences", { method: "POST", body: { practice_sport, selected_sports, interest_levels } });
  },
  async saveVisitorPreferences(favorite_sports, notify_sports) {
    return apiFetch("/api/auth/visitor-preferences", { method: "POST", body: { favorite_sports, notify_sports } });
  },
  async registerManager(username, email, password, admin_code) {
    return apiFetch("/api/auth/register-manager", { method: "POST", body: { username, email, password, admin_code } });
  },
  async getMe() {
    return apiFetch("/api/auth/me");
  },
  async getEvents() {
    return apiFetch("/api/events");
  },
  async getEvent(id) {
    return apiFetch(`/api/events/${id}`);
  },
  async createEvent(formData) {
    return apiFetchForm("/api/events", formData, "POST");
  },
  async updateEvent(id, formData) {
    return apiFetchForm(`/api/events/${id}`, formData, "PUT");
  },
  async deleteEvent(id) {
    return apiFetch(`/api/events/${id}`, { method: "DELETE" });
  },
  async addEventPhotos(id, formData) {
    return apiFetchForm(`/api/events/${id}/photos`, formData, "POST");
  },
  async deleteEventPhoto(eventId, photoId) {
    return apiFetch(`/api/events/${eventId}/photos/${photoId}`, { method: "DELETE" });
  },

  async getAdminDashboard() {
    return apiFetch("/api/admin/dashboard");
  },
  async getAdminUsers() {
    return apiFetch("/api/admin/users");
  },
  async deleteUser(id) {
    return apiFetch(`/api/admin/users/${id}`, { method: "DELETE" });
  },
  async createUser(data) {
    return apiFetch("/api/admin/users", { method: "POST", body: data });
  },
  async updateUser(id, data) {
    return apiFetch(`/api/admin/users/${id}`, { method: "PUT", body: data });
  },
  async getSportsConfig() {
    return apiFetch("/api/admin/sports-config");
  },
  async getTeams() {
    return apiFetch("/api/admin/teams");
  },
  async getTeam(id) {
    return apiFetch(`/api/admin/teams/${id}`);
  },
  async createTeam(data) {
    return apiFetch("/api/admin/teams", { method: "POST", body: data });
  },
  async updateTeam(id, data) {
    return apiFetch(`/api/admin/teams/${id}`, { method: "PUT", body: data });
  },
  async deleteTeam(id) {
    return apiFetch(`/api/admin/teams/${id}`, { method: "DELETE" });
  },
  async getTournaments() {
    return apiFetch("/api/admin/tournaments");
  },
  async getTournament(id) {
    return apiFetch(`/api/admin/tournaments/${id}`);
  },
  async createTournament(data) {
    return apiFetch("/api/admin/tournaments", { method: "POST", body: data });
  },
  async deleteTournament(id) {
    return apiFetch(`/api/admin/tournaments/${id}`, { method: "DELETE" });
  },
  async scheduleMatches(tournamentId, matches) {
    return apiFetch(`/api/admin/tournaments/${tournamentId}/schedule`, { method: "PUT", body: { matches } });
  },
  async updateMatch(id, data) {
    return apiFetch(`/api/admin/matches/${id}`, { method: "PUT", body: data });
  },
  async getPlayers() {
    return apiFetch("/api/admin/players");
  },
  async searchPlayers(query) {
    return apiFetch(`/api/admin/players/search?q=${encodeURIComponent(query)}`);
  },
  async getPlayer(id) {
    return apiFetch(`/api/admin/player/${id}`);
  },
  async createBooking(match_id) {
    return apiFetch("/api/admin/bookings", { method: "POST", body: { match_id } });
  },
  async getMyBookings() {
    return apiFetch("/api/admin/bookings/my");
  },
  async getMyCalendar() {
    return apiFetch("/api/admin/calendar");
  },
  // Comments
  async addEventComment(eventId, content) {
    return apiFetch("/api/comments/event", {
      method: "POST",
      body: { event_id: eventId, content }
    });
  },
  async getEventComments(eventId) {
    return apiFetch(`/api/comments/event/${eventId}`);
  },
  async addMatchComment(matchId, content) {
    return apiFetch("/api/comments/match", {
      method: "POST",
      body: { match_id: matchId, content }
    });
  },
  async getMatchComments(matchId) {
    return apiFetch(`/api/comments/match/${matchId}`);
  },
  async deleteComment(type, id) {
    return apiFetch(`/api/comments/${type}/${id}`, { method: "DELETE" });
  },
};


function showToast(message, type = "info", duration = 4000) {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("removing");
    setTimeout(() => toast.remove(), 300);
  }, duration);
}


function setButtonLoading(btn, loading, originalText) {
  if (loading) {
    btn.disabled = true;
    btn.innerHTML = `<span class="btn-spinner"></span> Chargement...`;
  } else {
    btn.disabled = false;
    btn.textContent = originalText;
  }
}

const SPORTS_LIST = [
  "Breaking", "Escalade", "Skateboard", "Surf",
  "Athlétisme", "Aviron", "Badminton", "Basketball",
  "Basketball 3x3", "Boxe", "Canoë course en ligne", "Canoë slalom",
  "Cyclisme sur piste", "Cyclisme sur route", "BMX freestyle",
  "BMX racing", "VTT", "Escrime", "Football",
  "Golf", "Gymnastique artistique", "Gymnastique rythmique",
  "Gymnastique trampoline", "Haltérophilie", "Handball", "Hockey", "Judo",
  "Lutte", "Pentathlon moderne", "Rugby", "Natation",
  "Natation artistique", "Natation marathon", "Plongeon",
  "Water-polo", "Sports équestres", "Taekwondo", "Tennis",
  "Tennis de table", "Tir", "Tir à l'arc", "Triathlon", "Voile",
  "Volleyball", "Beach Volleyball",
];

function sportEmoji(sport) {
  const map = {
    "Football":"⚽","Basketball":"🏀","Basketball 3x3":"🏀","Tennis":"🎾",
    "Volleyball":"🏐","Beach Volleyball":"🏐","Natation":"🏊","Athlétisme":"🏃",
    "Judo":"🥋","Boxe":"🥊","Cyclisme sur route":"🚴","BMX racing":"🚵",
    "Escalade":"🧗","Golf":"⛳","Rugby":"🏉","Handball":"🤾",
    "Hockey":"🏑","Ski":"⛷️","Surf":"🏄","Water-polo":"🤽",
    "Badminton":"🏸","Taekwondo":"🥋","Escrime":"🤺","Haltérophilie":"🏋️",
    "Gymnastique artistique":"🤸","Tir à l'arc":"🏹","Aviron":"🚣",
    "Breaking":"💃","Skateboard":"🛹","Triathlon":"🏊",
  };
  return map[sport] || "🏆";
}

function formatDateFr(dt) {
  if (!dt) return "—";
  return new Date(dt).toLocaleDateString("fr-FR", {
    day: "numeric", month: "long", year: "numeric",
    hour: "2-digit", minute: "2-digit"
  });
}

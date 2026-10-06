
const SECTION_CONFIG = {};

(window.HOMEPAGE_SECTIONS || []).forEach(section => {
    SECTION_CONFIG[section.section_id] = {
        source: section.source,
        value: section.value,
        limit: section.limit || 6
    };
});



function buildPayload() {
    return {
        sections: (window.HOMEPAGE_SECTIONS || []).map(section => ({
            section_id: section.section_id,
            source: section.source,
            value: section.value,
            limit: section.limit || 6
        }))
    };
}


async function loadHomepageSections() {
    const sections = window.HOMEPAGE_SECTIONS || [];

    if (!sections.length) {
        return;
    }

    const cacheKey = "homepage_dynamic_sections";
    const cacheDuration = 330 * 1000; // 5.5 minutes

    const cached = sessionStorage.getItem(cacheKey);

    if (cached) {
        try {
            const cacheData = JSON.parse(cached);

            const age = Date.now() - cacheData.timestamp;

            if (age < cacheDuration) {
                renderSections(
                    cacheData.data.groups || [],
                    cacheData.data.settings
                );

                return;
            }

            // Expired
            sessionStorage.removeItem(cacheKey);

        } catch (e) {
            sessionStorage.removeItem(cacheKey);
        }
    }

    const res = await frappe.call({
        method: "dt_recomendations.api.get_dynamic_sections",
        args: {
            config: {
                sections
            }
        }
    });
    response = res.message || {};
    sessionStorage.setItem(
        cacheKey,
        JSON.stringify({
            timestamp: Date.now(),
            data: response
        })
    );
    renderSections(response.groups || {}, response.settings);;
}

function renderSections(groups, settings) {

    groups.forEach(group => {

        const container = document
            .getElementById(group.section_id)
            ?.querySelector(".row");

        if (!container) return;

        new webshop.ProductGrid({
            items: group.items,
            settings: settings,
            products_section: $(container),
            preference: "Grid View"
        });

    });
}

window.trackSearchClick = function (itemEl) {
    const link = itemEl.closest("a");

    if (!link) return;

    // Prevent attaching the same listener more than once
    if (link.dataset.searchTrackingAttached === "1") {
        return;
    }

    link.dataset.searchTrackingAttached = "1";

    link.addEventListener("click", () => {
        const item_code = link.dataset.itemCode;

        if (!item_code) return;

        const query =
            document.querySelector(".dt-search")?.value || null;

        fetch("/api/method/dt_recomendations.api.log_search_click", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Frappe-CSRF-Token": frappe.csrf_token
            },
            body: JSON.stringify({
                item_code,
                query
            }),
            keepalive: true
        });
    });
};

function attachCatalogSearchTracking() {
    const form = document.querySelector("#dalali-search-form");

    if (!form) {
        return;
    }

    if (form.dataset.searchTrackingAttached === "1") {
        return;
    }

    form.dataset.searchTrackingAttached = "1";

    form.addEventListener("submit", (event) => {
        const formData = new FormData(form);

        // Search text is stored separately
        const query = formData.get("search")?.trim() || null;

        // Everything else becomes catalog filter state
        const filters = {};

        for (const [key, value] of formData.entries()) {
            if (key === "search") {
                continue;
            }

            if (!value) {
                continue;
            }

            // Support fields that can have multiple values
            if (key in filters) {
                if (!Array.isArray(filters[key])) {
                    filters[key] = [filters[key]];
                }

                filters[key].push(value);
            } else {
                filters[key] = value;
            }
        }

        // Determine what caused the submission
        const submitter = event.submitter;

        const action =
            submitter?.dataset.catalogAction ||
            "catalog_search";

        fetch("/api/method/dt_recomendations.api.log_catalog_interaction", {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "X-Frappe-CSRF-Token": frappe.csrf_token
            },

            body: JSON.stringify({
                action,
                query,
                filters
            }),

            keepalive: true
        });
    });
}

function attachCatalogFilterTracking() {
    const form = document.querySelector("#dalali-sidebar-form");
    if (!form) {
        return;
    }
    
    if (form.dataset.filterTrackingAttached === "1") {
        return;
    }

    form.dataset.filterTrackingAttached = "1";

    form.addEventListener("submit", () => {
        const formData = new FormData(form);

        const query = formData.get("search")?.trim() || null;

        const filters = {};

        for (const [key, value] of formData.entries()) {
            if (key === "search") {
                continue;
            }

            if (!value) {
                continue;
            }

            // Support fields such as brands[]
            // that can occur multiple times.
            if (key in filters) {
                if (!Array.isArray(filters[key])) {
                    filters[key] = [filters[key]];
                }

                filters[key].push(value);
            } else {
                filters[key] = value;
            }
        }

        fetch("/api/method/dt_recomendations.api.log_catalog_interaction", {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "X-Frappe-CSRF-Token": frappe.csrf_token
            },

            body: JSON.stringify({
                action: "catalog_filter",
                query,
                filters
            }),

            keepalive: true
        });
    });
}

frappe.ready(function () {
    // Bind once
    webshop.webshop.wishlist.bind_wishlist_action();
    webshop.webshop.shopping_cart.bind_add_to_cart_action();
    loadHomepageSections();
    attachCatalogSearchTracking();
    attachCatalogFilterTracking();
});
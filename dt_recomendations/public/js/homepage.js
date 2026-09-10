
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

frappe.ready(function () {
    // Bind once
    webshop.webshop.wishlist.bind_wishlist_action();
    webshop.webshop.shopping_cart.bind_add_to_cart_action();
    loadHomepageSections();
});
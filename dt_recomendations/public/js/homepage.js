
const SECTION_CONFIG = {
    trending_now: {
        source: "trending",
        limit: 6
    },
    best_sellers: {
        source: "best_sellers",
        limit: 6
    },
    for_you: {
        source: "recommended",
        limit: 6
    },
    category: {
        source: "category",
        value: "",
        limit: 6
    }
};

function getSectionsOnPage() {
    return Object.keys(SECTION_CONFIG).filter(id =>
        document.getElementById(id)
    );
}

function getCategorySections() {
    return [...document.querySelectorAll(".category")];
}

function getCategoryConfigs() {
    const sections = getCategorySections();

    return sections.map(section => {
        const id = section.id;

        if (!id) return null;

        // find inner element with data-item-group
        const inner = section.querySelector("[data-item-group]");
        const value = inner?.dataset.itemGroup;

        if (!value) return null;

        return {
            section_id: id,
            source: "category",
            value: value,
            limit: 6
        };
    }).filter(Boolean);
}

function buildPayload() {
    const staticSections = Object.keys(SECTION_CONFIG)
        .filter(id => id !== "category") // exclude base category template
        .filter(id => document.getElementById(id))
        .map(id => ({
            section_id: id,
            ...SECTION_CONFIG[id]
        }));

    const categorySections = getCategoryConfigs();

    return {
        sections: [
            ...staticSections,
            ...categorySections
        ]
    };
}

async function loadHomepageSections() {
    const payload = buildPayload();

    const res = await frappe.call({
        method: "dt_recomendations.api.get_dynamic_sections",
        args: { config: payload }
    });

    renderSections(res.message);
}

function renderSections(data) {
    
    Object.keys(data).forEach(section_id => {
        const container = document.getElementById(section_id)?.querySelector(".row");

        if (!container) return;

        const items = data[section_id];

        container.innerHTML = items;
    });
}


frappe.ready(function () {
    loadHomepageSections();
});
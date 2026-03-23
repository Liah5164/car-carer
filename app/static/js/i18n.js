const I18N = {
    currentLocale: 'fr',
    translations: {},

    async loadLocale(locale) {
        if (this.translations[locale]) {
            this.currentLocale = locale;
            return;
        }
        try {
            const res = await fetch(`/static/i18n/${locale}.json`);
            if (res.ok) {
                this.translations[locale] = await res.json();
                this.currentLocale = locale;
            }
        } catch (e) {
            console.warn(`i18n: failed to load ${locale}`);
        }
    },

    t(key, params = {}) {
        const keys = key.split('.');
        let val = this.translations[this.currentLocale];
        for (const k of keys) {
            val = val?.[k];
        }
        if (typeof val !== 'string') return key;
        return val.replace(/\{(\w+)\}/g, (_, k) => params[k] ?? `{${k}}`);
    }
};

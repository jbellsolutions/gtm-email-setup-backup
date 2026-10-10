/**
 * Meta Ad Library — Advertiser Extraction
 * Run in browser_console after scrolling to load ads.
 * Returns JSON: { total: N, advertisers: [{name, page_id, page_url}] }
 * 
 * Filters out: system links, l.facebook.com redirects, navigation,
 *   age-confirmation prompts, Instagram embeds, URL shorteners,
 *   marketplace listings, and obvious false positives.
 */

(() => {
    const advertisers = new Map();
    
    document.querySelectorAll('a').forEach(a => {
        const href = a.href || '';
        const text = a.innerText.trim();
        
        // Skip empty or too-short text
        if (!text || text.length < 3) return;
        
        // Skip known noise patterns
        if (href.includes('l.facebook.com')) return;
        if (href.includes('facebook.com/help')) return;
        if (href.includes('facebook.com/ads/about')) return;
        if (href.includes('facebook.com/policies')) return;
        if (href.includes('metastatus.com')) return;
        if (href.includes('facebook.com/ads/library')) return;
        if (href.includes('facebook.com/language')) return;
        
        // Skip noise text patterns
        if (text.includes('confirm your age')) return;
        if (text.includes('Advertising Standards')) return;
        if (text.includes('Log in')) return;
        if (text.includes('Privacy')) return;
        if (text.includes('English')) return;
        if (text.includes('Cookies')) return;
        if (text.includes('Terms')) return;
        if (text.includes('FAQ')) return;
        if (text.includes('System status')) return;
        if (text.includes('Subscribe')) return;
        if (text.includes('Branded Content')) return;
        if (text.includes('Ad Library')) return;
        if (text.includes('See ad')) return;
        if (text.includes('See summary')) return;
        if (text.includes('Open Dropdown')) return;
        if (text.includes('Play')) return;
        if (text.includes('Filters')) return;
        if (text.includes('Search by')) return;
        if (text.includes('About ads')) return;
        if (text.includes('Settings')) return;
        if (text.includes('INSTAGRAM')) return;
        if (text.includes('Visit Instagram')) return;
        if (text.includes('Next items')) return;
        if (text.includes('URLGENI')) return;
        if (text.includes('Shop now')) return;
        if (text.includes('Learn More')) return;
        if (text.includes('Apply now')) return;
        
        // Extract Facebook page ID from URL
        const match = href.match(/facebook\.com\/([^\/\?]+)/);
        if (!match) return;
        
        // Skip known non-advertiser paths
        const pageId = match[1];
        if (pageId.match(/^(help|privacy|policies|ads|language|login|legal|marketplace|profile\.php)$/)) return;
        
        // Only add if we haven't seen this page_id yet
        if (!advertisers.has(pageId)) {
            advertisers.set(pageId, {
                name: text,
                page_id: pageId,
                page_url: href
            });
        }
    });
    
    return JSON.stringify({
        total: advertisers.size,
        advertisers: Array.from(advertisers.values())
    });
})();

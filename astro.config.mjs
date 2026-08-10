import { defineConfig, fontProviders } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  vite: {
    plugins: [tailwindcss()],
  },
  experimental: {
    // Fonts are downloaded at build time, emitted into _astro/fonts and served
    // from our own origin — no runtime requests to fonts.googleapis.com or
    // fonts.gstatic.com. Astro also generates metric-matched fallbacks to keep
    // layout shift down while a face loads.
    fonts: [
      {
        provider: fontProviders.google(),
        name: 'Inter',
        cssVariable: '--font-inter',
        // 400 body, 500 for font-medium. Nothing uses font-semibold, so the
        // 600 the old Google URL requested is dropped.
        weights: [400, 500],
        // Normal only, matching the previous URL: the one sans italic
        // (About.astro) stays browser-synthesised.
        styles: ['normal'],
        fallbacks: ['system-ui', '-apple-system', 'sans-serif'],
      },
      {
        provider: fontProviders.google(),
        name: 'Playfair Display',
        cssVariable: '--font-playfair-display',
        // 700 normal for headings, 400 italic for the hero tagline. This is a
        // cross-product, so 400 normal and 700 italic are also declared; the
        // browser only fetches the faces a page actually uses.
        weights: [400, 700],
        styles: ['normal', 'italic'],
        // Astro defaults to sans-serif; this family needs a serif chain.
        fallbacks: ['Georgia', 'serif'],
      },
    ],
  },
});

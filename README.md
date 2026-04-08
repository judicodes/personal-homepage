# Personal Homepage

Personal website built with [Astro](https://astro.build), [Tailwind CSS v4](https://tailwindcss.com), and TypeScript. Deployed to Vercel.

## Stack

- **Framework:** Astro 5
- **Styles:** Tailwind CSS v4 (CSS-first, no `tailwind.config.js`)
- **Language:** TypeScript
- **Deployment:** Vercel

## Pages

| Route      | Description                       |
| ---------- | --------------------------------- |
| `/`        | Main page — Hero, About, Services |
| `/connect` | Standalone link-tree page         |
| `/imprint` | Legal imprint (§ 5 TMG)           |

## Development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## Dark mode

Dark mode uses Tailwind's class strategy (`.dark` on `<html>`). On first load, `prefers-color-scheme` is respected and the preference is persisted to `localStorage`. A toggle in the nav switches modes manually.

## License

MIT — see [LICENSE](LICENSE).

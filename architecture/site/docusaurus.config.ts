import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'AWS Deploy',
  tagline: 'Architecture decisions and working journal',
  // Published to GitHub Pages under /<repo>/, so links and assets must not be root-absolute.
  url: 'https://juan19932carlos.github.io',
  baseUrl: '/aws-deployments/',
  organizationName: 'juan19932carlos',
  projectName: 'aws-deployments',
  trailingSlash: false,
  onBrokenLinks: 'throw',

  markdown: {
    format: 'detect',
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],

  presets: [
    [
      'classic',
      {
        docs: {
          path: '../decisions',
          routeBasePath: 'decisions',
        },
        blog: false,
        theme: {},
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'journal',
        path: '../journal',
        routeBasePath: 'journal',
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'AWS Deploy',
      items: [
        { to: '/decisions/tech-stack', label: 'Decisions', position: 'right', activeBaseRegex: '/decisions' },
        { to: '/journal/setup-and-gradual-deployment', label: 'Journal', position: 'right', activeBaseRegex: '/journal' },
      ],
    },
    footer: { style: 'light' },
  } satisfies Preset.ThemeConfig,
};

export default config;

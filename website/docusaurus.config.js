import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'PromptVault',
  tagline: 'Open-source prompt versioning, evaluation, and management as an MCP server.',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://krishbnsl.github.io',
  baseUrl: '/promptVault/',

  organizationName: 'KrishBnsl',
  projectName: 'promptVault',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/KrishBnsl/promptVault/tree/main/website/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'PromptVault',
        logo: {
          alt: 'PromptVault logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Docs',
          },
          {
            href: '/promptVault/docs/api-reference',
            label: 'API',
            position: 'left',
          },
          {
            href: 'https://github.com/KrishBnsl/promptVault',
            label: 'GitHub',
            position: 'right',
            className: 'navbar-github-link',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              { label: 'Getting Started', to: '/docs/intro' },
              { label: 'API Reference', to: '/docs/api-reference' },
              { label: 'CLI Reference', to: '/docs/cli-reference' },
            ],
          },
          {
            title: 'Community',
            items: [
              { label: 'GitHub', href: 'https://github.com/KrishBnsl/promptVault' },
              { label: 'Issues', href: 'https://github.com/KrishBnsl/promptVault/issues' },
            ],
          },
          {
            title: 'More',
            items: [
              { label: 'MCP Tools', to: '/docs/mcp-tools' },
              { label: 'Agent Docs (llms.txt)', href: 'https://raw.githubusercontent.com/KrishBnsl/promptVault/main/llms.txt' },
            ],
          },
        ],
        copyright: `Copyright ${new Date().getFullYear()} PromptVault. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['bash', 'json', 'python'],
      },
    }),
};

export default config;

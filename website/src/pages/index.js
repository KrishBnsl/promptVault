import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Get Started
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            href="https://github.com/KrishBnsl/promptVault"
            style={{marginLeft: '1rem'}}>
            GitHub
          </Link>
        </div>
      </div>
    </header>
  );
}

const features = [
  {
    title: 'Version Prompts',
    description: 'Immutable version history with diffs and rollback. Track every change to your prompts like code.',
    icon: '📝',
  },
  {
    title: 'Evaluate Everything',
    description: 'Run prompts against datasets with automatic scoring, cost tracking, and metrics for 23+ LLM models.',
    icon: '📊',
  },
  {
    title: 'MCP Server',
    description: 'Connect directly to Claude Desktop and other MCP clients. 13 tools for full prompt lifecycle management.',
    icon: '🔌',
  },
  {
    title: 'CLI & REST API',
    description: 'Full-featured command line tool and HTTP API. Integrate with any workflow or build custom UIs.',
    icon: '🛠️',
  },
  {
    title: 'Multi-Provider',
    description: 'OpenAI, Anthropic, Google Gemini, and Ollama. Switch providers with a single config change.',
    icon: '🤖',
  },
  {
    title: 'Local-First',
    description: 'SQLite database on your machine. No cloud dependency, no vendor lock-in. MIT licensed.',
    icon: '🏠',
  },
];

function Feature({title, description, icon}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md padding-vert--lg">
        <div style={{fontSize: '3rem', marginBottom: '1rem'}}>{icon}</div>
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {features.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

const quickstart = [
  {
    title: '1. Install',
    code: 'git clone https://github.com/KrishBnsl/promptVault.git\ncd promptVault\nuv sync',
  },
  {
    title: '2. Create Prompt',
    code: 'promptctl prompt create qa-bot \\\n  --content "Answer: {question}" \\\n  --tags "qa"',
  },
  {
    title: '3. Evaluate',
    code: 'promptctl eval run qa-bot \\\n  --dataset test-data \\\n  --model-config \'{"provider":"gemini"}\'',
  },
];

function Quickstart() {
  return (
    <section className={styles.quickstart}>
      <div className="container">
        <Heading as="h2" className="text--center" style={{marginBottom: '2rem'}}>
          Quick Start
        </Heading>
        <div className="row">
          {quickstart.map((step, idx) => (
            <div key={idx} className="col col--4">
              <Heading as="h3">{step.title}</Heading>
              <pre><code>{step.code}</code></pre>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title="Home"
      description={siteConfig.tagline}>
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <Quickstart />
      </main>
    </Layout>
  );
}

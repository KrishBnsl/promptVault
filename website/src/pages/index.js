import {useState} from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

import styles from './index.module.css';

const capabilities = [
  {
    number: '01',
    marker: 'DIFF',
    title: 'Version Prompts',
    description:
      'Immutable version history with diffs and rollback. Track every change to your prompts like code.',
  },
  {
    number: '02',
    marker: 'EVAL',
    title: 'Evaluate Everything',
    description:
      'Run prompts against datasets with automatic scoring, cost tracking, and metrics for 23+ LLM models.',
  },
  {
    number: '03',
    marker: 'MCP',
    title: 'MCP Server',
    description:
      'Connect directly to MCP clients with 14 tools and 4 resources for full prompt lifecycle management.',
  },
  {
    number: '04',
    marker: 'CLI',
    title: 'CLI & REST API',
    description:
      'Use the command line or HTTP API to fit PromptVault into existing workflows and custom tooling.',
  },
  {
    number: '05',
    marker: 'LLM',
    title: 'Multi-Provider',
    description:
      'OpenAI, Anthropic, Google Gemini, and Ollama. Switch providers with a single config change.',
  },
  {
    number: '06',
    marker: 'LOCAL',
    title: 'Local-First',
    description:
      'A SQLite database on your machine. No cloud dependency, no vendor lock-in, and an MIT license.',
  },
];

const quickstart = [
  {
    number: '01',
    title: 'Install',
    code: 'git clone https://github.com/KrishBnsl/promptVault.git\ncd promptVault\nuv sync',
  },
  {
    number: '02',
    title: 'Create Prompt',
    code: 'promptctl prompt create qa-bot \\\n  --content "Answer: {question}" \\\n  --tags "qa"',
  },
  {
    number: '03',
    title: 'Evaluate',
    code: 'promptctl eval run qa-bot \\\n  --dataset test-data \\\n  --model-config \'{"provider":"gemini"}\'',
  },
];

function LedgerPanel() {
  return (
    <div className={styles.ledgerWrap}>
      <span className={styles.ledgerLabel}>Version ledger</span>
      <div className={styles.ledger}>
        <div className={styles.ledgerHeader}>
          <div>
            <strong>support-agent.prompt</strong>
            <span>v12 to v13</span>
          </div>
          <span className={styles.currentBadge}>Current</span>
        </div>
        <div className={styles.diff} aria-label="Example prompt version diff">
          <div className={styles.lineNumbers} aria-hidden="true">
            {['01', '02', '03', '04', '05', '06', '07'].map((line) => (
              <span key={line}>{line}</span>
            ))}
          </div>
          <div className={styles.diffContent}>
            <span><b className={styles.removed}>-</b> Be helpful and concise.</span>
            <span className={styles.removedLine}><b>-</b> Answer every request.</span>
            <span className={styles.addedLine}><b>+</b> Answer using verified context.</span>
            <span className={styles.addedLine}><b>+</b> Cite the source record.</span>
            <span>&nbsp;&nbsp;If context is incomplete:</span>
            <span className={styles.addedLine}><b>+</b> Ask one clarifying question.</span>
            <span>&nbsp;&nbsp;Return: {'{answer}'}</span>
          </div>
        </div>
        <div className={styles.ledgerMeta}>
          <div><span>Commit</span><strong>7f3a91c</strong></div>
          <div><span>Author</span><strong>local</strong></div>
          <div><span>Status</span><strong className={styles.saved}>Saved</strong></div>
        </div>
      </div>
    </div>
  );
}

function HomepageHeader() {
  return (
    <header className={styles.hero}>
      <div className={styles.heroInner}>
        <div className={styles.heroCopy}>
          <p className={styles.eyebrow}>
            <span /> Open-source prompt operations
          </p>
          <h1>
            Every prompt has a <span className={styles.highlight}>record.</span>
          </h1>
          <p className={styles.lede}>
            Version, evaluate, and manage production prompts with a local-first
            ledger built for serious engineering workflows.
          </p>
          <div className={styles.actions}>
            <Link className={styles.primaryAction} to="/docs/intro">
              Get Started <span aria-hidden="true">↗</span>
            </Link>
            <Link
              className={styles.secondaryAction}
              href="https://github.com/KrishBnsl/promptVault">
              GitHub
            </Link>
          </div>
        </div>
        <LedgerPanel />
      </div>
    </header>
  );
}

function ProofRail() {
  const proof = [
    ['SELF-HOSTED', 'Local control'],
    ['SQLITE', 'Portable data'],
    ['MIT', 'Open source'],
    ['14', 'MCP tools'],
    ['4', 'Resources'],
  ];

  return (
    <section className={styles.proofRail} aria-label="PromptVault technical facts">
      <div className={styles.proofInner}>
        {proof.map(([value, label]) => (
          <div className={styles.proofItem} key={value}>
            <strong>{value}</strong>
            <span>{label}</span>
          </div>
        ))}
        <div className={styles.providers}>
          OpenAI / Anthropic / Gemini / Ollama
        </div>
      </div>
    </section>
  );
}

function Capabilities() {
  return (
    <section className={styles.capabilities} aria-labelledby="capabilities-title">
      <div className={styles.sectionInner}>
        <div className={styles.sectionHeading}>
          <div>
            <p className={styles.sectionLabel}>01 / Capabilities</p>
            <h2 id="capabilities-title">A disciplined prompt workbench.</h2>
          </div>
          <p>
            Version control, evaluation, and delivery tools arranged around a
            local source of truth.
          </p>
        </div>
        <div className={styles.capabilityGrid}>
          {capabilities.map((capability) => (
            <article className={styles.capability} key={capability.number}>
              <div className={styles.capabilityTop}>
                <span>{capability.number}</span>
                <strong>{capability.marker}</strong>
              </div>
              <h3>{capability.title}</h3>
              <p>{capability.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function CopyButton({code}) {
  const [copied, setCopied] = useState(false);

  async function copyCode() {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <button type="button" className={styles.copyButton} onClick={copyCode}>
      {copied ? 'Copied' : 'Copy'}
    </button>
  );
}

function Quickstart() {
  return (
    <section className={styles.quickstart} aria-labelledby="quick-start-title">
      <div className={styles.sectionInner}>
        <div className={styles.sectionHeading}>
          <div>
            <p className={styles.sectionLabel}>02 / First run</p>
            <h2 id="quick-start-title">Quick Start</h2>
          </div>
          <p>Three commands from local checkout to a repeatable prompt evaluation.</p>
        </div>
        <div className={styles.quickstartGrid}>
          {quickstart.map((step) => (
            <article className={styles.commandCard} key={step.number}>
              <div className={styles.commandHeader}>
                <div>
                  <span>{step.number}</span>
                  <h3>{step.title}</h3>
                </div>
                <CopyButton code={step.code} />
              </div>
              <div className={styles.commandBody}>
                <div className={styles.windowBar}>
                  <i /><i /><i />
                  <span>shell</span>
                </div>
                <pre><code>{step.code}</code></pre>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout title="Home" description={siteConfig.tagline}>
      <main className={styles.page}>
        <HomepageHeader />
        <ProofRail />
        <Capabilities />
        <Quickstart />
      </main>
    </Layout>
  );
}

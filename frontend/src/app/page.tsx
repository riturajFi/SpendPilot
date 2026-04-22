import {
  appConfig,
  brandPalette,
  brandSpacing,
  brandTypography,
} from "@/common/config/brand";

const portfolioStats = [
  {
    label: "Monthly budget",
    value: "$4,800",
    change: "+12% vs last month",
  },
  {
    label: "Spent so far",
    value: "$3,140",
    change: "65% of target",
  },
  {
    label: "Saved this month",
    value: "$1,660",
    change: "On track",
  },
] as const;

const spendingBuckets = [
  {
    name: "Housing",
    amount: "$1,420",
    width: "76%",
  },
  {
    name: "Food",
    amount: "$540",
    width: "44%",
  },
  {
    name: "Transport",
    amount: "$285",
    width: "28%",
  },
  {
    name: "Fun",
    amount: "$190",
    width: "18%",
  },
] as const;

const activityFeed = [
  "Card payment cleared for grocery run",
  "Savings rule moved $250 into emergency fund",
  "Rent forecast stable for next billing cycle",
] as const;

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="dashboard-shell">
        <div className="dashboard">
          <div className="hero-card section-block">
          <div className="hero-copy-block">
            <p className="eyebrow">Finance cockpit</p>
            <h1>{appConfig.name}</h1>
            <p className="hero-copy">
              Sample frontend built from centralized design tokens. Palette,
              spacing, typography all read from shared config.
            </p>
          </div>

          <div className="hero-actions">
            <button className="primary-button" type="button">
              Review budget
            </button>
            <button className="secondary-button" type="button">
              View reports
            </button>
          </div>
          </div>

          <section className="stats-grid section-block">
            {portfolioStats.map((stat) => (
              <article className="stat-card stat-divider" key={stat.label}>
                <span>{stat.label}</span>
                <strong>{stat.value}</strong>
                <p>{stat.change}</p>
              </article>
            ))}
          </section>

          <section className="content-grid">
            <article className="feature-panel section-block">
              <div className="section-heading">
                <p className="eyebrow">Category usage</p>
                <h2>Live spend breakdown</h2>
              </div>

              <div className="bucket-list">
                {spendingBuckets.map((bucket) => (
                  <div className="bucket-row" key={bucket.name}>
                    <div className="bucket-meta">
                      <span>{bucket.name}</span>
                      <strong>{bucket.amount}</strong>
                    </div>
                    <div className="progress-track">
                      <div
                        className="progress-fill"
                        style={{ width: bucket.width }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className="activity-panel section-block">
              <div className="section-heading">
                <p className="eyebrow">Recent moves</p>
                <h2>Smart activity feed</h2>
              </div>

              <div className="activity-list">
                {activityFeed.map((item) => (
                  <div className="activity-item" key={item}>
                    <div className="activity-dot" />
                    <p>{item}</p>
                  </div>
                ))}
              </div>
            </article>
          </section>

          <section className="token-panel section-block">
            <div className="section-heading">
              <p className="eyebrow">Shared tokens</p>
              <h2>Frontend reads config, not magic numbers</h2>
            </div>

            <div className="token-grid">
              <article>
                <span>Button</span>
                <strong>{brandPalette.button}</strong>
              </article>
              <article>
                <span>Text</span>
                <strong>{brandPalette.text}</strong>
              </article>
              <article>
                <span>Background</span>
                <strong>{brandPalette.background}</strong>
              </article>
              <article>
                <span>Font</span>
                <strong>{brandTypography.primaryFont}</strong>
              </article>
              <article>
                <span>Page padding</span>
                <strong>
                  {brandSpacing.pagePaddingY} / {brandSpacing.pagePaddingX}
                </strong>
              </article>
              <article>
                <span>Body font</span>
                <strong>{brandTypography.fontSize.body}</strong>
              </article>
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}

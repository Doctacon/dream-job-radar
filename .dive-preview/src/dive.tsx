import { useSQLQuery } from "@motherduck/react-sql-query";

const N = (v: unknown): number => (v != null ? Number(v) : 0);

const TABLE = `"acorn-granary"."main"."current_open_roles"`;
const MART_TABLE = `"acorn-granary"."mart"."job_postings_daily_snapshot"`;
const RECENT_FILTER = "coalesce(posted_at, first_seen_at) >= current_date - INTERVAL 6 DAY";

// Light-mode theme — loughondata palette flipped for sunlight
// readability. Direct sunlight wrecks dark UI; high contrast on white
// stays legible.
const T = {
  bg: "#ffffff",
  text: "#101515",       // neutral-900
  muted: "#435d59",      // neutral-600
  faint: "#547570",      // neutral-500
  border: "#8faeaa",     // neutral-300
  borderSoft: "#bcceca", // neutral-200
  borderFaint: "#e8eeed",// neutral-100 (row separators)
  accent: "#078677",     // primary-800 — deep teal for link text
  accentHover: "#09ad99",// primary-700
};

export default function DreamJobRadar() {
  const summary = useSQLQuery(`
    SELECT
      count(*) AS total_roles,
      count(DISTINCT company) AS companies,
      count(DISTINCT location) AS locations,
      strftime(max(last_seen_at), '%Y-%m-%d %H:%M UTC') AS last_refresh
    FROM ${TABLE}
    WHERE ${RECENT_FILTER}
  `);

  const roles = useSQLQuery(`
    SELECT
      company,
      title,
      coalesce(location, '—') AS location,
      coalesce(
        strftime(posted_at, '%Y-%m-%d'),
        strftime(first_seen_at, '%Y-%m-%d')
      ) AS posted_at,
      url
    FROM ${TABLE}
    WHERE ${RECENT_FILTER}
    ORDER BY coalesce(posted_at, first_seen_at) DESC NULLS LAST
  `);

  const snapshots = useSQLQuery(`
    SELECT
      strftime(snapshot_date, '%Y-%m-%d') AS snapshot_date,
      count(*) AS roles
    FROM ${MART_TABLE}
    GROUP BY snapshot_date
    ORDER BY snapshot_date
  `);

  const summaryRow = (Array.isArray(summary.data) ? summary.data : [])[0] ?? {};
  const roleRows = Array.isArray(roles.data) ? roles.data : [];
  const snapshotRows = Array.isArray(snapshots.data) ? snapshots.data : [];

  return (
    <div
      className="p-4 sm:p-8"
      style={{
        background: T.bg,
        color: T.text,
        minHeight: "100%",
        fontFamily: "ui-sans-serif, system-ui, -apple-system, sans-serif",
      }}
    >
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <h1
          className="text-2xl sm:text-4xl font-bold tracking-tight"
          style={{ color: T.text }}
        >
          Dream Job Radar
        </h1>
        <p className="text-sm mt-3 mb-10" style={{ color: T.muted, lineHeight: 1.6 }}>
          Open roles posted (or first observed) in the last 7 days, across a
          hand-picked list of outdoor, geospatial, and mission-aligned
          companies. Filtered to data, engineering, GIS and geospatial
          titles.
          {summaryRow.last_refresh ? (
            <>
              {" "}
              Last refresh:{" "}
              <span style={{ color: T.text, fontWeight: 500 }}>
                {String(summaryRow.last_refresh)}
              </span>
              .
            </>
          ) : null}
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 sm:gap-10 mb-12">
          <KPI loading={summary.isLoading} value={N(summaryRow.total_roles)} label="Open roles" />
          <KPI loading={summary.isLoading} value={N(summaryRow.companies)} label="Companies" />
          <KPI loading={summary.isLoading} value={N(summaryRow.locations)} label="Locations" />
          <KPI loading={summary.isLoading} value={N(roleRows.length)} label="Rows shown" />
        </div>

        <h2
          className="text-lg font-semibold mb-4 pb-3"
          style={{ color: T.text, borderBottom: `1px solid ${T.border}` }}
        >
          Daily snapshot history
        </h2>
        <p className="text-sm mb-4" style={{ color: T.muted, lineHeight: 1.6 }}>
          Open-role count snapshotted once per UTC day into Apache Iceberg
          on Cloudflare R2 (R2 Data Catalog), then materialized back into
          MotherDuck for this view.
        </p>
        <SnapshotStrip rows={snapshotRows} loading={snapshots.isLoading} />
        <div className="mb-12" />

        <h2
          className="text-lg font-semibold mb-4 pb-3"
          style={{ color: T.text, borderBottom: `1px solid ${T.border}` }}
        >
          Recent roles
        </h2>

        {roles.isLoading ? (
          <div className="animate-pulse space-y-3">
            <div className="h-6 rounded w-full" style={{ background: T.borderFaint }} />
            <div className="h-6 rounded w-full" style={{ background: T.borderFaint }} />
            <div className="h-6 rounded w-3/4" style={{ background: T.borderFaint }} />
          </div>
        ) : (
          <table className="w-full text-sm" style={{ color: T.text, borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${T.borderSoft}` }}>
                <Th>Company</Th>
                <Th>Title</Th>
                <Th hideOnMobile>Location</Th>
                <Th>Posted</Th>
              </tr>
            </thead>
            <tbody>
              {roleRows.map((r, i) => {
                const url = String(r.url ?? "");
                const title = String(r.title ?? "").trim();
                const titleEl = url ? (
                  <a
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: T.accent, textDecoration: "underline", fontWeight: 500 }}
                    onMouseEnter={(e) => (e.currentTarget.style.color = T.accentHover)}
                    onMouseLeave={(e) => (e.currentTarget.style.color = T.accent)}
                  >
                    {title}
                  </a>
                ) : (
                  <span>{title}</span>
                );
                return (
                  <tr
                    key={i}
                    style={{ borderBottom: `1px solid ${T.borderFaint}`, verticalAlign: "top" }}
                  >
                    <td className="py-3 pr-4 whitespace-nowrap" style={{ color: T.muted }}>
                      {String(r.company ?? "")}
                    </td>
                    <td className="py-3 pr-4">
                      {titleEl}
                      <div className="text-xs mt-1 sm:hidden" style={{ color: T.faint }}>
                        {String(r.location ?? "")}
                      </div>
                    </td>
                    <td className="py-3 pr-4 hidden sm:table-cell" style={{ color: T.faint }}>
                      {String(r.location ?? "")}
                    </td>
                    <td className="py-3 whitespace-nowrap" style={{ color: T.faint }}>
                      {String(r.posted_at ?? "")}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}

        <p className="text-xs mt-12" style={{ color: T.faint, lineHeight: 1.7 }}>
          Source: dream-job-radar pipeline → Cloudflare R2 → MotherDuck view{" "}
          <code
            style={{
              color: T.muted,
              background: T.borderFaint,
              padding: "1px 6px",
              borderRadius: 4,
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
            }}
          >
            current_open_roles
          </code>
          . Posted column falls back to the first-observed date when the
          upstream source does not expose a posting timestamp.
        </p>
      </div>
    </div>
  );
}

function KPI({ loading, value, label }: { loading: boolean; value: number; label: string }) {
  return (
    <div>
      {loading ? (
        <div
          className="h-10 sm:h-12 w-20 rounded animate-pulse"
          style={{ background: T.borderFaint }}
        />
      ) : (
        <p
          className="text-3xl sm:text-5xl font-bold tabular-nums"
          style={{ color: T.text, letterSpacing: "-0.02em" }}
        >
          {value}
        </p>
      )}
      <p className="text-sm mt-2" style={{ color: T.muted }}>
        {label}
      </p>
    </div>
  );
}

function SnapshotStrip({
  rows,
  loading,
}: {
  rows: Array<Record<string, unknown>>;
  loading: boolean;
}) {
  if (loading) {
    return (
      <div
        className="animate-pulse rounded"
        style={{ height: 48, background: T.borderFaint }}
      />
    );
  }
  if (rows.length === 0) {
    return (
      <p className="text-xs" style={{ color: T.faint }}>
        No snapshots yet.
      </p>
    );
  }
  const max = Math.max(1, ...rows.map((r) => Number(r.roles ?? 0)));
  return (
    <div
      style={{
        display: "flex",
        alignItems: "flex-end",
        gap: 4,
        height: 48,
        padding: "4px 0",
        borderBottom: `1px solid ${T.borderFaint}`,
      }}
    >
      {rows.map((r, i) => {
        const v = Number(r.roles ?? 0);
        const h = Math.max(2, Math.round((v / max) * 40));
        return (
          <div
            key={i}
            title={`${String(r.snapshot_date)}: ${v} open roles`}
            style={{
              flex: 1,
              height: `${h}px`,
              background: T.accent,
              borderRadius: 2,
            }}
          />
        );
      })}
    </div>
  );
}

function Th({
  children,
  hideOnMobile = false,
}: {
  children: React.ReactNode;
  hideOnMobile?: boolean;
}) {
  return (
    <th
      className={`text-left py-3 pr-4 font-medium text-xs ${
        hideOnMobile ? "hidden sm:table-cell" : ""
      }`}
      style={{ color: T.faint, textTransform: "uppercase", letterSpacing: "0.05em" }}
    >
      {children}
    </th>
  );
}

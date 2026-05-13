import { useSQLQuery } from "@motherduck/react-sql-query";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export const REQUIRED_DATABASES = [
  { type: "database", path: "md:acorn-granary", alias: "acorn-granary" },
];

const N = (v: unknown): number => (v != null ? Number(v) : 0);

const RELEVANT_TABLE = `"acorn-granary"."main"."relevant_open_roles"`;
const INVENTORY_TABLE = `"acorn-granary"."main"."current_open_roles"`;
const MART_TABLE = `"acorn-granary"."mart"."job_postings_daily_snapshot"`;
const RECENT_FILTER = "coalesce(posted_at, first_seen_at) >= current_date - INTERVAL 6 DAY";

const T = {
  bg: "#ffffff",
  text: "#101515",
  muted: "#435d59",
  faint: "#547570",
  border: "#8faeaa",
  borderSoft: "#bcceca",
  borderFaint: "#e8eeed",
  accent: "#078677",
  accentHover: "#09ad99",
  warm: "#b86e2f",
};

export default function DreamJobRadar() {
  const inventory = useSQLQuery(`
    SELECT
      count(*) AS total_roles,
      count(DISTINCT company) AS companies,
      count(DISTINCT location) AS locations,
      strftime(max(last_seen_at), '%Y-%m-%d %H:%M UTC') AS last_refresh
    FROM ${RELEVANT_TABLE}
  `);

  const recent = useSQLQuery(`
    SELECT
      count(*) AS recent_roles,
      count(DISTINCT company) AS recent_companies
    FROM ${RELEVANT_TABLE}
    WHERE ${RECENT_FILTER}
  `);

  const snapshots = useSQLQuery(`
    SELECT
      strftime(snapshot_date, '%Y-%m-%d') AS snapshot_date,
      count(*) AS roles
    FROM ${MART_TABLE}
    GROUP BY snapshot_date
    ORDER BY snapshot_date
  `);

  const companyCoverage = useSQLQuery(`
    SELECT
      company,
      count(*) AS roles,
      count(*) FILTER (WHERE ${RECENT_FILTER}) AS recent_roles
    FROM ${RELEVANT_TABLE}
    GROUP BY company
    ORDER BY roles DESC, company
    LIMIT 8
  `);

  const sourceCoverage = useSQLQuery(`
    SELECT
      source_kind,
      count(*) AS roles,
      count(DISTINCT company) AS companies
    FROM ${RELEVANT_TABLE}
    GROUP BY source_kind
    ORDER BY roles DESC, source_kind
  `);

  const roles = useSQLQuery(`
    SELECT
      company,
      source_kind,
      title,
      coalesce(location, '—') AS location,
      coalesce(
        strftime(posted_at, '%Y-%m-%d'),
        strftime(first_seen_at, '%Y-%m-%d')
      ) AS role_date,
      url
    FROM ${RELEVANT_TABLE}
    WHERE ${RECENT_FILTER}
    ORDER BY coalesce(posted_at, first_seen_at) DESC NULLS LAST, company, title
    LIMIT 10
  `);

  const inventoryRow = (Array.isArray(inventory.data) ? inventory.data : [])[0] ?? {};
  const recentRow = (Array.isArray(recent.data) ? recent.data : [])[0] ?? {};
  const snapshotRows = Array.isArray(snapshots.data) ? snapshots.data : [];
  const companyRows = Array.isArray(companyCoverage.data) ? companyCoverage.data : [];
  const sourceRows = Array.isArray(sourceCoverage.data) ? sourceCoverage.data : [];
  const roleRows = Array.isArray(roles.data) ? roles.data : [];

  return (
    <div
      className="p-4 sm:p-6"
      style={{
        background: T.bg,
        color: T.text,
        minHeight: "100%",
        fontFamily: "ui-sans-serif, system-ui, -apple-system, sans-serif",
      }}
    >
      <div style={{ maxWidth: 980, margin: "0 auto" }}>
        <header className="mb-6">
          <p className="text-xs font-semibold uppercase tracking-wide mb-2" style={{ color: T.accent }}>
            Personalized opportunity radar
          </p>
          <h1 className="text-2xl sm:text-4xl font-bold tracking-tight" style={{ color: T.text }}>
            Dream Job Radar
          </h1>
          <p className="text-sm mt-3" style={{ color: T.muted, lineHeight: 1.6 }}>
            Location-relevant open roles across hand-picked outdoor, geospatial, and
            mission-aligned companies. The primary metrics use the personalized relevance
            view: explicit remote US/worldwide roles and explicit Arizona-local roles.
            Full inventory remains available separately for debugging.
            {inventoryRow.last_refresh ? (
              <>
                {" "}Last refresh:{" "}
                <span style={{ color: T.text, fontWeight: 600 }}>
                  {String(inventoryRow.last_refresh)}
                </span>
                .
              </>
            ) : null}
          </p>
        </header>

        <section className="grid grid-cols-2 sm:grid-cols-4 gap-5 sm:gap-8 mb-8">
          <KPI loading={inventory.isLoading} value={N(inventoryRow.total_roles)} label="Relevant open roles" />
          <KPI loading={inventory.isLoading} value={N(inventoryRow.companies)} label="Companies covered" />
          <KPI loading={inventory.isLoading} value={N(inventoryRow.locations)} label="Locations" />
          <KPI loading={recent.isLoading} value={N(recentRow.recent_roles)} label="New/recent this week" tone="warm" />
        </section>

        <section className="mb-8">
          <SectionTitle eyebrow="Full inventory history" title="Daily UTC snapshots" />
          <p className="text-sm mb-3" style={{ color: T.muted, lineHeight: 1.6 }}>
            Each point is the full current matching open-role inventory from {INVENTORY_TABLE},
            captured once per UTC day in the Iceberg mart. It is intentionally broader than
            the personalized relevant-role counts above.
          </p>
          <SnapshotTrend rows={snapshotRows} loading={snapshots.isLoading} />
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-8">
          <div className="lg:col-span-3">
            <SectionTitle eyebrow="Relevant coverage" title="Companies with relevant matches" />
            <CompanyTable rows={companyRows} loading={companyCoverage.isLoading} />
          </div>
          <div className="lg:col-span-2">
            <SectionTitle eyebrow="Relevant source mix" title="Source coverage" />
            <SourceList rows={sourceRows} loading={sourceCoverage.isLoading} />
          </div>
        </section>

        <section>
          <SectionTitle eyebrow="Recent relevant lens" title="Relevant roles posted or first observed in the last 7 days" />
          <RecentRoles rows={roleRows} loading={roles.isLoading} />
        </section>

        <p className="text-xs mt-8" style={{ color: T.faint, lineHeight: 1.7 }}>
          Source: dream-job-radar pipeline to Cloudflare R2, MotherDuck relevance view{" "}
          <code
            style={{
              color: T.muted,
              background: T.borderFaint,
              padding: "1px 6px",
              borderRadius: 4,
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
            }}
          >
            relevant_open_roles
          </code>
          , full-inventory view <code
            style={{
              color: T.muted,
              background: T.borderFaint,
              padding: "1px 6px",
              borderRadius: 4,
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
            }}
          >
            current_open_roles
          </code>, and Iceberg mart table{" "}
          <code
            style={{
              color: T.muted,
              background: T.borderFaint,
              padding: "1px 6px",
              borderRadius: 4,
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
            }}
          >
            job_postings_daily_snapshot
          </code>
          . Posted dates fall back to first-observed dates when upstream sources omit a posting timestamp.
        </p>
      </div>
    </div>
  );
}

function KPI({
  loading,
  value,
  label,
  tone = "accent",
}: {
  loading: boolean;
  value: number;
  label: string;
  tone?: "accent" | "warm";
}) {
  return (
    <div>
      {loading ? (
        <div className="h-10 sm:h-12 w-20 rounded animate-pulse" style={{ background: T.borderFaint }} />
      ) : (
        <p
          className="text-3xl sm:text-5xl font-bold tabular-nums"
          style={{ color: tone === "warm" ? T.warm : T.text, letterSpacing: "-0.02em" }}
        >
          {value}
        </p>
      )}
      <p className="text-xs sm:text-sm mt-2" style={{ color: T.muted, lineHeight: 1.3 }}>
        {label}
      </p>
    </div>
  );
}

function SectionTitle({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div className="mb-3 pb-2" style={{ borderBottom: `1px solid ${T.borderSoft}` }}>
      <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: T.faint }}>
        {eyebrow}
      </p>
      <h2 className="text-lg font-semibold" style={{ color: T.text }}>
        {title}
      </h2>
    </div>
  );
}

function SnapshotTrend({ rows, loading }: { rows: Array<Record<string, unknown>>; loading: boolean }) {
  if (loading) {
    return <div className="animate-pulse rounded" style={{ height: 210, background: T.borderFaint }} />;
  }

  if (rows.length === 0) {
    return (
      <p className="text-sm" style={{ color: T.faint }}>
        No inventory snapshots have been materialized yet.
      </p>
    );
  }

  const data = rows.map((row) => ({
    snapshot_date: String(row.snapshot_date ?? ""),
    roles: N(row.roles),
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 8, right: 12, bottom: 4, left: 0 }}>
        <CartesianGrid stroke={T.borderFaint} strokeDasharray="3 3" />
        <XAxis dataKey="snapshot_date" fontSize={11} tick={{ fill: T.faint }} />
        <YAxis fontSize={11} tick={{ fill: T.faint }} width={36} domain={["dataMin - 2", "dataMax + 2"]} />
        <Tooltip formatter={(value) => [`${N(value)} roles`, "Inventory"]} labelFormatter={(label) => `UTC ${label}`} />
        <Line type="linear" dataKey="roles" stroke={T.accent} strokeWidth={2.5} dot={{ r: 3 }} activeDot={{ r: 5 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function CompanyTable({ rows, loading }: { rows: Array<Record<string, unknown>>; loading: boolean }) {
  if (loading) {
    return <SkeletonRows count={4} />;
  }

  if (rows.length === 0) {
    return <EmptyText>No companies currently have relevant open roles.</EmptyText>;
  }

  return (
    <table className="w-full text-sm" style={{ color: T.text, borderCollapse: "collapse" }}>
      <thead>
        <tr style={{ borderBottom: `1px solid ${T.borderSoft}` }}>
          <Th>Company</Th>
          <Th align="right">Relevant</Th>
          <Th align="right">Recent</Th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={String(row.company ?? "")} style={{ borderBottom: `1px solid ${T.borderFaint}` }}>
            <td className="py-2 pr-4" style={{ color: T.muted }}>
              {String(row.company ?? "")}
            </td>
            <td className="py-2 pr-4 text-right tabular-nums">{N(row.roles)}</td>
            <td className="py-2 text-right tabular-nums" style={{ color: N(row.recent_roles) > 0 ? T.warm : T.faint }}>
              {N(row.recent_roles)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function SourceList({ rows, loading }: { rows: Array<Record<string, unknown>>; loading: boolean }) {
  if (loading) {
    return <SkeletonRows count={3} />;
  }

  if (rows.length === 0) {
    return <EmptyText>No relevant source coverage is available.</EmptyText>;
  }

  const max = Math.max(1, ...rows.map((row) => N(row.roles)));

  return (
    <div className="space-y-3">
      {rows.map((row) => {
        const roles = N(row.roles);
        return (
          <div key={String(row.source_kind ?? "")}>
            <div className="flex items-baseline justify-between gap-4 text-sm">
              <span style={{ color: T.muted }}>{String(row.source_kind ?? "")}</span>
              <span className="tabular-nums" style={{ color: T.text }}>
                {roles} roles / {N(row.companies)} companies
              </span>
            </div>
            <div className="mt-1" style={{ height: 6, background: T.borderFaint }}>
              <div style={{ height: 6, width: `${Math.max(4, (roles / max) * 100)}%`, background: T.accent }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function RecentRoles({ rows, loading }: { rows: Array<Record<string, unknown>>; loading: boolean }) {
  if (loading) {
    return <SkeletonRows count={5} />;
  }

  if (rows.length === 0) {
    return <EmptyText>No relevant roles were posted or first observed in the last 7 days.</EmptyText>;
  }

  return (
    <table className="w-full text-sm" style={{ color: T.text, borderCollapse: "collapse" }}>
      <thead>
        <tr style={{ borderBottom: `1px solid ${T.borderSoft}` }}>
          <Th>Company</Th>
          <Th hideOnMobile>Source</Th>
          <Th>Title</Th>
          <Th hideOnMobile>Location</Th>
          <Th>Date</Th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => {
          const url = String(row.url ?? "");
          const title = String(row.title ?? "").trim();
          return (
            <tr key={`${url}-${i}`} style={{ borderBottom: `1px solid ${T.borderFaint}`, verticalAlign: "top" }}>
              <td className="py-3 pr-4 whitespace-nowrap" style={{ color: T.muted }}>
                {String(row.company ?? "")}
              </td>
              <td className="py-3 pr-4 hidden sm:table-cell" style={{ color: T.faint }}>
                {String(row.source_kind ?? "")}
              </td>
              <td className="py-3 pr-4">
                {url ? (
                  <a
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: T.accent, textDecoration: "underline", fontWeight: 600 }}
                    onMouseEnter={(e) => (e.currentTarget.style.color = T.accentHover)}
                    onMouseLeave={(e) => (e.currentTarget.style.color = T.accent)}
                  >
                    {title}
                  </a>
                ) : (
                  <span>{title}</span>
                )}
                <div className="text-xs mt-1 sm:hidden" style={{ color: T.faint }}>
                  {String(row.source_kind ?? "")} - {String(row.location ?? "")}
                </div>
              </td>
              <td className="py-3 pr-4 hidden sm:table-cell" style={{ color: T.faint }}>
                {String(row.location ?? "")}
              </td>
              <td className="py-3 whitespace-nowrap" style={{ color: T.faint }}>
                {String(row.role_date ?? "")}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

function SkeletonRows({ count }: { count: number }) {
  return (
    <div className="animate-pulse space-y-2">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="h-5 rounded" style={{ background: T.borderFaint, width: `${92 - i * 9}%` }} />
      ))}
    </div>
  );
}

function EmptyText({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-sm" style={{ color: T.faint }}>
      {children}
    </p>
  );
}

function Th({
  children,
  hideOnMobile = false,
  align = "left",
}: {
  children: React.ReactNode;
  hideOnMobile?: boolean;
  align?: "left" | "right";
}) {
  const classes = hideOnMobile
    ? "text-left py-2 pr-4 font-medium text-xs hidden sm:table-cell"
    : "text-left py-2 pr-4 font-medium text-xs";

  return (
    <th
      className={classes}
      style={{
        color: T.faint,
        letterSpacing: "0.05em",
        textAlign: align,
        textTransform: "uppercase",
      }}
    >
      {children}
    </th>
  );
}

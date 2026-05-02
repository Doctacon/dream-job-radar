import { useSQLQuery } from "@motherduck/react-sql-query";

const N = (v: unknown): number => (v != null ? Number(v) : 0);

const TABLE = `"acorn-granary"."main"."current_open_roles"`;

export default function DreamJobRadar() {
  const summary = useSQLQuery(`
    SELECT
      count(*) AS total_roles,
      count(DISTINCT company) AS companies,
      count(DISTINCT location) AS locations,
      strftime(max(last_seen_at), '%Y-%m-%d %H:%M UTC') AS last_refresh
    FROM ${TABLE}
  `);

  const roles = useSQLQuery(`
    SELECT
      company,
      title,
      coalesce(location, '—') AS location,
      strftime(posted_at, '%Y-%m-%d') AS posted_at,
      url
    FROM ${TABLE}
    ORDER BY posted_at DESC NULLS LAST
  `);

  const summaryRow = (Array.isArray(summary.data) ? summary.data : [])[0] ?? {};
  const roleRows = Array.isArray(roles.data) ? roles.data : [];

  return (
    <div className="p-4 sm:p-6" style={{ background: "#f8f8f8", margin: "0 auto" }}>
      <h1 className="text-xl sm:text-2xl font-semibold" style={{ color: "#231f20" }}>
        dream-job-radar
      </h1>
      <p className="text-xs sm:text-sm mb-6" style={{ color: "#6a6a6a" }}>
        Open roles across hand-picked companies, filtered to data, engineering,
        GIS and geospatial titles.
        {summaryRow.last_refresh ? (
          <>
            {" "}
            Last refresh:{" "}
            <span style={{ color: "#231f20" }}>{String(summaryRow.last_refresh)}</span>.
          </>
        ) : null}
      </p>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-8 mb-8">
        <div>
          {summary.isLoading ? (
            <div className="h-10 w-20 bg-gray-200 animate-pulse rounded" />
          ) : (
            <p className="text-3xl sm:text-5xl font-bold" style={{ color: "#231f20" }}>
              {N(summaryRow.total_roles)}
            </p>
          )}
          <p className="text-xs sm:text-sm mt-1" style={{ color: "#6a6a6a" }}>
            Open roles
          </p>
        </div>
        <div>
          {summary.isLoading ? (
            <div className="h-10 w-20 bg-gray-200 animate-pulse rounded" />
          ) : (
            <p className="text-3xl sm:text-5xl font-bold" style={{ color: "#231f20" }}>
              {N(summaryRow.companies)}
            </p>
          )}
          <p className="text-xs sm:text-sm mt-1" style={{ color: "#6a6a6a" }}>
            Companies
          </p>
        </div>
        <div>
          {summary.isLoading ? (
            <div className="h-10 w-20 bg-gray-200 animate-pulse rounded" />
          ) : (
            <p className="text-3xl sm:text-5xl font-bold" style={{ color: "#231f20" }}>
              {N(summaryRow.locations)}
            </p>
          )}
          <p className="text-xs sm:text-sm mt-1" style={{ color: "#6a6a6a" }}>
            Locations
          </p>
        </div>
        <div>
          {summary.isLoading ? (
            <div className="h-10 w-20 bg-gray-200 animate-pulse rounded" />
          ) : (
            <p className="text-3xl sm:text-5xl font-bold" style={{ color: "#231f20" }}>
              {N(roleRows.length)}
            </p>
          )}
          <p className="text-xs sm:text-sm mt-1" style={{ color: "#6a6a6a" }}>
            Rows shown
          </p>
        </div>
      </div>

      <h2 className="text-base font-semibold mb-3" style={{ color: "#231f20" }}>
        Roles
      </h2>

      {roles.isLoading ? (
        <div className="animate-pulse space-y-2">
          <div className="h-5 bg-gray-200 rounded w-full" />
          <div className="h-5 bg-gray-200 rounded w-full" />
          <div className="h-5 bg-gray-200 rounded w-3/4" />
        </div>
      ) : (
        <table className="w-full text-sm" style={{ color: "#231f20" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #d8d8d8" }}>
              <th className="text-left py-2 pr-3 font-medium" style={{ color: "#6a6a6a" }}>
                Company
              </th>
              <th className="text-left py-2 pr-3 font-medium" style={{ color: "#6a6a6a" }}>
                Title
              </th>
              <th className="text-left py-2 pr-3 font-medium hidden sm:table-cell" style={{ color: "#6a6a6a" }}>
                Location
              </th>
              <th className="text-left py-2 font-medium" style={{ color: "#6a6a6a" }}>
                Posted
              </th>
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
                  style={{ color: "#0777b3", textDecoration: "underline" }}
                >
                  {title}
                </a>
              ) : (
                <span>{title}</span>
              );
              return (
                <tr key={i} style={{ borderBottom: "1px solid #ececec", verticalAlign: "top" }}>
                  <td className="py-2 pr-3 whitespace-nowrap">{String(r.company ?? "")}</td>
                  <td className="py-2 pr-3">
                    {titleEl}
                    <div className="text-xs mt-1 sm:hidden" style={{ color: "#6a6a6a" }}>
                      {String(r.location ?? "")}
                    </div>
                  </td>
                  <td className="py-2 pr-3 hidden sm:table-cell" style={{ color: "#6a6a6a" }}>
                    {String(r.location ?? "")}
                  </td>
                  <td className="py-2 whitespace-nowrap" style={{ color: "#6a6a6a" }}>
                    {String(r.posted_at ?? "")}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      <p className="text-xs mt-8" style={{ color: "#6a6a6a" }}>
        Source: dream-job-radar pipeline → Cloudflare R2 → MotherDuck view
        <code className="ml-1" style={{ color: "#231f20" }}>current_open_roles</code>.
      </p>
    </div>
  );
}

export async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body.detail;
    throw new Error(
      Array.isArray(detail)
        ? detail.map((e) => `${e.loc.at(-1)}: ${e.msg}`).join("; ")
        : detail || `Request failed (${response.status})`,
    );
  }
  return response.status === 204 ? null : response.json();
}

export function exportCSV(books) {
  const rows = [
    [
      "Title",
      "Author",
      "ISBN",
      "Category",
      "Shelf",
      "Total copies",
      "Available",
    ],
    ...books.map((b) => [
      b.title,
      b.author,
      b.isbn,
      b.category,
      b.shelf,
      b.total_copies,
      b.available_copies,
    ]),
  ];
  const csv = rows
    .map((row) =>
      row
        .map((value) => {
          const safe = String(value).replace(/^[=+@\-\t\r]/, "'$&");
          return `"${safe.replaceAll('"', '""')}"`;
        })
        .join(","),
    )
    .join("\r\n");
  const url = URL.createObjectURL(
    new Blob([csv], { type: "text/csv;charset=utf-8" }),
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = "folio-catalog.csv";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

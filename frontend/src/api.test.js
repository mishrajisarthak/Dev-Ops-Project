import { afterEach, test } from "node:test";
import assert from "node:assert/strict";
import { request, exportCSV } from "./api.js";

const originalFetch = globalThis.fetch;
afterEach(() => {
  globalThis.fetch = originalFetch;
});

test("API requests use the same-origin proxy and preserve method/body", async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, "/api/books");
    assert.equal(options.method, "POST");
    assert.equal(options.body, '{"title":"A book"}');
    assert.equal(options.headers["Content-Type"], "application/json");
    return new Response('{"id":1}', { status: 201 });
  };
  assert.deepEqual(
    await request("/books", { method: "POST", body: '{"title":"A book"}' }),
    { id: 1 },
  );
});

test("empty 204 responses do not attempt to parse JSON", async () => {
  globalThis.fetch = async () => new Response(null, { status: 204 });
  assert.equal(await request("/books/1", { method: "DELETE" }), null);
});

test("business errors reach the UI", async () => {
  globalThis.fetch = async () =>
    new Response('{"detail":"No copies available"}', { status: 409 });
  await assert.rejects(request("/loans"), /No copies available/);
});

test("validation errors include field and reason", async () => {
  globalThis.fetch = async () =>
    new Response(
      JSON.stringify({
        detail: [{ loc: ["body", "isbn"], msg: "Invalid ISBN" }],
      }),
      { status: 422 },
    );
  await assert.rejects(request("/books"), /isbn: Invalid ISBN/);
});

test("non-JSON server failures have a readable fallback", async () => {
  globalThis.fetch = async () => new Response("upstream down", { status: 502 });
  await assert.rejects(request("/stats"), /Request failed \(502\)/);
});

test("CSV export escapes quotes and neutralizes spreadsheet formulas", async () => {
  const originalCreate = URL.createObjectURL;
  const originalDocument = globalThis.document;
  let exported;
  URL.createObjectURL = (blob) => {
    exported = blob;
    return "blob:folio";
  };
  globalThis.document = {
    createElement: () => ({
      click() {},
      set download(value) {
        assert.equal(value, "folio-catalog.csv");
      },
    }),
  };
  try {
    exportCSV([
      {
        title: '=HYPERLINK("example")',
        author: "An Author",
        isbn: "1234567890",
        category: "Test",
        shelf: "A-01",
        total_copies: 1,
        available_copies: 1,
      },
    ]);
    const csv = await exported.text();
    assert.ok(csv.includes(`"'=HYPERLINK(""example"")"`));
    assert.ok(csv.startsWith('"Title","Author"'));
  } finally {
    URL.createObjectURL = originalCreate;
    globalThis.document = originalDocument;
  }
});

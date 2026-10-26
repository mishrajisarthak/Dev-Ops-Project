import React, { useCallback, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowDownToLine,
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  BookOpenCheck,
  BookMarked,
  ChartNoAxesCombined,
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CircleHelp,
  Clock3,
  Grid2X2,
  LayoutDashboard,
  List,
  LoaderCircle,
  Menu,
  Plus,
  Search,
  Settings2,
  Users,
  X,
} from "lucide-react";
import { exportCSV, request } from "./api";
import "./styles.css";

const NAV = [
  ["Overview", LayoutDashboard],
  ["Book catalog", BookOpen],
  ["Circulation", BookOpenCheck],
  ["Members", Users],
  ["Reports", ChartNoAxesCombined],
];
const CATEGORIES = [
  "Fiction",
  "Technology",
  "Science",
  "Personal growth",
  "Design",
  "History",
];
const dateLabel = (value) =>
  new Date(`${value.slice(0, 10)}T12:00:00`).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
const dueDefault = () => {
  const d = new Date();
  d.setDate(d.getDate() + 14);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};
const todayISO = () => new Date().toISOString().slice(0, 10);

function Cover({ book, small = false }) {
  return (
    <div
      className={`cover cover-${book.id % 6} ${small ? "cover-small" : ""}`}
      aria-hidden="true"
    >
      <div className="cover-rule" />
      <span>{book.author.split(" ").at(-1)}</span>
      <strong>{book.title}</strong>
      <i />
      <span className="cover-edition">FOLIO EDITION</span>
    </div>
  );
}

function Badge({ children, tone = "green" }) {
  return (
    <span className={`badge ${tone}`}>
      <span />
      {children}
    </span>
  );
}

function Modal({ title, subtitle, onClose, children }) {
  const ref = useRef(null);
  useEffect(() => {
    const previous = document.activeElement;
    const dialog = ref.current;
    dialog.showModal();
    return () => {
      dialog.close();
      previous?.focus();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === ref.current) onClose();
      }}
      aria-labelledby="modal-title"
    >
      <div className="modal-head">
        <div>
          <span className="eyebrow">FOLIO WORKSPACE</span>
          <h2 id="modal-title">{title}</h2>
          <p>{subtitle}</p>
        </div>
        <button
          className="icon-button"
          aria-label="Close dialog"
          onClick={onClose}
        >
          <X size={20} />
        </button>
      </div>
      {children}
    </dialog>
  );
}

function App() {
  const [page, setPage] = useState("Overview");
  const [data, setData] = useState({
    books: [],
    members: [],
    loans: [],
    stats: null,
  });
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [tab, setTab] = useState("All books");
  const [loanTab, setLoanTab] = useState("All loans");
  const [grid, setGrid] = useState(false);
  const [modal, setModal] = useState(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");
  const [toast, setToast] = useState("");
  const [mobileNav, setMobileNav] = useState(false);
  const [offset, setOffset] = useState(0);
  const refresh = useCallback(async () => {
    const [books, members, loans, stats] = await Promise.all([
      request("/books"),
      request("/members"),
      request("/loans"),
      request("/stats"),
    ]);
    setData({ books, members, loans, stats });
    setError("");
  }, []);
  useEffect(() => {
    refresh()
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [refresh]);
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 4000);
    return () => clearTimeout(timer);
  }, [toast]);
  useEffect(() => {
    setOffset(0);
  }, [query, category, tab, page]);
  const navigate = (value) => {
    setPage(value);
    setQuery("");
    setCategory("");
    setTab("All books");
    setMobileNav(false);
  };
  const open = (value) => {
    setModal(value);
    setFormError("");
  };
  const mutate = async (path, method, body, message) => {
    setBusy(true);
    setFormError("");
    try {
      await request(path, {
        method,
        ...(body ? { body: JSON.stringify(body) } : {}),
      });
      await refresh();
      setModal(null);
      setToast(message);
    } catch (e) {
      if (modal) setFormError(e.message);
      else setError(e.message);
    } finally {
      setBusy(false);
    }
  };
  const submitBook = (e) => {
    e.preventDefault();
    const values = Object.fromEntries(new FormData(e.currentTarget));
    values.total_copies = Number(values.total_copies);
    mutate(
      modal.book ? `/books/${modal.book.id}` : "/books",
      modal.book ? "PUT" : "POST",
      values,
      modal.book ? "Book updated" : "Book added to your catalog",
    );
  };
  const submitMember = (e) => {
    e.preventDefault();
    const values = Object.fromEntries(new FormData(e.currentTarget));
    if (modal.member) values.active = e.currentTarget.elements.active.checked;
    mutate(
      modal.member ? `/members/${modal.member.id}` : "/members",
      modal.member ? "PUT" : "POST",
      values,
      "Member saved",
    );
  };
  const submitLoan = (e) => {
    e.preventDefault();
    const values = Object.fromEntries(new FormData(e.currentTarget));
    values.book_id = Number(values.book_id);
    values.member_id = Number(values.member_id);
    mutate("/loans", "POST", values, "Book checked out successfully");
  };
  const { books, members, loans, stats } = data;
  const filtered = books.filter(
    (b) =>
      `${b.title} ${b.author} ${b.isbn}`
        .toLowerCase()
        .includes(query.toLowerCase()) &&
      (!category || b.category === category) &&
      (tab === "All books" ||
        (tab === "Available"
          ? b.available_copies > 0
          : b.available_copies < b.total_copies)),
  );
  const filteredMembers = members.filter((m) =>
    `${m.name} ${m.email}`.toLowerCase().includes(query.toLowerCase()),
  );
  const visibleLoans = loans.filter(
    (l) =>
      `${l.book_title} ${l.member_name}`
        .toLowerCase()
        .includes(query.toLowerCase()) &&
      (loanTab === "All loans" ||
        (loanTab === "On loan"
          ? l.status !== "returned"
          : l.status === loanTab.toLowerCase())),
  );
  const catalog = page === "Overview" || page === "Book catalog";
  const categoryOptions = [
    ...new Set([...CATEGORIES, ...books.map((b) => b.category)]),
  ].sort();
  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileNav ? "open" : ""}`}>
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            navigate("Overview");
          }}
        >
          <span className="brand-icon">
            <BookOpen size={25} />
          </span>
          folio<span className="brand-dot">.</span>
        </a>
        <div className="workspace">
          <span className="workspace-mark">C</span>
          <div>
            <strong>Central Library</strong>
            <span>Library workspace</span>
          </div>
          <ChevronDown size={15} />
        </div>
        <p className="nav-caption">WORKSPACE</p>
        <nav aria-label="Main navigation">
          {NAV.map(([name, Icon]) => (
            <button
              key={name}
              className={page === name ? "active" : ""}
              onClick={() => navigate(name)}
            >
              <Icon size={19} />
              {name}
              {name === "Circulation" && stats?.active_loans > 0 ? (
                <span className="nav-count">{stats.active_loans}</span>
              ) : null}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-note">
            <span className="note-symbol">✳</span>
            <h3>
              A little order.
              <br />A world of stories.
            </h3>
            <p>
              Your next great library day
              <br />
              starts right here.
            </p>
            <BookOpen size={57} strokeWidth={1} />
          </div>
          <button
            className="help-button"
            onClick={() => open({ type: "help" })}
          >
            <CircleHelp size={18} />
            Workspace guide
            <ArrowUpRight size={15} />
          </button>
          <div className="profile">
            <span className="avatar">LB</span>
            <div>
              <strong>Library team</strong>
              <span>Librarian workspace</span>
            </div>
            <span className="online-dot" />
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="icon-button mobile-menu"
              aria-label="Toggle navigation"
              onClick={() => setMobileNav(!mobileNav)}
            >
              <Menu size={20} />
            </button>
            <span>Workspace</span>
            <ChevronRight size={14} />
            <strong>{page}</strong>
          </div>
          <div className="topbar-right">
            <span className="live-status">
              <span />
              Library workspace
            </span>
            <span className="topbar-divider" />
            <span className="avatar small-avatar">LB</span>
          </div>
        </header>
        <main>
          <div className="page-heading">
            <div>
              <div className="eyebrow">YOUR LIBRARY, CONNECTED</div>
              <h1>
                {page === "Overview" ? "A good day for a great read." : page}
              </h1>
              <p>
                {page === "Overview"
                  ? "A little overview of the stories, people, and activity in your library."
                  : page === "Book catalog"
                    ? "Every book has a place. Keep your collection in good company."
                    : page === "Members"
                      ? "The people at the heart of your library."
                      : page === "Circulation"
                        ? "Keep every checkout, due date, and return in view."
                        : "A clearer picture of your collection and circulation."}
              </p>
            </div>
            <div className="heading-actions">
              {catalog ? (
                <>
                  <button
                    className="button secondary"
                    onClick={() => exportCSV(filtered)}
                  >
                    <ArrowDownToLine size={16} />
                    Export catalog
                  </button>
                  <button
                    className="button primary"
                    onClick={() => open({ type: "book" })}
                  >
                    <Plus size={18} />
                    Add book
                  </button>
                </>
              ) : page === "Members" ? (
                <button
                  className="button primary"
                  onClick={() => open({ type: "member" })}
                >
                  <Plus size={18} />
                  Add member
                </button>
              ) : (
                <button
                  className="button primary"
                  onClick={() => open({ type: "loan" })}
                >
                  <Plus size={18} />
                  Issue a book
                </button>
              )}
            </div>
          </div>
          {error ? (
            <div className="error-banner" role="alert">
              {error}
              <button
                onClick={() => refresh().catch((e) => setError(e.message))}
              >
                Retry connection
              </button>
            </div>
          ) : null}
          {loading ? (
            <div className="loading">
              <LoaderCircle className="spin" />
              Connecting to your library…
            </div>
          ) : (
            <>
              <section className="stats-grid" aria-label="Library statistics">
                {[
                  [
                    "Books in collection",
                    stats?.total_titles ?? 0,
                    BookMarked,
                    `${stats?.total_copies ?? 0} copies across your shelves`,
                    "mint",
                  ],
                  [
                    "Currently on loan",
                    stats?.active_loans ?? 0,
                    BookOpenCheck,
                    `${stats?.available_copies ?? 0} copies ready to borrow`,
                    "blue",
                  ],
                  [
                    "Active members",
                    stats?.active_members ?? 0,
                    Users,
                    "A community of curious minds",
                    "peach",
                  ],
                  [
                    "Overdue returns",
                    stats?.overdue_loans ?? 0,
                    Clock3,
                    "A friendly reminder goes a long way",
                    "yellow",
                  ],
                ].map(([label, number, Icon, note, color]) => (
                  <article className="stat-card" key={label}>
                    <div className="stat-top">
                      <span>{label}</span>
                      <span className={`stat-icon ${color}`}>
                        <Icon size={19} />
                      </span>
                    </div>
                    <strong className="stat-number">
                      {String(number).padStart(2, "0")}
                    </strong>
                    <p>
                      {label === "Overdue returns" && number > 0 ? (
                        <span className="attention-dot" />
                      ) : (
                        <span className="mini-line" />
                      )}
                      {note}
                    </p>
                  </article>
                ))}
              </section>
              {catalog ? (
                <div
                  className={
                    page === "Overview" ? "content-columns" : "catalog-only"
                  }
                >
                  <section className="panel catalog-panel">
                    <div className="panel-title">
                      <div>
                        <h2>
                          Your collection{" "}
                          <span className="count-pill">
                            {books.length} titles
                          </span>
                        </h2>
                        <p>A home for every book on your shelves.</p>
                      </div>
                      <button
                        className="text-link"
                        onClick={() => open({ type: "loan" })}
                      >
                        Issue a book <ArrowUpRight size={15} />
                      </button>
                    </div>
                    <div
                      className="catalog-tabs"
                      role="group"
                      aria-label="Book availability"
                    >
                      {["All books", "Available", "On loan"].map((t) => (
                        <button
                          key={t}
                          className={t === tab ? "selected" : ""}
                          onClick={() => setTab(t)}
                        >
                          {t}
                          {t === "All books" ? (
                            <span>{books.length}</span>
                          ) : null}
                        </button>
                      ))}
                    </div>
                    <div className="table-toolbar">
                      <label className="search-box">
                        <Search size={17} />
                        <input
                          aria-label="Search books"
                          placeholder="Search by title, author, or ISBN…"
                          value={query}
                          onChange={(e) => setQuery(e.target.value)}
                        />
                        {query ? (
                          <button
                            aria-label="Clear search"
                            onClick={() => setQuery("")}
                          >
                            <X size={14} />
                          </button>
                        ) : null}
                      </label>
                      <label className="category-select">
                        <Settings2 size={15} />
                        <select
                          aria-label="Filter by category"
                          value={category}
                          onChange={(e) => setCategory(e.target.value)}
                        >
                          <option value="">All categories</option>
                          {categoryOptions.map((c) => (
                            <option key={c}>{c}</option>
                          ))}
                        </select>
                      </label>
                      <div className="view-toggle">
                        <button
                          className={!grid ? "selected" : ""}
                          aria-label="List view"
                          onClick={() => setGrid(false)}
                        >
                          <List size={17} />
                        </button>
                        <button
                          className={grid ? "selected" : ""}
                          aria-label="Grid view"
                          onClick={() => setGrid(true)}
                        >
                          <Grid2X2 size={16} />
                        </button>
                      </div>
                    </div>
                    {filtered.length === 0 ? (
                      <div className="empty-state">
                        <BookOpen size={35} />
                        <h3>No books found</h3>
                        <p>
                          {books.length
                            ? "Try a different search or category."
                            : "Add your first book to start your collection."}
                        </p>
                      </div>
                    ) : grid ? (
                      <div className="book-grid">
                        {filtered.slice(offset, offset + 6).map((book) => (
                          <button
                            className="book-tile"
                            key={book.id}
                            onClick={() => open({ type: "detail", book })}
                          >
                            <Cover book={book} />
                            <h3>{book.title}</h3>
                            <p>{book.author}</p>
                            <Badge
                              tone={book.available_copies ? "green" : "orange"}
                            >
                              {book.available_copies ? "Available" : "On loan"}
                            </Badge>
                          </button>
                        ))}
                      </div>
                    ) : (
                      <div className="table-scroll">
                        <table className="books-table">
                          <thead>
                            <tr>
                              <th>BOOK DETAILS</th>
                              <th>CATEGORY</th>
                              <th>AVAILABILITY</th>
                              <th>SHELF</th>
                              <th aria-label="Actions" />
                            </tr>
                          </thead>
                          <tbody>
                            {filtered.slice(offset, offset + 6).map((book) => (
                              <tr key={book.id}>
                                <td>
                                  <button
                                    className="book-cell"
                                    onClick={() =>
                                      open({ type: "detail", book })
                                    }
                                  >
                                    <Cover book={book} small />
                                    <div>
                                      <strong>{book.title}</strong>
                                      <span>{book.author}</span>
                                    </div>
                                  </button>
                                </td>
                                <td>
                                  <span className="category-label">
                                    {book.category}
                                  </span>
                                </td>
                                <td>
                                  <Badge
                                    tone={
                                      book.available_copies ? "green" : "orange"
                                    }
                                  >
                                    {book.available_copies
                                      ? "Available"
                                      : "On loan"}
                                  </Badge>
                                  <span className="copies">
                                    {book.available_copies} of{" "}
                                    {book.total_copies} copies
                                  </span>
                                </td>
                                <td>
                                  <span className="shelf">{book.shelf}</span>
                                </td>
                                <td>
                                  <button
                                    className="icon-button"
                                    aria-label={`View ${book.title}`}
                                    onClick={() =>
                                      open({ type: "detail", book })
                                    }
                                  >
                                    <ArrowUpRight size={17} />
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                    <div className="table-footer">
                      <span>
                        Showing {filtered.length ? offset + 1 : 0}–
                        {Math.min(offset + 6, filtered.length)} of{" "}
                        {filtered.length} books
                      </span>
                      <div>
                        <button
                          className="icon-button"
                          aria-label="Previous page"
                          disabled={offset === 0}
                          onClick={() => setOffset(offset - 6)}
                        >
                          <ChevronLeft size={17} />
                        </button>
                        <span className="page-number">
                          {Math.floor(offset / 6) + 1}
                        </span>
                        <button
                          className="icon-button"
                          aria-label="Next page"
                          disabled={offset + 6 >= filtered.length}
                          onClick={() => setOffset(offset + 6)}
                        >
                          <ChevronRight size={17} />
                        </button>
                      </div>
                    </div>
                  </section>
                  {page === "Overview" ? (
                    <aside className="overview-aside">
                      <section className="welcome-card">
                        <div className="welcome-label">
                          <span />
                          THE READING ROOM
                        </div>
                        <h2>
                          Good books.
                          <br />
                          Great possibilities.
                        </h2>
                        <p>
                          Make room for the next chapter
                          <br />
                          in someone's story.
                        </p>
                        <div className="illustrated-books" aria-hidden="true">
                          <div>
                            THE
                            <br />
                            ART OF
                            <br />
                            <b>READING</b>
                          </div>
                          <div>
                            ONE MORE
                            <br />
                            <b>CHAPTER</b>
                            <span>✳</span>
                          </div>
                          <div>
                            STORIES
                            <br />
                            THAT
                            <br />
                            <b>STAY</b>
                          </div>
                        </div>
                        <button
                          onClick={() => {
                            navigate("Book catalog");
                            setGrid(true);
                          }}
                        >
                          Explore the collection <ArrowRight size={16} />
                        </button>
                      </section>
                      <section className="panel activity-panel">
                        <div className="panel-title">
                          <h2>Recent circulation</h2>
                          <span className="activity-dot" />
                        </div>
                        {loans.length ? (
                          loans.slice(0, 4).map((l) => (
                            <div className="activity" key={l.id}>
                              <span
                                className={`activity-icon ${l.status === "returned" ? "mint" : "peach"}`}
                              >
                                {l.status === "returned" ? (
                                  <Check size={15} />
                                ) : (
                                  <BookOpen size={15} />
                                )}
                              </span>
                              <div>
                                <p>
                                  <strong>{l.member_name.split(" ")[0]}</strong>{" "}
                                  {l.status === "returned"
                                    ? "returned"
                                    : "borrowed"}{" "}
                                  a book
                                </p>
                                <span>{l.book_title}</span>
                                <small>
                                  {dateLabel(l.returned_at || l.borrowed_at)}
                                </small>
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="muted activity-empty">
                            Your circulation activity will appear here.
                          </p>
                        )}
                        <button
                          className="activity-footer"
                          onClick={() => navigate("Circulation")}
                        >
                          View all circulation <ArrowRight size={14} />
                        </button>
                      </section>
                    </aside>
                  ) : null}
                </div>
              ) : null}
              {page === "Members" ? (
                <section className="panel">
                  <div className="panel-title">
                    <div>
                      <h2>
                        Your reading community{" "}
                        <span className="count-pill">
                          {members.length} members
                        </span>
                      </h2>
                      <p>Manage memberships and keep your community growing.</p>
                    </div>
                    <label className="search-box">
                      <Search size={17} />
                      <input
                        aria-label="Search members"
                        placeholder="Find a member…"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                      />
                    </label>
                  </div>
                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>MEMBER</th>
                          <th>EMAIL ADDRESS</th>
                          <th>JOINED</th>
                          <th>STATUS</th>
                          <th />
                        </tr>
                      </thead>
                      <tbody>
                        {filteredMembers.map((m) => (
                          <tr key={m.id}>
                            <td>
                              <div className="member-cell">
                                <span className={`avatar member-${m.id % 3}`}>
                                  {m.name
                                    .split(" ")
                                    .map((n) => n[0])
                                    .slice(0, 2)
                                    .join("")}
                                </span>
                                <div>
                                  <strong>{m.name}</strong>
                                  <span>
                                    MEM-{String(m.id).padStart(4, "0")}
                                  </span>
                                </div>
                              </div>
                            </td>
                            <td>{m.email}</td>
                            <td>{dateLabel(m.joined_at)}</td>
                            <td>
                              <Badge tone={m.active ? "green" : "gray"}>
                                {m.active ? "Active" : "Inactive"}
                              </Badge>
                            </td>
                            <td>
                              <button
                                className="text-link"
                                onClick={() =>
                                  open({ type: "member", member: m })
                                }
                              >
                                Edit member
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {!filteredMembers.length ? (
                    <div className="empty-state">
                      No members found. Add a member to begin.
                    </div>
                  ) : null}
                </section>
              ) : null}
              {page === "Circulation" ? (
                <section className="panel">
                  <div className="panel-title">
                    <div>
                      <h2>Books on their next chapter</h2>
                      <p>
                        Check books out, welcome them back, and track due dates.
                      </p>
                    </div>
                    <label className="search-box">
                      <Search size={17} />
                      <input
                        aria-label="Search loans"
                        placeholder="Search books or members…"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                      />
                    </label>
                  </div>
                  <div className="catalog-tabs">
                    {["All loans", "On loan", "Overdue", "Returned"].map(
                      (t) => (
                        <button
                          className={t === loanTab ? "selected" : ""}
                          key={t}
                          onClick={() => setLoanTab(t)}
                        >
                          {t}
                        </button>
                      ),
                    )}
                  </div>
                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>BOOK</th>
                          <th>MEMBER</th>
                          <th>CHECKED OUT</th>
                          <th>DUE DATE</th>
                          <th>STATUS</th>
                          <th />
                        </tr>
                      </thead>
                      <tbody>
                        {visibleLoans.map((l) => (
                          <tr key={l.id}>
                            <td>
                              <strong>{l.book_title}</strong>
                              <span className="copies">
                                LOAN-{String(l.id).padStart(4, "0")}
                              </span>
                            </td>
                            <td>{l.member_name}</td>
                            <td>{dateLabel(l.borrowed_at)}</td>
                            <td>{dateLabel(l.due_date)}</td>
                            <td>
                              <Badge
                                tone={
                                  l.status === "overdue"
                                    ? "red"
                                    : l.status === "returned"
                                      ? "gray"
                                      : "blue"
                                }
                              >
                                {l.status === "active"
                                  ? "On loan"
                                  : l.status[0].toUpperCase() +
                                    l.status.slice(1)}
                              </Badge>
                            </td>
                            <td>
                              {l.status !== "returned" ? (
                                <button
                                  className="button small-button secondary"
                                  disabled={busy}
                                  onClick={() =>
                                    open({ type: "return", loan: l })
                                  }
                                >
                                  Return book
                                </button>
                              ) : (
                                <span className="muted">
                                  {dateLabel(l.returned_at)}
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {!visibleLoans.length ? (
                    <div className="empty-state">
                      <BookOpenCheck size={34} />
                      <h3>No loans to show</h3>
                      <p>Issue a book to an active member to begin.</p>
                    </div>
                  ) : null}
                </section>
              ) : null}
              {page === "Reports" ? (
                <div className="reports-grid">
                  <section className="panel">
                    <div className="panel-title">
                      <div>
                        <h2>A collection of interests</h2>
                        <p>Titles by category, live from your catalog.</p>
                      </div>
                      <ChartNoAxesCombined size={21} />
                    </div>
                    <div className="category-chart">
                      {stats?.categories.length ? (
                        stats.categories.map((c, index) => (
                          <div className="chart-row" key={c.name}>
                            <span>{c.name}</span>
                            <div>
                              <i
                                style={{
                                  width: `${(c.count / Math.max(...stats.categories.map((x) => x.count))) * 100}%`,
                                  background: ["#407163", "#91b6a5", "#e3a68d"][
                                    index % 3
                                  ],
                                }}
                              />
                            </div>
                            <strong>{c.count}</strong>
                          </div>
                        ))
                      ) : (
                        <p>Add books to see your collection breakdown.</p>
                      )}
                    </div>
                  </section>
                  <section className="panel report-summary">
                    <span className="eyebrow">CIRCULATION SNAPSHOT</span>
                    <h2>Every copy accounted for.</h2>
                    <div
                      className="donut"
                      style={{
                        "--portion": `${stats?.total_copies ? (stats.available_copies / stats.total_copies) * 100 : 0}%`,
                      }}
                    >
                      <div>
                        <strong>{stats?.available_copies ?? 0}</strong>
                        <span>available copies</span>
                      </div>
                    </div>
                    <p>
                      <span className="legend-dot" />
                      Available <strong>{stats?.available_copies ?? 0}</strong>
                    </p>
                    <p>
                      <span className="legend-dot borrowed" />
                      On loan <strong>{stats?.active_loans ?? 0}</strong>
                    </p>
                    <p>
                      <Check size={15} />
                      Completed returns{" "}
                      <strong>{stats?.returned_loans ?? 0}</strong>
                    </p>
                  </section>
                </div>
              ) : null}
              <footer className="page-footer">
                <span>
                  <BookOpen size={13} />
                  Folio · A place for every story.
                </span>
                <span>Made for the people behind the books.</span>
              </footer>
            </>
          )}
        </main>
      </div>
      {toast ? (
        <div className="toast" role="status">
          <Check size={17} />
          {toast}
        </div>
      ) : null}
      {modal ? (
        <Modal
          title={
            modal.type === "book"
              ? modal.book
                ? "Edit book"
                : "A new story on the shelf."
              : modal.type === "member"
                ? modal.member
                  ? "Edit member"
                  : "Welcome a new reader."
                : modal.type === "loan"
                  ? "Start the next chapter."
                  : modal.type === "detail"
                    ? modal.book.title
                    : modal.type === "return"
                      ? "Welcome this book back."
                      : modal.type === "delete"
                        ? "Remove this book?"
                        : "Your library, at a glance."
          }
          subtitle={
            modal.type === "loan"
              ? "Choose a book, a reader, and a return date."
              : modal.type === "book"
                ? "Add the details that help readers find their next favorite."
                : modal.type === "member"
                  ? "A few details to keep your community connected."
                  : "Central Library · Folio workspace"
          }
          onClose={() => {
            if (!busy) setModal(null);
          }}
        >
          {formError ? (
            <div className="form-error" role="alert">
              {formError}
            </div>
          ) : null}
          {modal.type === "book" ? (
            <form onSubmit={submitBook}>
              <label>
                Book title
                <input
                  name="title"
                  required
                  minLength={2}
                  maxLength={160}
                  defaultValue={modal.book?.title}
                  placeholder="e.g. The Midnight Library"
                  autoFocus
                />
              </label>
              <label>
                Author
                <input
                  name="author"
                  required
                  minLength={2}
                  maxLength={120}
                  defaultValue={modal.book?.author}
                  placeholder="Author's full name"
                />
              </label>
              <div className="form-row">
                <label>
                  ISBN
                  <input
                    name="isbn"
                    required
                    pattern="([0-9]{10}|[0-9]{13})"
                    title="10 or 13 digits, without hyphens"
                    defaultValue={modal.book?.isbn}
                    placeholder="9780525559474"
                  />
                </label>
                <label>
                  Category
                  <select
                    aria-label="Category"
                    name="category"
                    defaultValue={modal.book?.category || "Fiction"}
                  >
                    {categoryOptions.map((c) => (
                      <option key={c}>{c}</option>
                    ))}
                  </select>
                </label>
              </div>
              <div className="form-row">
                <label>
                  Shelf location
                  <input
                    name="shelf"
                    required
                    maxLength={30}
                    defaultValue={modal.book?.shelf || "A-01"}
                  />
                </label>
                <label>
                  Total copies
                  <input
                    name="total_copies"
                    type="number"
                    min={1}
                    max={1000}
                    required
                    defaultValue={modal.book?.total_copies || 1}
                  />
                </label>
              </div>
              <label>
                Description
                <textarea
                  name="description"
                  maxLength={1000}
                  rows={3}
                  defaultValue={modal.book?.description}
                  placeholder="A little about this book…"
                />
              </label>
              <div className="modal-actions">
                <button
                  type="button"
                  className="button secondary"
                  disabled={busy}
                  onClick={() => setModal(null)}
                >
                  Cancel
                </button>
                <button className="button primary" disabled={busy}>
                  {busy
                    ? "Saving…"
                    : modal.book
                      ? "Save changes"
                      : "Add to collection"}
                  <Plus size={16} />
                </button>
              </div>
            </form>
          ) : null}
          {modal.type === "member" ? (
            <form onSubmit={submitMember}>
              <label>
                Full name
                <input
                  name="name"
                  required
                  minLength={2}
                  maxLength={120}
                  defaultValue={modal.member?.name}
                  autoFocus
                  placeholder="Reader's full name"
                />
              </label>
              <label>
                Email address
                <input
                  name="email"
                  type="email"
                  required
                  maxLength={180}
                  defaultValue={modal.member?.email}
                  placeholder="reader@example.com"
                />
              </label>
              {modal.member ? (
                <label className="checkbox-label">
                  <input
                    name="active"
                    type="checkbox"
                    defaultChecked={modal.member.active}
                  />
                  Active membership
                </label>
              ) : null}
              <div className="modal-actions">
                <button
                  type="button"
                  className="button secondary"
                  disabled={busy}
                  onClick={() => setModal(null)}
                >
                  Cancel
                </button>
                <button className="button primary" disabled={busy}>
                  {busy ? "Saving…" : "Save member"}
                  <Check size={16} />
                </button>
              </div>
            </form>
          ) : null}
          {modal.type === "loan" ? (
            <form onSubmit={submitLoan}>
              <label>
                Book
                <select
                  aria-label="Book"
                  name="book_id"
                  required
                  defaultValue={modal.book?.id || ""}
                >
                  <option value="" disabled>
                    Select an available book
                  </option>
                  {books
                    .filter((b) => b.available_copies > 0)
                    .map((b) => (
                      <option key={b.id} value={b.id}>
                        {b.title} ({b.available_copies} available)
                      </option>
                    ))}
                </select>
              </label>
              <label>
                Member
                <select
                  aria-label="Member"
                  name="member_id"
                  required
                  defaultValue=""
                >
                  <option value="" disabled>
                    Select an active member
                  </option>
                  {members
                    .filter((m) => m.active)
                    .map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.name} · {m.email}
                      </option>
                    ))}
                </select>
              </label>
              <label>
                Return due date
                <input
                  type="date"
                  name="due_date"
                  required
                  min={todayISO()}
                  defaultValue={dueDefault()}
                />
              </label>
              <div className="info-box">
                <BookOpen size={19} />
                <span>
                  Each checkout reserves one copy. Return the book to make it
                  available again.
                </span>
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="button secondary"
                  disabled={busy}
                  onClick={() => setModal(null)}
                >
                  Cancel
                </button>
                <button
                  className="button primary"
                  disabled={
                    busy ||
                    !members.some((m) => m.active) ||
                    !books.some((b) => b.available_copies > 0)
                  }
                >
                  {busy ? "Issuing…" : "Confirm checkout"}
                  <ArrowRight size={16} />
                </button>
              </div>
            </form>
          ) : null}
          {modal.type === "detail" ? (
            <>
              <div className="book-detail">
                <Cover book={modal.book} />
                <div>
                  <Badge
                    tone={modal.book.available_copies ? "green" : "orange"}
                  >
                    {modal.book.available_copies ? "Available" : "On loan"}
                  </Badge>
                  <h3>{modal.book.author}</h3>
                  <p>{modal.book.description || "No description added yet."}</p>
                  <dl>
                    <dt>ISBN</dt>
                    <dd>{modal.book.isbn}</dd>
                    <dt>Category</dt>
                    <dd>{modal.book.category}</dd>
                    <dt>Shelf</dt>
                    <dd>{modal.book.shelf}</dd>
                    <dt>Copies</dt>
                    <dd>
                      {modal.book.available_copies} available /{" "}
                      {modal.book.total_copies} total
                    </dd>
                  </dl>
                </div>
              </div>
              <div className="modal-actions detail-actions">
                <button
                  className="text-link danger"
                  onClick={() => open({ type: "delete", book: modal.book })}
                >
                  Remove book
                </button>
                <button
                  className="button secondary"
                  onClick={() => open({ type: "book", book: modal.book })}
                >
                  Edit book
                </button>
                <button
                  className="button primary"
                  disabled={!modal.book.available_copies}
                  onClick={() => open({ type: "loan", book: modal.book })}
                >
                  Issue book
                  <ArrowRight size={15} />
                </button>
              </div>
            </>
          ) : null}
          {modal.type === "return" || modal.type === "delete" ? (
            <>
              <p className="confirm-copy">
                {modal.type === "return"
                  ? `Confirm the return of “${modal.loan.book_title}” from ${modal.loan.member_name}. One copy will become available.`
                  : `Remove “${modal.book.title}” from your catalog? Books with loan history are retained for your records.`}
              </p>
              <div className="modal-actions">
                <button
                  className="button secondary"
                  disabled={busy}
                  onClick={() => setModal(null)}
                >
                  Cancel
                </button>
                <button
                  className="button primary"
                  disabled={busy}
                  onClick={() =>
                    modal.type === "return"
                      ? mutate(
                          `/loans/${modal.loan.id}/return`,
                          "POST",
                          null,
                          "Book returned to the shelves",
                        )
                      : mutate(
                          `/books/${modal.book.id}`,
                          "DELETE",
                          null,
                          "Book removed",
                        )
                  }
                >
                  {busy
                    ? "Saving…"
                    : modal.type === "return"
                      ? "Confirm return"
                      : "Remove book"}
                </button>
              </div>
            </>
          ) : null}
          {modal.type === "help" ? (
            <div className="help-content">
              <p>
                <strong>1. Build your collection.</strong> Add titles, ISBNs,
                categories, and the number of copies you own.
              </p>
              <p>
                <strong>2. Welcome your readers.</strong> Register members and
                manage their membership status.
              </p>
              <p>
                <strong>3. Keep stories moving.</strong> Issue an available book
                to a member, choose a due date, and confirm its return in
                Circulation.
              </p>
              <p>
                <strong>4. Find the bigger picture.</strong> Use Reports for
                live stock and category totals, or export the catalog as CSV.
              </p>
            </div>
          ) : null}
        </Modal>
      ) : null}
    </div>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

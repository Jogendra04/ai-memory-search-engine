function Sidebar({
  activePage,
  setActivePage,
  onLogout,
}) {
  const handleLogout = () => {
    localStorage.removeItem("access_token");
    onLogout();
  };

  return (
    <aside className="sidebar">

      {/* Logo */}
      <div className="sidebar-logo">
        <div className="logo-icon">🧠</div>

        <div>
          <h2>AI Memory</h2>
          <span>Search Engine</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">

        <button
          className={
            activePage === "chat"
              ? "nav-item active"
              : "nav-item"
          }
          onClick={() => setActivePage("chat")}
        >
          <span className="nav-icon">💬</span>
          <span>Chat</span>
        </button>

        <button
          className={
            activePage === "documents"
              ? "nav-item active"
              : "nav-item"
          }
          onClick={() =>
            setActivePage("documents")
          }
        >
          <span className="nav-icon">📄</span>
          <span>Documents</span>
        </button>

        <button
          className={
            activePage === "memories"
              ? "nav-item active"
              : "nav-item"
          }
          onClick={() =>
            setActivePage("memories")
          }
        >
          <span className="nav-icon">🧠</span>
          <span>Memories</span>
        </button>

      </nav>

      {/* Bottom */}
      <div className="sidebar-bottom">

        <div className="sidebar-user">

          <div className="user-avatar">
            👤
          </div>

          <div className="user-info">
            <strong>User</strong>
            <span>Personal workspace</span>
          </div>

        </div>

        <button
          className="logout-button"
          onClick={handleLogout}
        >
          <span>🚪</span>
          <span>Logout</span>
        </button>

      </div>

    </aside>
  );
}

export default Sidebar;
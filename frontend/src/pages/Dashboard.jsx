import { useState } from "react";

import Chat from "../components/Chat/Chat";
import DocumentUpload from "../components/Documents/DocumentUpload";
import DocumentList from "../components/Documents/DocumentList";
import MemoryForm from "../components/Memories/MemoryForm";
import MemoryList from "../components/Memories/MemoryList";


// ==========================================
// Get Logged-in User
// ==========================================

function getLoggedInUser() {

  const name =
    localStorage.getItem("user_name") ||
    "User";

  const email =
    localStorage.getItem("user_email") ||
    "Personal AI";

  return {
    name,
    email,
  };
}


// ==========================================
// Dashboard
// ==========================================

function Dashboard() {

  const [activePage, setActivePage] =
    useState("chat");

  const [documentRefresh, setDocumentRefresh] =
    useState(0);

  const [memoryRefresh, setMemoryRefresh] =
    useState(0);

  const [user] = useState(
    getLoggedInUser()
  );


  // ==========================================
  // Logout
  // ==========================================

  const handleLogout = () => {

    const confirmed = window.confirm(
      "Are you sure you want to logout?"
    );

    if (!confirmed) {
      return;
    }

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user_name"
    );

    localStorage.removeItem(
      "user_email"
    );

    window.location.href = "/login";
  };


  // ==========================================
  // Page Title
  // ==========================================

  const getPageTitle = () => {

    if (activePage === "chat") {
      return "Chat";
    }

    if (activePage === "documents") {
      return "Documents";
    }

    if (activePage === "memories") {
      return "Memories";
    }

    return "Dashboard";
  };


  // ==========================================
  // Render Main Content
  // ==========================================

  const renderContent = () => {

    // ----------------------------------------
    // Chat
    // ----------------------------------------

    if (activePage === "chat") {
      return <Chat />;
    }


    // ----------------------------------------
    // Documents
    // ----------------------------------------

    if (activePage === "documents") {

      return (
        <div className="page-content">

          <div className="page-heading">

            <div>

              <h2>
                Documents
              </h2>

              <p>
                Upload and manage your documents.
              </p>

            </div>

          </div>


          <div className="documents-grid">

            <DocumentUpload
              onUploadSuccess={() =>
                setDocumentRefresh(
                  (value) => value + 1
                )
              }
            />

            <DocumentList
              refresh={documentRefresh}
            />

          </div>

        </div>
      );
    }


    // ----------------------------------------
    // Memories
    // ----------------------------------------

    if (activePage === "memories") {

      return (
        <div className="page-content">

          <div className="page-heading">

            <div>

              <h2>
                Memories
              </h2>

              <p>
                Save information you want your AI
                to remember.
              </p>

            </div>

          </div>


          <div className="memories-grid">

            <MemoryForm
              onMemorySaved={() =>
                setMemoryRefresh(
                  (value) => value + 1
                )
              }
            />

            <MemoryList
              refresh={memoryRefresh}
            />

          </div>

        </div>
      );
    }


    return null;
  };


  // ==========================================
  // UI
  // ==========================================

  return (

    <div className="dashboard">


      {/* ======================================
          SIDEBAR
      ====================================== */}

      <aside className="sidebar">


        {/* Logo */}

        <div className="sidebar-brand">

          <div className="brand-icon">
            🧠
          </div>

          <div>

            <h1>
              AI Memory
            </h1>

            <span>
              Search Engine
            </span>

          </div>

        </div>


        {/* Navigation */}

        <nav className="sidebar-navigation">


          {/* Chat */}

          <button
            className={
              activePage === "chat"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("chat")
            }
          >

            <span className="nav-icon">
              💬
            </span>

            <span>
              Chat
            </span>

          </button>


          {/* Documents */}

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

            <span className="nav-icon">
              📄
            </span>

            <span>
              Documents
            </span>

          </button>


          {/* Memories */}

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

            <span className="nav-icon">
              🧠
            </span>

            <span>
              Memories
            </span>

          </button>

        </nav>


        {/* ======================================
            Sidebar Bottom
        ====================================== */}

        <div className="sidebar-bottom">


          {/* User Profile */}

          <div className="user-info">

            <div className="user-avatar">
              👤
            </div>

            <div className="user-details">

              <strong>
                {user.name}
              </strong>

              <span>
                {user.email}
              </span>

            </div>

          </div>


          {/* Logout */}

          <button
            className="logout-button"
            onClick={handleLogout}
          >

            <span>
              ↪
            </span>

            <span>
              Logout
            </span>

          </button>

        </div>

      </aside>


      {/* ======================================
          MAIN AREA
      ====================================== */}

      <main className="dashboard-main">


        {/* Top Header */}

        <header className="dashboard-header">

          <div>

            <h2>
              {getPageTitle()}
            </h2>

            <p>
              Your personal AI workspace
            </p>

          </div>

        </header>


        {/* Page */}

        <section className="dashboard-content">

          {renderContent()}

        </section>

      </main>

    </div>
  );
}


export default Dashboard;
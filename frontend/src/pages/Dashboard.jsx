import { useState } from "react";
import "../App.css";

import Chat from "../components/Chat/Chat";
import DocumentUpload from "../components/Documents/DocumentUpload";
import DocumentList from "../components/Documents/DocumentList";
import MemoryForm from "../components/Memories/MemoryForm";
import MemoryList from "../components/Memories/MemoryList";

function Dashboard() {
  const [documentRefresh, setDocumentRefresh] = useState(0);
  const [memoryRefresh, setMemoryRefresh] = useState(0);

  return (
    <div className="app">
      <h1>AI Memory Search Engine</h1>

      <div className="main-layout">
        <Chat />

        <div className="memory-section">
          <DocumentUpload
            onUploadSuccess={() =>
              setDocumentRefresh((value) => value + 1)
            }
          />

          <DocumentList
            refresh={documentRefresh}
          />

          <MemoryForm
            onMemorySaved={() =>
              setMemoryRefresh((value) => value + 1)
            }
          />

          <MemoryList
            refresh={memoryRefresh}
          />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
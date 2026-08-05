import { useEffect, useState } from "react";
import {
  getDocuments,
  deleteDocument,
} from "../../services/api";

function DocumentList({ refresh }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadDocuments = async () => {
    try {
      const data = await getDocuments();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error(error);
      alert(error.message || "Failed to load documents.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);

    const fetchDocuments = async () => {
      await loadDocuments();
    };

    fetchDocuments();
  }, [refresh]);

  const handleDelete = async (filename) => {
    if (!window.confirm(`Delete "${filename}"?`)) {
      return;
    }

    try {
      setLoading(true);

      await deleteDocument(filename);

      await loadDocuments();

      alert("Document deleted successfully.");
    } catch (error) {
      console.error(error);
      alert(error.message || "Failed to delete document.");
    }
  };

  return (
    <div className="document-list">
      <h2>Uploaded Documents</h2>

      {loading ? (
        <p>Loading documents...</p>
      ) : documents.length === 0 ? (
        <p>No documents uploaded.</p>
      ) : (
        documents.map((document) => (
          <div
            key={document.filename}
            className="memory-card"
          >
            <div className="memory-header">
              <div>
                <h3>{document.filename}</h3>
                <p>
                  {document.chunks}{" "}
                  {document.chunks === 1 ? "chunk" : "chunks"}
                </p>
              </div>

              <button
                className="delete-button"
                onClick={() => handleDelete(document.filename)}
              >
                Delete
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default DocumentList;
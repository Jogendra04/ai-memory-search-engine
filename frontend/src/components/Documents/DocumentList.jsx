import { useEffect, useState } from "react";

import {
  getDocuments,
  deleteDocument,
} from "../../services/api";

function DocumentList({ refresh }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [deletingFilename, setDeletingFilename] =
    useState(null);

  const loadDocuments = async () => {
    try {
      setLoading(true);

      const data = await getDocuments();

      setDocuments(
        data.documents || []
      );
    } catch (error) {
      console.error(error);

      alert(
        error.message ||
          "Failed to load documents."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [refresh]);

  const handleDelete = async (filename) => {
    const confirmed = window.confirm(
      `Delete "${filename}"?\n\nThis will remove the document and its stored chunks.`
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingFilename(filename);

      await deleteDocument(filename);

      setDocuments((prev) =>
        prev.filter(
          (document) =>
            document.filename !== filename
        )
      );
    } catch (error) {
      console.error(error);

      alert(
        error.message ||
          "Failed to delete document."
      );
    } finally {
      setDeletingFilename(null);
    }
  };

  return (
    <div className="document-list">

      {/* Header */}

      <div className="list-header">

        <div>
          <h3>Your Documents</h3>

          <p>
            {documents.length}{" "}
            {documents.length === 1
              ? "document"
              : "documents"}
          </p>
        </div>

      </div>


      {/* Loading */}

      {loading && (
        <div className="documents-loading">
          Loading documents...
        </div>
      )}


      {/* Empty state */}

      {!loading &&
        documents.length === 0 && (
          <div className="documents-empty">

            <div className="empty-icon">
              📄
            </div>

            <h4>
              No documents yet
            </h4>

            <p>
              Upload a document above to
              start building your AI
              knowledge base.
            </p>

          </div>
        )}


      {/* Documents */}

      {!loading &&
        documents.length > 0 && (
          <div className="documents">

            {documents.map(
              (document) => {

                const isDeleting =
                  deletingFilename ===
                  document.filename;

                return (
                  <div
                    key={
                      document.filename
                    }
                    className="document-card"
                  >

                    <div className="document-icon">
                      📄
                    </div>


                    <div className="document-info">

                      <h4>
                        {document.filename}
                      </h4>

                      <p>
                        {document.chunks}{" "}
                        {document.chunks ===
                        1
                          ? "chunk"
                          : "chunks"}
                      </p>

                    </div>


                    <button
                      className="document-delete-button"
                      onClick={() =>
                        handleDelete(
                          document.filename
                        )
                      }
                      disabled={
                        isDeleting
                      }
                    >
                      {isDeleting
                        ? "Deleting..."
                        : "Delete"}
                    </button>

                  </div>
                );
              }
            )}

          </div>
        )}

    </div>
  );
}

export default DocumentList;
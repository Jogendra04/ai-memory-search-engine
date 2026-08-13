import { useEffect, useState } from "react";

import {
  getMemories,
  deleteMemory,
  updateMemory,
} from "../../services/api";

function MemoryList({ refresh }) {
  const [memories, setMemories] = useState([]);

  const [loading, setLoading] = useState(false);

  const [editingId, setEditingId] =
    useState(null);

  const [editTitle, setEditTitle] =
    useState("");

  const [editContent, setEditContent] =
    useState("");

  const [editTags, setEditTags] =
    useState("");

  const [error, setError] =
    useState("");

  const [savingId, setSavingId] =
    useState(null);

  const [deletingId, setDeletingId] =
    useState(null);

  // ==========================================
  // Load Memories
  // ==========================================

  const loadMemories = async () => {
    try {
      setLoading(true);
      setError("");

      const data =
        await getMemories();

      setMemories(
        data.memories || []
      );
    } catch (error) {
      console.error(
        "Failed to load memories:",
        error
      );

      setError(
        error.message ||
          "Failed to load memories."
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // Load on Mount / Refresh
  // ==========================================

  useEffect(() => {
    loadMemories();
  }, [refresh]);

  // ==========================================
  // Start Editing
  // ==========================================

  const handleEdit = (memory) => {
    setError("");

    setEditingId(memory.id);

    setEditTitle(
      memory.title || ""
    );

    setEditContent(
      memory.content || ""
    );

    setEditTags(
      (memory.tags || []).join(", ")
    );
  };

  // ==========================================
  // Cancel Editing
  // ==========================================

  const handleCancelEdit = () => {
    setEditingId(null);

    setEditTitle("");
    setEditContent("");
    setEditTags("");
  };

  // ==========================================
  // Save Updated Memory
  // ==========================================

  const handleUpdate = async () => {
    setError("");

    if (!editTitle.trim()) {
      setError(
        "Please enter a memory title."
      );
      return;
    }

    if (!editContent.trim()) {
      setError(
        "Please enter memory content."
      );
      return;
    }

    const tagList = editTags
      .split(",")
      .map((tag) => tag.trim())
      .filter((tag) => tag.length > 0);

    try {
      setSavingId(editingId);

      await updateMemory(
        editingId,
        {
          title: editTitle.trim(),
          content: editContent.trim(),
          tags: tagList,
        }
      );

      setMemories((previous) =>
        previous.map((memory) =>
          memory.id === editingId
            ? {
                ...memory,
                title: editTitle.trim(),
                content:
                  editContent.trim(),
                tags: tagList,
              }
            : memory
        )
      );

      handleCancelEdit();
    } catch (error) {
      console.error(
        "Failed to update memory:",
        error
      );

      setError(
        error.message ||
          "Failed to update memory."
      );
    } finally {
      setSavingId(null);
    }
  };

  // ==========================================
  // Delete Memory
  // ==========================================

  const handleDelete = async (id) => {
    const confirmed =
      window.confirm(
        "Are you sure you want to delete this memory?"
      );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(id);
      setError("");

      await deleteMemory(id);

      setMemories((previous) =>
        previous.filter(
          (memory) =>
            memory.id !== id
        )
      );

    } catch (error) {
      console.error(
        "Failed to delete memory:",
        error
      );

      setError(
        error.message ||
          "Failed to delete memory."
      );
    } finally {
      setDeletingId(null);
    }
  };

  // ==========================================
  // Loading
  // ==========================================

  if (loading) {
    return (
      <div className="memory-list">

        <div className="list-header">
          <div>
            <h2>Saved Memories</h2>
          </div>
        </div>

        <div className="memory-loading">
          <span className="loading-spinner"></span>

          <span>
            Loading memories...
          </span>
        </div>

      </div>
    );
  }

  // ==========================================
  // UI
  // ==========================================

  return (
    <div className="memory-list">

      {/* ======================================
          Header
      ====================================== */}

      <div className="list-header">

        <div>
          <h2>
            Saved Memories
          </h2>

          <p>
            {memories.length}{" "}
            {memories.length === 1
              ? "memory"
              : "memories"}
          </p>
        </div>

      </div>

      {/* ======================================
          Error
      ====================================== */}

      {error && (
        <div className="form-error">
          {error}
        </div>
      )}

      {/* ======================================
          Empty State
      ====================================== */}

      {memories.length === 0 && (
        <div className="memory-empty">

          <div className="empty-icon">
            🧠
          </div>

          <h3>
            No memories yet
          </h3>

          <p>
            Save important information above
            so your AI can remember it.
          </p>

        </div>
      )}

      {/* ======================================
          Memory Cards
      ====================================== */}

      {memories.length > 0 && (
        <div className="memory-items">

          {memories.map((memory) => {

            const isEditing =
              editingId === memory.id;

            const isSaving =
              savingId === memory.id;

            const isDeleting =
              deletingId === memory.id;

            return (
              <div
                key={memory.id}
                className="memory-card"
              >

                {isEditing ? (

                  /* ==========================
                     EDIT MODE
                  ========================== */

                  <div className="memory-edit">

                    <h3>
                      Edit Memory
                    </h3>

                    <label>
                      Title
                    </label>

                    <input
                      type="text"
                      value={editTitle}
                      onChange={(event) =>
                        setEditTitle(
                          event.target.value
                        )
                      }
                      disabled={isSaving}
                    />

                    <label>
                      Content
                    </label>

                    <textarea
                      rows={5}
                      value={editContent}
                      onChange={(event) =>
                        setEditContent(
                          event.target.value
                        )
                      }
                      disabled={isSaving}
                    />

                    <label>
                      Tags
                    </label>

                    <input
                      type="text"
                      value={editTags}
                      onChange={(event) =>
                        setEditTags(
                          event.target.value
                        )
                      }
                      placeholder="ai, python, project"
                      disabled={isSaving}
                    />

                    <div className="edit-actions">

                      <button
                        className="save-edit-button"
                        onClick={
                          handleUpdate
                        }
                        disabled={isSaving}
                      >
                        {isSaving
                          ? "Saving..."
                          : "Save Changes"}
                      </button>

                      <button
                        className="cancel-edit-button"
                        onClick={
                          handleCancelEdit
                        }
                        disabled={isSaving}
                      >
                        Cancel
                      </button>

                    </div>

                  </div>

                ) : (

                  /* ==========================
                     VIEW MODE
                  ========================== */

                  <div>

                    <div className="memory-header">

                      <div className="memory-title-area">

                        <h3>
                          {memory.title}
                        </h3>

                      </div>

                      <div className="memory-actions">

                        <button
                          className="edit-button"
                          onClick={() =>
                            handleEdit(
                              memory
                            )
                          }
                          disabled={
                            deletingId !== null
                          }
                        >
                          Edit
                        </button>

                        <button
                          className="delete-button"
                          onClick={() =>
                            handleDelete(
                              memory.id
                            )
                          }
                          disabled={
                            deletingId !== null
                          }
                        >
                          {isDeleting
                            ? "Deleting..."
                            : "Delete"}
                        </button>

                      </div>

                    </div>

                    <p className="memory-content">
                      {memory.content}
                    </p>

                    {memory.tags?.length >
                      0 && (
                      <div className="tags">

                        {memory.tags.map(
                          (
                            tag,
                            index
                          ) => (
                            <span
                              key={index}
                              className="tag"
                            >
                              #{tag}
                            </span>
                          )
                        )}

                      </div>
                    )}

                  </div>
                )}

              </div>
            );
          })}

        </div>
      )}

    </div>
  );
}

export default MemoryList;
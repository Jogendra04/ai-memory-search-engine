import { useState } from "react";
import { uploadDocument } from "../../services/api";

function DocumentUpload({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [dragActive, setDragActive] = useState(false);

  const allowedExtensions = [
    ".pdf",
    ".txt",
    ".docx",
    ".csv",
    ".md",
  ];

  const validateFile = (file) => {
    if (!file) {
      return false;
    }

    const filename = file.name.toLowerCase();

    return allowedExtensions.some((extension) =>
      filename.endsWith(extension)
    );
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    setUploadMessage("");

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (!validateFile(file)) {
      setUploadMessage(
        "Please select a PDF, TXT, DOCX, CSV, or MD file."
      );

      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();

    setDragActive(false);
    setUploadMessage("");

    const file = event.dataTransfer.files[0];

    if (!file) {
      return;
    }

    if (!validateFile(file)) {
      setUploadMessage(
        "Please select a PDF, TXT, DOCX, CSV, or MD file."
      );

      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage(
        "Please select a document first."
      );
      return;
    }

    setUploadLoading(true);
    setUploadMessage("");

    try {
      const data = await uploadDocument(
        selectedFile
      );

      setUploadMessage(
        data.message ||
          "Document uploaded successfully!"
      );

      setSelectedFile(null);

      const input =
        document.getElementById(
          "document-upload"
        );

      if (input) {
        input.value = "";
      }

      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (error) {
      console.error(error);

      setUploadMessage(
        error.message ||
          "Upload failed."
      );
    } finally {
      setUploadLoading(false);
    }
  };

  return (
    <div className="upload-section">

      {/* Header */}

      <div className="section-title-row">

        <div>
          <h2>Documents</h2>

          <p className="section-description">
            Upload documents to your AI knowledge base.
          </p>
        </div>

      </div>


      {/* Upload Area */}

      <label
        htmlFor="document-upload"
        className={`upload-dropzone ${
          dragActive
            ? "drag-active"
            : ""
        }`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => {
          setDragActive(false);
        }}
        onDrop={handleDrop}
      >

        <div className="upload-icon">
          ↑
        </div>

        <div className="upload-title">
          Drop your document here
        </div>

        <div className="upload-subtitle">
          or click to browse files
        </div>

        <div className="upload-formats">
          PDF · TXT · DOCX · CSV · MD
        </div>

        <input
          id="document-upload"
          type="file"
          accept=".pdf,.txt,.docx,.csv,.md"
          onChange={handleFileChange}
          hidden
        />

      </label>


      {/* Selected file */}

      {selectedFile && (
        <div className="selected-file-card">

          <div className="file-icon">
            📄
          </div>

          <div className="selected-file-info">

            <div className="selected-file-name">
              {selectedFile.name}
            </div>

            <div className="selected-file-size">
              {(
                selectedFile.size /
                1024 /
                1024
              ).toFixed(2)}{" "}
              MB
            </div>

          </div>

        </div>
      )}


      {/* Upload button */}

      <button
        className="upload-button"
        onClick={handleUpload}
        disabled={
          uploadLoading ||
          !selectedFile
        }
      >
        {uploadLoading
          ? "Processing document..."
          : "Upload Document"}
      </button>


      {/* Message */}

      {uploadMessage && (
        <div className="upload-message">
          {uploadMessage}
        </div>
      )}

    </div>
  );
}

export default DocumentUpload;
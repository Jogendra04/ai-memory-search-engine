
import { useState } from "react";
import { uploadDocument } from "../../services/api";

function DocumentUpload({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    setUploadMessage("");

    if (!file) {
      setSelectedFile(null);
      return;
    }

    const allowedExtensions = [
      ".pdf",
      ".txt",
      ".docx",
      ".csv",
      ".md",
    ];

    const filename = file.name.toLowerCase();

    const isAllowed = allowedExtensions.some(
      (extension) => filename.endsWith(extension)
    );

    if (!isAllowed) {
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
        "Please select a PDF, TXT, DOCX, CSV, or MD file."
      );
      return;
    }

    setUploadLoading(true);

    try {
      const data = await uploadDocument(selectedFile);

      setUploadMessage(
        data.message || "Document uploaded successfully!"
      );

      setSelectedFile(null);

      const input = document.getElementById(
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
        error.message || "Upload failed."
      );

    } finally {
      setUploadLoading(false);
    }
  };

  return (
    <div>
      <h2>Documents</h2>

      <input
        id="document-upload"
        type="file"
        accept=".pdf,.txt,.docx,.csv,.md"
        onChange={handleFileChange}
      />

      <p>
        Supported files: PDF, TXT, DOCX, CSV, MD
      </p>

      {selectedFile && (
        <p>
          Selected: {selectedFile.name}
        </p>
      )}

      <button
        onClick={handleUpload}
        disabled={uploadLoading}
      >
        {uploadLoading
          ? "Processing..."
          : "Upload Document"}
      </button>

      {uploadMessage && (
        <p>{uploadMessage}</p>
      )}
    </div>
  );
}

export default DocumentUpload;
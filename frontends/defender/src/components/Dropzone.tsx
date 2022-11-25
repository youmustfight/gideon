import React from "React";
import { useDropzone } from "react-dropzone";

export const Dropzone = ({ open }) => {
  const { getRootProps, getInputProps, acceptedFiles } = useDropzone({});

  const files = acceptedFiles.map((file) => (
    <li key={file.path}>
      {file.path} - {file.size} bytes
    </li>
  ));

  return (
    <div className="container">
      <div {...getRootProps({ className: "dropzone" })}>
        <input {...getInputProps()} />
        <p>Drag 'n' drop some files here</p>
      </div>
      <aside>
        <ul>{files}</ul>
      </aside>
    </div>
  );

}

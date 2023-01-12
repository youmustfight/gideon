import axios from "axios";
import { getGideonApiUrl } from "../env";

export const reqIndexDocument = (
  files: any[],
  { caseId, organizationId, userId }: { caseId: number; organizationId: number; userId: number }
) => {
  // VALIDATE
  // --- exists (TODO: multiple files?)
  const file = files[0];
  if (!files || !files?.[0]) {
    alert("File upload missing.");
    return;
  }
  // --- size (2MB for now)
  if (file.size > 1000 * 1000 * 10) {
    alert("Please upload a file less than 10MB");
    return;
  }

  // --- get index document type from mime_type
  const mimeType = file.type;
  let type;
  if (mimeType.includes("audio")) {
    type = "audio";
  } else if (mimeType.includes("/vnd.openxmlformats-officedocument.wordprocessingml.document")) {
    type = "docx";
  } else if (mimeType.includes("image")) {
    type = "image";
  } else if (mimeType.includes("/pdf")) {
    type = "pdf";
  } else if (mimeType.includes("video")) {
    type = "video";
  } else {
    throw new Error(`Unhandled document type: ${mimeType}`);
  }

  // --- setup form data/submit
  const formData = new FormData();
  formData.append("file", file);

  // --- submit
  return axios
    .post(`${getGideonApiUrl()}/v1/index/document/${type}`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
      params: { case_id: caseId, organization_id: organizationId, user_id: userId },
    })
    .then((res) => {
      // TODO: do something?
      return res.data.data;
    });
};

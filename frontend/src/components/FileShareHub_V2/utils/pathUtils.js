// frontend/src/components/FileShareHub_V2/utils/pathUtils.js

export function joinPath(...segments) {
  const joined = segments
    .filter(Boolean)
    .join("/")
    .replace(/\/+/g, "/")
    .replace(/^\/|\/$/g, "");
  return decodeURIComponent(joined); // UI'de düzgün görünmesi için decode
}

export function getEncodedPath(path) {
  return encodeURIComponent(path);
}

export function getParentPath(path) {
  const parts = path.split("/").filter(Boolean);
  parts.pop();
  return parts.join("/");
}

export function getBreadcrumbs(path) {
  const parts = path.split("/").filter(Boolean);
  const breadcrumbs = [];
  let current = "";
  for (const part of parts) {
    current += `${part}/`;
    breadcrumbs.push({
      label: decodeURIComponent(part),
      path: current.replace(/\/$/, ""),
    });
  }
  return breadcrumbs;
}

export function isRootPath(path) {
  return !path || path === "/";
}

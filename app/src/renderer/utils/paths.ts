export function joinPath(base: string, name: string) {
  if (!base) {
    return name;
  }
  const separator = base.includes("\\") ? "\\" : "/";
  return `${base.replace(/[\\/]+$/, "")}${separator}${name}`;
}

export function extractFileName(pathValue: string) {
  if (!pathValue) {
    return "";
  }
  const parts = pathValue.split(/[\\/]/);
  return parts[parts.length - 1] || "";
}

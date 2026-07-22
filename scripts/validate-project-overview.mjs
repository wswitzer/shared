import fs from "node:fs";

const file = new URL("../PL/project-overview/project-overview.json", import.meta.url);
const data = JSON.parse(fs.readFileSync(file, "utf8"));
const raw = JSON.stringify(data);

const required = [
  data.meta?.title,
  data.meta?.lastUpdated,
  data.phase?.label,
  data.phase?.checkpoint,
  data.focus?.headline
];

if (required.some((value) => typeof value !== "string" || value.trim() === "")) {
  throw new Error("Project overview is missing required text.");
}

if (data.meta.public !== true) {
  throw new Error("Project overview must explicitly remain public-safe.");
}

for (const collection of ["signals", "decisions", "openQuestions", "actions", "links"]) {
  if (!Array.isArray(data[collection]) || data[collection].length === 0) {
    throw new Error(`Project overview collection is missing: ${collection}`);
  }
}

const forbidden = /(password|secret|token|private[_ -]?key|whatsapp|zoom\.us\/j|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})/i;

if (forbidden.test(raw)) {
  throw new Error("Project overview contains a prohibited private or credential-like value.");
}

console.log(`Project overview is valid (${data.meta.lastUpdated}).`);
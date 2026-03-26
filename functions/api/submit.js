// Cloudflare Pages Function: receive form submissions, create pending YAML in GitHub repo.
// No AI processing here — just a dumb pipe from form to git.

const GITHUB_REPO = "agentr2000-oss/ijm-legal-library";
const VALID_ACCESS = ["public", "backend-needed"];

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 50);
}

function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  const encoder = new TextEncoder();
  const bufA = encoder.encode(a);
  const bufB = encoder.encode(b);
  let result = 0;
  for (let i = 0; i < bufA.length; i++) {
    result |= bufA[i] ^ bufB[i];
  }
  return result === 0;
}

function buildYaml(data) {
  const lines = [
    `submitted_at: "${data.submitted_at}"`,
    `title: "${data.title.replace(/"/g, '\\"')}"`,
  ];
  if (data.url) {
    lines.push(`url: "${data.url}"`);
  }
  if (data.notes) {
    lines.push(`notes: >`, `  ${data.notes.replace(/\n/g, "\n  ")}`);
  }
  lines.push(`access: "${data.access}"`);
  if (data.access === "backend-needed" && data.retrieval_notes) {
    lines.push(
      `retrieval_notes: >`,
      `  ${data.retrieval_notes.replace(/\n/g, "\n  ")}`
    );
  }
  return lines.join("\n") + "\n";
}

export async function onRequestPost(context) {
  const { env, request } = context;

  // Parse body
  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse(400, { ok: false, error: "Invalid JSON body" });
  }

  const { title, url, notes, access, passphrase, retrieval_notes } = body;

  // Auth
  if (!passphrase || !timingSafeEqual(passphrase, env.SUBMIT_PASSPHRASE)) {
    return jsonResponse(401, { ok: false, error: "Invalid passphrase" });
  }

  // Validate
  const errors = [];
  if (!title || !title.trim()) errors.push("Title is required");
  if (!access || !VALID_ACCESS.includes(access))
    errors.push("Access must be 'public' or 'backend-needed'");
  if (
    access === "backend-needed" &&
    (!retrieval_notes || !retrieval_notes.trim())
  )
    errors.push("Retrieval notes are required for backend-needed entries");

  if (errors.length) {
    return jsonResponse(400, { ok: false, error: errors.join("; ") });
  }

  // Build YAML content
  const now = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19) + "Z";
  const slug = slugify(title);
  const filename = `${now}-${slug}.yml`;

  const yamlContent = buildYaml({
    submitted_at: new Date().toISOString(),
    title: title.trim(),
    url: url ? url.trim() : "",
    notes: notes ? notes.trim() : "",
    access,
    retrieval_notes: retrieval_notes ? retrieval_notes.trim() : "",
  });

  // Create file in GitHub via Contents API
  const path = `pending/${filename}`;
  const githubUrl = `https://api.github.com/repos/${GITHUB_REPO}/contents/${path}`;

  try {
    const res = await fetch(githubUrl, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${env.GITHUB_TOKEN}`,
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "ijm-legal-library-submit",
      },
      body: JSON.stringify({
        message: `pending: ${title.trim()}`,
        content: btoa(unescape(encodeURIComponent(yamlContent))),
        branch: "main",
      }),
    });

    if (!res.ok) {
      const err = await res.text();
      console.error("GitHub API error:", res.status, err);
      return jsonResponse(502, {
        ok: false,
        error: "Failed to create submission. Please try again.",
      });
    }

    return jsonResponse(200, {
      ok: true,
      message: "Submitted! Entry queued for processing.",
      filename,
    });
  } catch (err) {
    console.error("GitHub API request failed:", err);
    return jsonResponse(502, {
      ok: false,
      error: "Failed to reach GitHub. Please try again.",
    });
  }
}

// Handle OPTIONS for CORS preflight (in case submit.html is on a different origin during dev)
export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}

function jsonResponse(status, data) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}

/* WebAuthn browser-side helpers for CyberSkills Hub */

function b64urlToUint8(b64url) {
  const b64 = b64url.replace(/-/g, '+').replace(/_/g, '/');
  const padded = b64.padEnd(b64.length + (4 - b64.length % 4) % 4, '=');
  return Uint8Array.from(atob(padded), c => c.charCodeAt(0));
}

function uint8ToB64url(bytes) {
  return btoa(String.fromCharCode(...new Uint8Array(bytes)))
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

async function fetchJSON(url, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

/* Registration */
function parseRegOpts(opts) {
  return {
    ...opts,
    challenge: b64urlToUint8(opts.challenge),
    user: { ...opts.user, id: b64urlToUint8(opts.user.id) },
    excludeCredentials: (opts.excludeCredentials || []).map(c => ({
      ...c, id: b64urlToUint8(c.id)
    })),
  };
}

function serializeAttestation(cred) {
  const resp = cred.response;
  return {
    id: cred.id,
    rawId: uint8ToB64url(cred.rawId),
    type: cred.type,
    response: {
      clientDataJSON: uint8ToB64url(resp.clientDataJSON),
      attestationObject: uint8ToB64url(resp.attestationObject),
    },
  };
}

/* Authentication */
function parseAuthOpts(opts) {
  return {
    ...opts,
    challenge: b64urlToUint8(opts.challenge),
    allowCredentials: (opts.allowCredentials || []).map(c => ({
      ...c, id: b64urlToUint8(c.id)
    })),
  };
}

function serializeAssertion(cred) {
  const resp = cred.response;
  return {
    id: cred.id,
    rawId: uint8ToB64url(cred.rawId),
    type: cred.type,
    response: {
      clientDataJSON: uint8ToB64url(resp.clientDataJSON),
      authenticatorData: uint8ToB64url(resp.authenticatorData),
      signature: uint8ToB64url(resp.signature),
      userHandle: resp.userHandle ? uint8ToB64url(resp.userHandle) : null,
    },
  };
}

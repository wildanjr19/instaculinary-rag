import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { createServer } from 'node:http';
import { fileURLToPath } from 'node:url';
import { setTimeout as delay } from 'node:timers/promises';
import test from 'node:test';

const frontendDir = fileURLToPath(new URL('../', import.meta.url));

async function listen(server) {
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  return server.address().port;
}

async function close(server) {
  server.closeAllConnections();
  await new Promise(resolve => server.close(resolve));
}

test('production chat proxy boundaries', { timeout: 60_000 }, async t => {
  const calls = [];
  let redirectedCalls = 0;
  const backend = createServer(async (req, res) => {
    if (req.url === '/redirect-target') {
      redirectedCalls++;
      res.end('{}');
      return;
    }
    let raw = '';
    for await (const chunk of req) raw += chunk;
    const body = JSON.parse(raw);
    calls.push(body);
    const query = body.query;
    if (query === 'redirect') {
      res.writeHead(302, { Location: '/redirect-target' });
      res.end();
      return;
    }
    if (query === 'non-json') {
      res.writeHead(500, { 'Content-Type': 'text/html' });
      res.end('<html>private-backend-details</html>');
      return;
    }
    if (query === 'slow-headers' || query === 'slow-body') {
      if (query === 'slow-body') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.write('{"query_summary":');
      }
      const timer = setTimeout(() => res.end('{}'), 2_000);
      res.once('close', () => clearTimeout(timer));
      return;
    }
    const status = { invalid: 422, failure: 500, 'invalid-ai': 502 }[query] || 200;
    res.writeHead(status, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(status === 422 ? { detail: 'private-validation-details' } : {
      query_summary: 'Test response', results: [], ...(status !== 200 ? { error: 'Safe error' } : {}),
    }));
  });
  const backendPort = await listen(backend);
  const probe = createServer();
  const frontendPort = await listen(probe);
  await close(probe);
  const origin = `http://127.0.0.1:${frontendPort}`;
  let output = '';
  const child = spawn(process.execPath, ['node_modules/next/dist/bin/next', 'start', '--hostname', '127.0.0.1', '--port', String(frontendPort)], {
    cwd: frontendDir,
    env: { ...process.env, BACKEND_URL: `http://127.0.0.1:${backendPort}`, BACKEND_TIMEOUT_MS: '1000', NEXT_TELEMETRY_DISABLED: '1' },
    windowsHide: true,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  for (const stream of [child.stdout, child.stderr]) {
    stream.on('data', chunk => { output = (output + chunk.toString()).slice(-8_000); });
  }
  let backendOpen = true;
  const post = body => fetch(`${origin}/api/chat`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body,
    signal: AbortSignal.timeout(5_000),
  });
  try {
    let ready = false;
    for (let attempt = 0; attempt < 100; attempt++) {
      if (child.exitCode !== null) throw new Error(`Next.js exited: ${output}`);
      try {
        ready = (await fetch(origin, { signal: AbortSignal.timeout(1_000) })).ok;
        if (ready) break;
      } catch { /* Server may still be starting. */ }
      await delay(100);
    }
    assert.ok(ready, `Next.js did not start. Run npm run build first.\n${output}`);

    for (const [query, expected] of [['ok', 200], ['invalid', 422], ['failure', 500], ['invalid-ai', 502], ['non-json', 502]]) {
      await t.test(`${query}: HTTP ${expected}`, async () => {
        const res = await post(JSON.stringify({ query }));
        assert.equal(res.status, expected);
        const raw = await res.text();
        assert.deepEqual(JSON.parse(raw).results, []);
        assert.ok(!raw.includes('private-'));
      });
    }
    assert.deepEqual(calls[0], { query: 'ok' });
    await t.test('malformed JSON never reaches backend', async () => {
      const count = calls.length;
      const res = await post('{');
      assert.equal(res.status, 400);
      assert.deepEqual((await res.json()).results, []);
      assert.equal(calls.length, count);
    });
    await t.test('backend redirect is not followed', async () => {
      const res = await post(JSON.stringify({ query: 'redirect' }));
      assert.equal(res.status, 502);
      assert.deepEqual((await res.json()).results, []);
      assert.equal(redirectedCalls, 0);
    });
    for (const query of ['slow-headers', 'slow-body']) {
      await t.test(`${query}: HTTP 504`, async () => {
        const res = await post(JSON.stringify({ query }));
        assert.equal(res.status, 504);
        assert.deepEqual((await res.json()).results, []);
      });
    }
    await close(backend);
    backendOpen = false;
    await t.test('unavailable backend returns a generic HTTP 502', async () => {
      const res = await post(JSON.stringify({ query: 'offline' }));
      assert.equal(res.status, 502);
      const raw = await res.text();
      assert.deepEqual(JSON.parse(raw).results, []);
      assert.ok(!raw.includes('ECONNREFUSED'));
    });
  } finally {
    if (backendOpen) await close(backend);
    if (child.exitCode === null && child.signalCode === null) {
      const exited = once(child, 'exit');
      child.kill();
      const timer = setTimeout(() => child.kill('SIGKILL'), 5_000);
      timer.unref();
      await exited;
      clearTimeout(timer);
    }
  }
});

const measurementForm = document.getElementById('measurement-form');
const results = document.getElementById('results');
const accessToken = null;
let localNetworkTimer = null;
let localNetworkRequestInFlight = false;
const localNetworkHistory = [];
const localHistoryLimit = 60;

const getHeaders = (includeJson = false) => {
  const headers = {};
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }
  if (includeJson) {
    headers['Content-Type'] = 'application/json';
  }
  return headers;
};

const toJson = (form) => {
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  payload.timestamp = payload.timestamp ? new Date(payload.timestamp).toISOString() : null;
  payload.rsrp = Number(payload.rsrp);
  payload.rsrq = Number(payload.rsrq);
  payload.rssi = Number(payload.rssi);
  payload.sinr = Number(payload.sinr);
  payload.download_speed = Number(payload.download_speed);
  payload.upload_speed = Number(payload.upload_speed);
  payload.latency = Number(payload.latency);
  payload.packet_loss = Number(payload.packet_loss);
  payload.connected_users = Number(payload.connected_users);
  payload.call_drop_rate = Number(payload.call_drop_rate);
  payload.handover_failure_rate = Number(payload.handover_failure_rate);
  return payload;
};

const setResults = (value) => {
  results.textContent = JSON.stringify(value, null, 2);
};

const handleApiError = (response, data) => {
  const message = data.detail || `Request failed (${response.status})`;
  throw new Error(message);
};

const megabitsPerSecond = (byteCount, elapsedMs) =>
  (byteCount * 8) / Math.max(elapsedMs, 1) / 1000;

const measureBrowserNetwork = async () => {
  const latencySamples = [];
  const pingUrl = `https://speed.cloudflare.com/__down?bytes=1&cb=${Date.now()}`;

  for (let sample = 0; sample < 3; sample += 1) {
    const startedAt = performance.now();
    const response = await fetch(pingUrl, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Latency check failed (${response.status})`);
    await response.arrayBuffer();
    latencySamples.push(performance.now() - startedAt);
  }

  const latencyMs = latencySamples.reduce((sum, value) => sum + value, 0) / latencySamples.length;
  const downloadBytes = 5 * 1024 * 1024;
  const downloadStartedAt = performance.now();
  const downloadResponse = await fetch(
    `https://speed.cloudflare.com/__down?bytes=${downloadBytes}&cb=${Date.now()}`,
    { cache: 'no-store' }
  );
  if (!downloadResponse.ok) throw new Error(`Download test failed (${downloadResponse.status})`);
  const downloaded = await downloadResponse.arrayBuffer();
  const downloadMbps = megabitsPerSecond(downloaded.byteLength, performance.now() - downloadStartedAt);

  const uploadBytes = 1024 * 1024;
  const uploadPayload = new Uint8Array(uploadBytes);
  for (let offset = 0; offset < uploadBytes; offset += 65536) {
    crypto.getRandomValues(uploadPayload.subarray(offset, Math.min(offset + 65536, uploadBytes)));
  }
  const uploadStartedAt = performance.now();
  const uploadResponse = await fetch(`https://speed.cloudflare.com/__up?cb=${Date.now()}`, {
    method: 'POST',
    body: uploadPayload,
    cache: 'no-store',
  });
  if (!uploadResponse.ok) throw new Error(`Upload test failed (${uploadResponse.status})`);
  await uploadResponse.arrayBuffer();
  const uploadDuration = Math.max(1, performance.now() - uploadStartedAt - latencyMs);
  const uploadMbps = megabitsPerSecond(uploadBytes, uploadDuration);

  return { latencyMs, downloadMbps, uploadMbps };
};

const classifyConnection = ({ latencyMs, downloadMbps }) => {
  if (latencyMs > 250 || downloadMbps < 2) return 'Poor';
  if (latencyMs > 150 || downloadMbps < 10) return 'Fair';
  if (latencyMs > 80 || downloadMbps < 50) return 'Good';
  return 'Excellent';
};

const renderTrendChart = (points) => {
  const svg = document.getElementById('trend-chart');
  if (!svg) return;

  const width = 640;
  const height = 220;
  const padding = 20;
  const maxValue = Math.max(
    1,
    ...points.flatMap((point) => [point.latency, point.packet_loss, point.download_speed])
  );

  const toY = (value) => height - padding - (value / maxValue) * (height - padding * 2);
  const toX = (index, count) => padding + (index * (width - padding * 2)) / Math.max(count - 1, 1);

  const seriesColors = {
    latency: '#60a5fa',
    packet_loss: '#fbbf24',
    download_speed: '#34d399',
  };

  const lines = Object.entries(seriesColors)
    .map(([key, color]) => {
      const values = points.map((point) => point[key]);
      const path = values
        .map((value, index) => `${index === 0 ? 'M' : 'L'} ${toX(index, values.length)} ${toY(value)}`)
        .join(' ');
      return `<path d="${path}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linecap="round"/>`;
    })
    .join('');

  const grid = Array.from({ length: 5 })
    .map((_, index) => {
      const y = padding + (index * (height - padding * 2)) / 4;
      return `<line x1="${padding}" y1="${y}" x2="${width - padding}" y2="${y}" stroke="rgba(148,163,184,0.2)"/>`;
    })
    .join('');

  svg.innerHTML = `
    <g>
      ${grid}
      ${lines}
    </g>
  `;
};

const renderDashboard = (data) => {
  const snapshot = data.snapshot || {};
  document.getElementById('total-measurements').textContent = snapshot.total_measurements ?? '-';
  document.getElementById('active-cells').textContent = snapshot.active_cells ?? '-';
  document.getElementById('avg-latency').textContent = `${snapshot.average_latency_ms ?? 0} ms`;
  document.getElementById('avg-packet-loss').textContent = `${snapshot.average_packet_loss_pct ?? 0}%`;
  document.getElementById('avg-download-speed').textContent = `${snapshot.average_download_speed_mbps ?? 0} Mbps`;

  const rows = data.recent_measurements || [];
  const tbody = document.getElementById('recent-signals-body');

  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="6">No measurements yet.</td></tr>';
    return;
  }

  tbody.innerHTML = rows
    .map(
      (item) => `
        <tr>
          <td>${item.cell_id}</td>
          <td>${item.region}</td>
          <td>${item.network_type}</td>
          <td>${item.latency}</td>
          <td>${item.packet_loss}</td>
          <td>${item.download_speed}</td>
        </tr>
      `
    )
    .join('');
};

const formatTrafficRate = (bytesPerSecond) => {
  if (bytesPerSecond >= 1024 * 1024) {
    return `${(bytesPerSecond / (1024 * 1024)).toFixed(2)} MiB/s`;
  }
  if (bytesPerSecond >= 1024) {
    return `${(bytesPerSecond / 1024).toFixed(1)} KiB/s`;
  }
  return `${Math.round(bytesPerSecond)} B/s`;
};

const renderLocalNetworkChart = () => {
  const svg = document.getElementById('local-network-chart');
  const status = document.getElementById('local-chart-status');
  const width = 640;
  const height = 220;
  const padding = 26;

  if (!localNetworkHistory.length) return;

  const series = [
    { key: 'receiveMbps', color: '#34d399' },
    { key: 'transmitMbps', color: '#60a5fa' },
    { key: 'latencyMs', color: '#fbbf24' },
  ];
  const maxValues = Object.fromEntries(
    series.map(({ key }) => [
      key,
      Math.max(1, ...localNetworkHistory.map((point) => point[key] ?? 0)),
    ])
  );
  const xForIndex = (index) =>
    padding +
    (index * (width - padding * 2)) / Math.max(localNetworkHistory.length - 1, 1);
  const yForValue = (value, key) =>
    height - padding - (value / maxValues[key]) * (height - padding * 2);
  const grid = Array.from({ length: 5 }, (_, index) => {
    const y = padding + (index * (height - padding * 2)) / 4;
    return `<line x1="${padding}" y1="${y}" x2="${width - padding}" y2="${y}" stroke="rgba(148,163,184,0.2)"/>`;
  }).join('');
  const lines = series
    .map(({ key, color }) => {
      let started = false;
      const path = localNetworkHistory
        .map((point, index) => {
          const value = point[key];
          if (value === null || value === undefined) return null;
          const command = started ? 'L' : 'M';
          started = true;
          return `${command} ${xForIndex(index)} ${yForValue(value, key)}`;
        })
        .filter(Boolean)
        .join(' ');
      return path
        ? `<path d="${path}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>`
        : '';
    })
    .join('');

  svg.innerHTML = `<g>${grid}${lines}</g>`;
  const firstTime = new Date(localNetworkHistory[0].timestamp).toLocaleTimeString();
  const lastTime = new Date(localNetworkHistory[localNetworkHistory.length - 1].timestamp)
    .toLocaleTimeString();
  status.textContent =
    `${localNetworkHistory.length} samples · each line scaled independently · ${firstTime}–${lastTime}`;
};

const renderLocalNetworkStatus = (data) => {
  const internet = data.internet || {};
  document.getElementById('host-internet-status').textContent = internet.reachable
    ? 'Connected'
    : 'Unavailable';
  document.getElementById('host-probe-latency').textContent =
    internet.latency_ms === null || internet.latency_ms === undefined
      ? '—'
      : `${internet.latency_ms} ms`;

  const wifi = data.wifi;
  document.getElementById('host-wifi-ssid').textContent = wifi?.ssid || 'Not connected / unavailable';
  document.getElementById('host-wifi-signal').textContent =
    wifi?.signal_percent || 'Not available';
  document.getElementById('host-wifi-radio').textContent = wifi
    ? [wifi.radio_type, wifi.channel ? `ch ${wifi.channel}` : null].filter(Boolean).join(' / ') ||
      'Not available'
    : 'Not available';
  document.getElementById('host-wifi-rates').textContent = wifi
    ? `${wifi.receive_rate_mbps || '—'} / ${wifi.transmit_rate_mbps || '—'} Mbps`
    : 'Not available';

  const adapterBody = document.getElementById('local-network-adapters');
  adapterBody.replaceChildren();
  let totalReceiveRate = 0;
  let totalTransmitRate = 0;
  if (!data.interfaces?.length) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 6;
    cell.textContent = 'No network adapters were reported by the operating system.';
    row.append(cell);
    adapterBody.append(row);
  } else {
    for (const adapter of data.interfaces) {
      const row = document.createElement('tr');
      const isLoopback =
        adapter.name.toLowerCase().includes('loopback') ||
        (adapter.addresses?.length > 0 &&
          adapter.addresses.every(
            (address) => address.address === '127.0.0.1' || address.address === '::1'
          ));
      if (adapter.is_up && !isLoopback) {
        totalReceiveRate += adapter.receive_bytes_per_second || 0;
        totalTransmitRate += adapter.transmit_bytes_per_second || 0;
      }
      const values = [
        adapter.name,
        adapter.is_up ? 'Up' : 'Down',
        adapter.speed_mbps ? `${adapter.speed_mbps} Mbps` : 'Not reported',
        adapter.addresses?.map((address) => `${address.address} (${address.family})`).join(', ') ||
          'No IP address',
        formatTrafficRate(adapter.receive_bytes_per_second || 0),
        formatTrafficRate(adapter.transmit_bytes_per_second || 0),
      ];
      for (const value of values) {
        const cell = document.createElement('td');
        cell.textContent = value;
        row.append(cell);
      }
      adapterBody.append(row);
    }
  }

  localNetworkHistory.push({
    timestamp: data.sampled_at * 1000,
    receiveMbps: (totalReceiveRate * 8) / 1_000_000,
    transmitMbps: (totalTransmitRate * 8) / 1_000_000,
    latencyMs: internet.reachable ? internet.latency_ms : null,
  });
  if (localNetworkHistory.length > localHistoryLimit) {
    localNetworkHistory.shift();
  }
  renderLocalNetworkChart();

  const sampledAt = new Date(data.sampled_at * 1000).toLocaleTimeString();
  document.getElementById('local-network-status').textContent =
    `${data.computer_name} · ${data.operating_system} · Updated ${sampledAt}`;
};

const refreshLocalNetworkStatus = async () => {
  if (localNetworkRequestInFlight) return;
  localNetworkRequestInFlight = true;
  try {
    const response = await fetch('/network/local-status', { headers: getHeaders() });
    const data = await response.json();
    if (!response.ok) handleApiError(response, data);
    renderLocalNetworkStatus(data);
  } catch (error) {
    document.getElementById('local-network-status').textContent =
      `Unable to read local network details: ${error.message}`;
  } finally {
    localNetworkRequestInFlight = false;
  }
};

const startLocalNetworkPolling = () => {
  if (localNetworkTimer !== null) {
    window.clearInterval(localNetworkTimer);
  }
  void refreshLocalNetworkStatus();
  localNetworkTimer = window.setInterval(() => {
    void refreshLocalNetworkStatus();
  }, 5000);
};

const loadDashboard = async () => {
  try {
    const summaryResponse = await fetch('/analytics/summary', { headers: getHeaders() });
    const summaryData = await summaryResponse.json();
    if (!summaryResponse.ok) {
      handleApiError(summaryResponse, summaryData);
    }
    renderDashboard(summaryData);

    const trendResponse = await fetch('/analytics/trends', { headers: getHeaders() });
    const trendData = await trendResponse.json();
    if (!trendResponse.ok) {
      handleApiError(trendResponse, trendData);
    }
    renderTrendChart(trendData.points || []);
  } catch (error) {
    setResults({ error: error.message });
  }
};

measurementForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = toJson(measurementForm);

  try {
    const response = await fetch('/network/data', {
      method: 'POST',
      headers: { ...getHeaders(true) },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      handleApiError(response, data);
    }
    setResults({ created: true, response: data });
    await loadDashboard();
  } catch (error) {
    setResults({ error: error.message });
  }
});

document.getElementById('fetch-measurements').addEventListener('click', async () => {
  try {
    const response = await fetch('/network/data', { headers: getHeaders() });
    const data = await response.json();
    if (!response.ok) handleApiError(response, data);
    setResults(data);
    await loadDashboard();
  } catch (error) {
    setResults({ error: error.message });
  }
});

document.getElementById('predict-btn').addEventListener('click', async () => {
  const payload = toJson(measurementForm);
  try {
    const response = await fetch('/predict/quality', {
      method: 'POST',
      headers: { ...getHeaders(true) },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) handleApiError(response, data);
    setResults({ prediction: data });
  } catch (error) {
    setResults({ error: error.message });
  }
});

document.getElementById('anomaly-btn').addEventListener('click', async () => {
  const payload = toJson(measurementForm);
  try {
    const response = await fetch('/detect/anomaly', {
      method: 'POST',
      headers: { ...getHeaders(true) },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) handleApiError(response, data);
    setResults({ anomaly: data });
  } catch (error) {
    setResults({ error: error.message });
  }
});

document.getElementById('run-speed-test').addEventListener('click', async (event) => {
  const button = event.currentTarget;
  const status = document.getElementById('connection-status');
  const profile = navigator.connection;
  const profileLabel = profile
    ? [profile.type, profile.effectiveType].filter(Boolean).join(' / ') || 'Not reported'
    : 'Not reported by browser';
  button.disabled = true;
  document.getElementById('live-latency').textContent = '—';
  document.getElementById('live-download').textContent = '—';
  document.getElementById('live-upload').textContent = '—';
  document.getElementById('connection-profile').textContent = '—';
  status.textContent = 'Testing latency, download, and upload…';

  try {
    if (!navigator.onLine) {
      throw new Error('This browser reports that it is offline.');
    }
    const measured = await measureBrowserNetwork();
    measured.connectionProfile = profileLabel;
    measured.quality = classifyConnection(measured);
    document.getElementById('live-latency').textContent = `${Math.round(measured.latencyMs)} ms`;
    document.getElementById('live-download').textContent = `${measured.downloadMbps.toFixed(2)} Mbps`;
    document.getElementById('live-upload').textContent = `${measured.uploadMbps.toFixed(2)} Mbps`;
    document.getElementById('connection-profile').textContent = profileLabel;
    status.textContent = `Internet connection: ${measured.quality}`;
    setResults({ network_test: measured });
  } catch (error) {
    status.textContent = `Test failed: ${error.message}`;
    setResults({ network_test_error: error.message });
  } finally {
    button.disabled = false;
  }
});

loadDashboard();
startLocalNetworkPolling();

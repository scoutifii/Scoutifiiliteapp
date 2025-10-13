// Requires DataTables assets loaded in base.html
(async function () {
  try {
    const res = await fetch('/log', { credentials: 'same-origin' });
    const payload = await res.json();
    const data = (payload?.log_data?.log_list || []).map(r => ([
      r.username || '',
      r.activity || '',
      r.ip_address || '',
      r.url || '',
      r.user_agent || '',
      new Date(r.created_at).toLocaleString()
    ]));

    $('#logs').DataTable({
      data,
      columns: [
        { title: 'Username' },
        { title: 'Activity' },
        { title: 'IP Address' },
        { title: 'URL' },
        { title: 'User Agent' },
        { title: 'Date & Time' }
      ],
      responsive: true,
      pageLength: 25,
      order: [[5, 'desc']]
    });
  } catch (e) {
    console.error(e);
  }
});

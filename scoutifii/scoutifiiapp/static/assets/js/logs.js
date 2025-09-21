fetch('/logs')
.then(response => response.json())
.then(data => {
    console.log(data);
    if (data.error) {
        console.error(data.error);
    } else {
        const logsData = data.log_list.map(log => ({
        created_at: log.created_at,
        username: log.username,
        activity: log.activity,
        ip_address: log.ip_address,
        url: log.url,
        user_agent: log.user_agent
        }));

        $('#logs').DataTable({
            data: logsData,
            columns: [
                { data: 'username', title: 'Username' },
                { data: 'activity', title: 'Activity' },
                { data: 'ip_address', title: 'IP Address' },
                { data: 'url', title: 'Url' },
                { data: 'user_agent', title: 'User Agent' },
                { data: 'created_at', title: 'Date & Time' }
            ],
            destroy: true
        });

    }
})
.catch(error => console.error('Error:', error));

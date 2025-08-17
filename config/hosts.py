from django_hosts import patterns, host

# Two hosts: root domain -> public site; dashboard subdomain -> application
host_patterns = patterns(
    '',
    host(r'^$', 'config.urls_public', name='root'),
    host(r'^dashboard$', 'config.urls_dashboard', name='dashboard'),
)

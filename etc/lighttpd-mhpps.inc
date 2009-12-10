##################
# this file is included by /etc/lighttpd/lighttpd.conf

    server.document-root = "/mnt/hubplus-static/mhpss"

    fastcgi.server = (
        "/hubplus.fcgi" => (
            "main" => (
                "host" => "172.24.2.71",
                "port" => 3033,
                "check-local" => "disable",
		"allow-x-send-file" => "enable"
            )
        )
    )

  # alias.url = ( "/static" => "/wherever" )

    url.rewrite-once = (
      # "^(/media.*)$" => "$1",
      # "^/favicon\.ico$" => "/media/favicon.ico",
        "^/site_media(/avatars/.*)" => "$1",
	"^/site_media(/css/.*)" => "$1",
	"^/site_media(/themes/.*)" => "$1",
	"^/site_media(/images/.*)" => "$1",
	"^/site_media(/js/.*)" => "$1",
        "^(/.*)$" => "/hubplus.fcgi$1"
    )


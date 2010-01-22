// Use this for all the "onReady" and "onLoaded" etc. events

jq(document).ready(function () {
    profile_ready();
    permission_ready();
    jq(".accordion").accordion({ autoHeight: false });
    plus_links_ready();
    listing_ready();
    plus_status_ready();
    if (jq('#intro_bar_tabs').length) {
	home();
    }
    if (jq('.upload_field').length==1) {
	replace_file();
    }
    if (jq('.autocomplete_uploadable_groups').length==1) {
	autocomplete_uploadable_groups();
    }
});

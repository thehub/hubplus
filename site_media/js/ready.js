// Use this for all the "onReady" and "onLoaded" etc. events

jq(document).ready(function () {
    profile_ready();
    permission_ready();
    jq(".accordion").accordion({ autoHeight: false });
    plus_links_ready();
});

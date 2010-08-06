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

    if (jq('.tinymce').length==1) {

      var config = {
	mode : null,
	editor_selector :"tinymce",

	theme : "advanced",
	plugins : "emotions,spellchecker,advhr,insertdatetime,preview,table",

	theme_advanced_buttons1 : "newdocument,|,bold,italic,underline,|,sub,sup,|,justifyleft,justifycenter,justifyright,|,formatselect",
	theme_advanced_buttons2 : "cut,copy,paste,|,undo,redo,|,bullist,numlist,|,outdent,indent,|,link,unlink,anchor,image",
	theme_advanced_buttons3 : "insertdate,inserttime,|,table,|,charmap,emotions,advhr,|,spellchecker,removeformat,|,code,preview,",
	theme_advanced_toolbar_location : "top",
	theme_advanced_toolbar_align : "left",
	theme_advanced_statusbar_location : "bottom"
      };

      tinyMCE.init(config);
      var id = jq('#wiki_content').attr('id');
      tinyMCE.execCommand("mceAddControl", false, id);
    }

});

#!/bin/sh

cp on_clone/post-merge .git/hooks/

ensure() {
   if [ ! -d "$1" ]; then
      mkdir "$1";
   fi;
}


ensure 'site_media'
cd site_media
ensure 'css'
ensure 'js'
ensure 'themes'
ensure 'images'
ensure 'member_res' 
ensure 'avatars'

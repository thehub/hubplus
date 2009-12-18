from utils.jsmin import jsmin
import StringIO
from os import path, unlink
import md5


def minify(input_path):
   """return a minified version of a file as a python string
   """
   js_big = open(input_path)
   minified = jsmin(js_big.read())
   js_big.close()
   return minified

def get_version_no(file_name, default_path="hubspace/static/javascript"):
   """used in master template
   """
   base = path.abspath('.')
   try:
      return open(path.join(base, default_path, file_name + '.version')).read()
   except IOError:
      return 1

def get_file_list(path_or_filename_list, default_path):
   base = path.abspath('.')
   file_list = []
   for file_path in path_or_filename_list:
      if path.exists(path.join(base, file_path)):
         file_list.append(path.join(base, file_path))
      elif path.exists(path.join(base, default_path, file_path)):
         file_list.append(path.join(base, default_path, file_path))
      else:
         print "file: " + file_path + " not found when compiling javascript"
   return file_list
   
def compile(path_or_filename_list, default_path="static/javascript", output_filename="file.js", minified=False):
   """Input filenames that exist in the default_path or for which a full path is provided.
      Minfies and concatanates  js strings adding a special variable at the beginning to indicate that the file is compiled to key functions
   """
   #get the descriptors
   file_list = get_file_list(path_or_filename_list, default_path)
   if minified:
      compiled_js = "compiled = true;"
   else:
      compiled_js = ""

   for file_name in file_list:
      if minified:
         compiled_js += minify(file_name) + ';\n'
      else:
         compiled_js += open(file_name).read() + '\n'

   base = path.abspath('.')
   js_hash = md5.new(compiled_js)
   try:
      js_hash_file = open(path.join(base, default_path, output_filename + '.hash'), 'r+')
   except IOError:
      js_hash_file = open(path.join(base, default_path, output_filename + '.hash'), 'w+')

   old_hash = js_hash_file.read()
   if old_hash==js_hash.hexdigest():
      print "nothing change in: " + output_filename 
      return
   js_hash_file.seek(0)
   js_hash_file.write(js_hash.hexdigest())
   try:
      js_version_no = open(path.join(base, default_path, output_filename + '.version'), 'r+')
   except IOError:
      js_version_no = open(path.join(base, default_path, output_filename + '.version'), 'w+')
   try:
      js_v_no = int(js_version_no.read())
   except ValueError:
      js_v_no = 0
   js_v_no += 1
   js_version_no.seek(0)
   js_version_no.write(str(js_v_no))
   file_out = open(path.join(base, default_path, versioned_file_name(output_filename, js_v_no)), 'w')
   for no in range(1, js_v_no):
      old_path = path.join(base, default_path, versioned_file_name(output_filename, no))
      if path.exists(old_path):
         unlink(old_path)
   file_out.write(compiled_js)
   file_out.close()
   print "file " + versioned_file_name(output_filename, js_v_no) + " written"
   return True

def versioned_file_name(filename, no):
   file_name_parts = filename.split('.')
   file_name_parts[-2] += str(no)
   return '.'.join(file_name_parts)
   




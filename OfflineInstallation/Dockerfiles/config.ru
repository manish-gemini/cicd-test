require 'rubygems'
require 'geminabox'
Geminabox.allow_delete = false
Geminabox.data = '/opt/rubygems'
run Geminabox::Server

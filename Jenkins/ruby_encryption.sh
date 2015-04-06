
#!/bin/bash
#Please make sure you have put file in /var/lib/jenkins and updated path in jenkins command line settings

/usr/local/rubyencoder/bin/rubyencoder --ruby 2.1.0 --ruby 2.2.0 -r '*.rb'
cp -r /usr/local/rubyencoder/rgloader .

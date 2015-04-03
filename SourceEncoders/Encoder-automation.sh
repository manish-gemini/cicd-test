#/bin/bash
yum install git -y
yum install rsync -y
rm -rf /opt/encoding/Gemini-poc-stack.git
rm -rf /opt/encoding/Gemini-poc-mgnt.git
rm -rf /opt/encrypted
mkdir /opt/encrypted
if [ ! -d /opt/encoding ]; then
    mkdir -p /opt/encoding
fi
cd /opt/encoding
git clone https://prakash-gemini:l3tm3in@github.com/Gemini-sys/Gemini-poc-stack.git
git clone https://prakash-gemini:l3tm3in@github.com/Gemini-sys/Gemini-poc-mgnt.git
CWD=`pwd`
SRC_DIR=$CWD/Gemini-poc-stack
DST_DIR=$CWD/Gemini-poc-stack-encrypted
rm -rf $DST_DIR
cp -r $SRC_DIR $DST_DIR

# cleanup - remove unwanted files
rm -rf $DST_DIR/replicate-transport-python
rm -rf $DST_DIR/orchestrate
rm -rf $DST_DIR/replicate
rm -rf $DST_DIR/appdb

cd $DST_DIR
# remove all .pyc files
for file in `find . -name "*.pyc" -print`
do
        rm -rf $file
done

# now compile all python files to bytecode (.pyc)
python -m compileall . >> /home/pythonencode.log

# remove all .py files
for file in `find . -name "*.py" -print`
do
        rm -rf $file
done

# remove java module src files
rm -rf $DST_DIR/jcommon

# remove p2v_convert src files
rm -rf $DST_DIR/p2v_convert

#Move encrypted source script to /opt/encrypted directory
mv /opt/encoding/Gemini-poc-stack-encrypted /opt/encrypted/Gemini-poc-stack

#scp /opt/encrypted directory to jenkins server under /home
ssh 209.205.208.181 rm -rf /home/Gemini-poc-stack
rsync -avz -e ssh /opt/encrypted/Gemini-poc-stack root@209.205.208.181:/home
mail -s "[`hostname`] Python Encode Log on `date`" prakash@assistanz.com < /home/pythonencode.log

#ruby encoding start
#ruby command for encoding
/usr/local/rubyencoder/bin/rubyencoder  --ruby 2.1.0 --ruby 2.2.0 -r "/opt/encoding/Gemini-poc-mgnt/*.rb" >> /home/rubyencoder.log
#copy encoder directory
cp -r /opt/encoding/Gemini-poc-mgnt /opt/encrypted
cp -r /usr/local/rubyencoder/rgloader /opt/encrypted
ssh 209.205.208.181 rm -rf /home/Gemini-poc-mgnt
rsync -avz -e ssh /opt/encrypted/Gemini-poc-mgnt root@209.205.208.181:/home
rsync -avz -e ssh /opt/encrypted/rgloader root@209.205.208.181:/home
rsync -avz -e ssh /opt/encrypted/rgloader root@209.205.208.181:/home
mail -s "[`hostname`] Ruby Encode Log on `date`" prakash@assistanz.com < /home/rubyencoder.log

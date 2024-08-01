# run all files in src directory and it's subdirectories with .test.py extension
echo "activating environment"
. .venv/bin/activate
echo "reading requirements"
sudo pip3 install -r ./reqs.txt
for file in $(find src -name "*.test.py"); do
    echo "running test $file"
    python3 $file
done

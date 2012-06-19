#!/bin/sh

# dumper.sh
# 
# class-dumper (using class-dump on i386 binaries)

_class="class-dump --arch i386" # you can easily add -S, -s, -a and -A flags ;) 

usage()
{
printf "\targ[1]: Frameworks' folder.\n\targ[2]: output folder.\n"
}

exiterr() { usage; exit 1; }

if [ ! -d "$1" ]; then exiterr; fi
if [ ! -d "$2" ]; then exiterr; fi
if [ "`ls $1 | grep '.framework'`" = "" ]; then echo "no frameworks found in $1"; exiterr; fi
if [ ! -d "$2" ]; then mkdir "$2"; fi


cd $1
for i in *.framework; do
shopt -s extglob
nameOf="$i"
nameF=${nameOf//@(.framework)/} 
echo $nameF 
mkdir $2/$nameF;
cd $i
for o in *; do
if [ -f $o ]; then $_class -H $o -o $2/$nameF &>/dev/null; fi
done
cd ..;nameF=;
done
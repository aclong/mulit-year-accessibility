#!/bin/bash

read monthname_in

year=${monthname_in:0:4}

month_string=${monthname_in:4:6}


#check that date is before today
today=`date +"%Y%m"`
if [[ ${year}${month_string} -ge today ]]; then
    continue
fi

#get date as digti for later
if [[ ${month_string:0:1} -eq 1 ]]; then
    month_dig=$month_string
else
    month_dig=${month_string:1:2}
fi
echo "working on ${year} ${month_string}"
#echo "month as digit is ${month_dig}"
this_otp_dir="/store/along_data/otp_working_dir/otp_wd_${year}_${month_string}"
#testing version just print stuff

#make the directory
echo "making directory ${this_otp_dir}"
mkdir $this_otp_dir
#get the correct year osm
#get "this year" for 01/04 and "next year" for 07/12
if [[ ${month_dig} -le 6 ]]; then
    osm_year=$year
elif [[ ${month_dig} -ge 7 ]]; then
    osm_year=$[year+1]
fi

echo "osm year is ${osm_year}"
#get the right folder for the osm data
osm_full_filepath="/home/ucfnacl/DATA/dynamic_accessibility/data/osm_data/west-midlands-${osm_year:2:4}0101.osm.pbf"
echo "osm 2 digit year ${osm_year:2:4}"
echo "full filepath ${osm_full_filepath}"
#check if the particular year you want exists as data if not select year before
if [ -f $osm_full_filepath ]; then
    cp $osm_full_filepath "${this_otp_dir}/"
    #echo "then copy ${osm_full_filepath} ${this_otp_dir}/"
else
    osm_minus1_year=$[osm_year-1]
    cp "/home/ucfnacl/DATA/dynamic_accessibility/data/osm_data/west-midlands-${osm_minus1_year:2:4}0101.osm.pbf" "${this_otp_dir}/"
    #echo "then copy /home/ucfnacl/DATA/dynamic_accessibility/data/osm_data/west-midlands-${osm_minus1_year:2:4}0101.osm.pbf ${this_otp_dir}/"
fi

#now get the gtfs data it may be the month before
#if it exists for the first of the given month use it tho
gtfs_dir="/store/along_data/gtfs_data/planar_network_converted_gtfs/"
if [ -f "${gtfs_dir}WM_${year}${month_string}01_gtfs.zip" ]; then
    gtfs_fullfilepth="${gtfs_dir}WM_${year}${month_string}01_gtfs.zip"
    #echo "${gtfs_fullfilepath}"
else
    gtfs_minus1month=$[month_dig-1]
    if [[ ${gtfs_minus1month} -lt 2 ]]; then
        gtfs_monthstring=$gtfs_minus1month
    else
        gtfs_monthstring="0${gtfs_minus1month}"
    fi
    gtfs_file=$(ls $gtfs_dir | grep "WM_${year}${gtfs_monthstring}[0-3][0-9]_gtfs.zip" | sort | tail -n1)
    echo "gtfs file is ${gtfs_file}"
    gtfs_fullfilepath="${gtfs_dir}${gtfs_file}"
fi
#now copy it to the current directory
#echo "copy over ${gtfs_fullfilepath} to ${this_otp_dir}"
cp $gtfs_fullfilepath "${this_otp_dir}"

#now everything is in place you can build the graph
#change to the working directory
echo "changing directory to ${this_otp_dir}"
cd $this_otp_dir
#make the graph directory and file
echo "making graph directory ${this_otp_dir}/graphs"
mkdir -p graphs/gb

#build the graph
echo "building the actual graph"
java -Xmx2G -d64 -server -jar ../otp-1.2.0-shaded.jar --basePath . --build .
echo "finished building the graph now removing old data"

#move new graph into ready directory
mv Graph.obj graphs/gb/

#remove the old now unneccesary gtfs and osm files
rm *gtfs.zip
rm *.osm.pbf

#go back up to the main directory
#echo "change back to old directory"
cd ../




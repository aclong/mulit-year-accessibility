#!/usr/bin/jython

# INPUT ###################################################################################################
###################################################################################################

# max number of threads to use in parallel
#check to see what you can fit on this CPU

#running at the same time as the other one so use half the number of threads
max_threads = 20

#run with the list of dates
tues_dates=[['2015', '01', '06'], ['2015', '04', '07'], ['2015', '07', '07'], ['2015', '10', '06'], ['2016', '01', '05'], ['2016', '04', '05'], ['2016', '07', '05'], ['2016', '10', '04'], ['2017', '01', '03'], ['2017', '04', '04'], ['2017', '07', '04'], ['2017', '10', '03'], ['2018', '01', '02'], ['2018', '04', '03'], ['2018', '07', '03'], ['2018', '10', '02'], ['2019', '01', '01'], ['2019', '04', '02'], ['2019', '07', '02'], ['2019', '10', '01'], ['2019', '11', '05'], ['2020', '01', '07'], ['2020', '04', '07'], ['2020', '07', '07'], ['2020', '10', '06'], ['2020', '11', '03'], ['2021', '01', '05'], ['2021', '04', '06'], ['2021', '07', '06'], ['2021', '10', '05']]

# Trips
mins = ['00', '10', '20','30', '40', '50']
hours = ['06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']

#run through the dates
#for year, month, day in tues_dates:

# set date of trips # now set by loop
#year= '2020'
#month = '04'
#day = '07'
#mydate = year+month+day

#travel modes
travel_mode_var='WALK,TRANSIT'

#file finding information
indir = '/store/along_data/accessibility_data/'
orig_file = 'oa_2011_points.csv'
result_file_name_string = 'gp_su_ma'

dest_file_no_ext = 'od_amenity_lists/individual_oa_dest_lists/'

#file writing information
travel_type='pub_trans'


###################################################################################################

import gc
gc.collect()

import os

# Start timing the code
import time
start_time = time.time()

# THREADED VERSION OF OTP SCRIPT
import threading
from time import sleep

from org.opentripplanner.scripting.api import OtpsEntryPoint

#run through the dates
for year, month, day in tues_dates:

    gc.collect()
    # set date of trips # now set by loop
    #year= '2020'
    #month = '04'
    #day = '07'
    mydate = year+month+day

    #change directory stuff if path exists
    otp_working_dir='/store/along_data/otp_working_dir/otp_wd_'+year+'_'+month

    #testing it works
    print("date "+mydate)
    print("working directory "+otp_working_dir)
    #continue


    if os.path.isdir(otp_working_dir):
        #print("directory exists")

        #continue
        os.chdir(otp_working_dir)


        # Instantiate an OtpsEntryPoint
        dir_graph = otp_working_dir+"/graphs"
        otp = OtpsEntryPoint.fromArgs(['--graphs', dir_graph,
                                       '--router', 'gb'])


        # Get the default router
        router = otp.getRouter('gb')



        ### make a list of jobs to do
        jobs = []
        for h in hours:
                for m in mins:
                        jobs.append((h,m))

        # define a function describing a complete job
        # I just copy-pasted what you had in the loop into here
        def do_the_stuff(h, m):

            #set the date_time character for files and int for otp
            datetime = [year, month, day, h, m, '00']
            datetime2 = [int(x) for x in datetime]

            #create file name
            fl_out = '/store/along_data/accessibility_data/long_run_accessibility_results/oa_'+result_file_name_string+'_'+travel_type+'_'+datetime[0]+datetime[1]+datetime[2]+'_'+datetime[3]+datetime[4]+'.csv'
            print('>>>>> '+fl_out+' ---------------------------------')

                # Create a default request for a given time
            req = otp.createRequest()
            req.setDateTime(datetime2[0],datetime2[1],datetime2[2],datetime2[3],datetime2[4],datetime2[5])
            req.setMaxTimeSec(7200)
            req.setModes(travel_mode_var)
            # define transport mode : ("WALK,CAR, TRANSIT, TRAM,RAIL,SUBWAY,FUNICULAR,GONDOLA,CABLE_CAR,BUS")
            # for more routing options, check: http://dev.opentripplanner.org/javadoc/0.19.0/org/opentripplanner/scripting/api/OtpsRoutingRequest.html

            # Read Points of Destination - The file points.csv contains the columns GEOID, X and Y [inside]
            origs = otp.loadCSVPopulation(indir+'/'+orig_file, 'oa_lat', 'oa_lon')
            print('origs read!')

            #create the file you are going to write results to
            with open(fl_out, 'a') as fo:
                fo.write(','.join([ 'origin', 'destination', 'amenity_type','walk_distance', 'travel_time', 'boardings', '\n' ]))

            j = -1

            with open(fl_out, 'a') as fo:
                for o in origs:
                    j = j + 1
                    if j % 500 == 0: print(str(j)+' stops for departure time '+h+':'+m+' processed at '+time.strftime('%a %H:%M:%S'))

                    req.setOrigin(o)
                    spt = router.plan(req)
                    if spt is None: continue

                    dests = otp.loadCSVPopulation(indir+'/'+dest_file_no_ext+'/'+mydate+'_'+o.getStringData('oa11cd')+'_dests.csv', 'am_lat', 'am_lon')

                    result = spt.eval(dests)

                    for r in result:
                        row = [o.getStringData('oa11cd'), r.getIndividual().getStringData('amenity'), r.getIndividual().getStringData('type'), r.getWalkDistance(), r.getTime(), r.getBoardings(), '\n']
                        fo.write(','.join(str(x) for x in row))
            fo.close()


        #
        # ^ that ^ function has to be defined before it's called
        # the threading bit is down here vvv
        #

        # how many threads do you want?
        #max_threads = int(raw_input('max threads (int) ? --> '))
        # start looping over jobs
        while len(jobs) > 0:
                if threading.active_count() < max_threads + 1:
                        h,m = jobs.pop()
                        thread = threading.Thread(target=do_the_stuff,args=(h,m))
        #		thread.daemon = True
                        thread.start()
                else:
                        sleep(0.1)
        # now wait for all daemon threads to end before letting
        # the main thread die. Otherwise stuff will get cut off
        # before it's finished
        while threading.active_count() > 1:
                sleep(0.1)

        print 'ALL JOBS COMPLETED!'

        print("Elapsed time was %g seconds" % (time.time() - start_time))

    else:
        print("No directory "+otp_working_dir)
        print("Moving on to next one")

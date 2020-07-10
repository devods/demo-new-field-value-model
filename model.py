#!/usr/bin/env python3
from dateutil.parser import parse
import fileinput
import argparse
import json
import sys
import datetime
import traceback

def local_log(msg):
    print(msg)
    sys.stdout.flush()

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def send_to_glue(model_stdout, msg):
    try:
        model_stdout.write(json.dumps([msg], default=datetime_handler))
        model_stdout.write('\n')
        model_stdout.flush()
        return True
    except Exception as e:
        local_log('cannot write msg:{} file to /devo/pipes/stdout with error: {}'.format(msg, e))
        return False

def send(model_stdout, msg):
    send_to_glue(model_stdout, msg)
    local_log(msg)

def model_runner(stdin_path, stdout_path, job_id=1000, debug=False):
    try:
        while True:
            with open(stdout_path, "w") as model_stdout:
                roster = {}
                for line in fileinput.input(files=(stdin_path), mode='rU'):
                    try:
                        for row in json.loads(line):
                            if row:
                                try:
                                    eventdate = row['eventdate']
                                    entity_id = row['entityId']
                                    analyzed_field = row['analyzedField']

                                    if entity_id not in roster:
                                        roster[entity_id] = {analyzed_field: eventdate}
                                    else:
                                        visited = roster[entity_id]

                                        # start monitoring from previous 1 day
                                        if analyzed_field not in visited and (datetime.datetime.now()-parse(eventdate)).days <=1:
                                            data = {
                                                    "entity_id": entity_id,
                                                    "new_value": analyzed_field,
                                                    "lastmodifieddate": eventdate
                                            }
                                            # send to devo
                                            send(model_stdout, data)

                                        visited[analyzed_field] = eventdate
                                except Exception as e1:
                                    local_log(traceback.print_exc())
                                    raise Exception(f'{str(e1)}')
                    except Exception as e2:
                        local_log(traceback.print_exc())
                        raise Exception(f'row processing error: {str(e2)}')
    except Exception as e3:
        send(model_stdout, f'{str(e3)}')
        time.sleep(120)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--job_id', default=1000)
    parser.add_argument('--debug', default=False)
    args = parser.parse_args()

    if args.debug:
        args.debug = True if args.debug == "True" else False
    local_log(f'Tracking new field value by entity.')

    model_runner("/devo/pipes/stdin", "/devo/pipes/stdout", args.job_id, args.debug)

import requests
import zipfile
import io
import os
import errno
import sys

def process_timetable(url, dataset_id, out_dir):
    xmls=[]
    save_tt = True and out_dir is not None
    resp = requests.get(url)
    if out_dir is not None:
        try:
            os.mkdir(f"{out_dir}/{dataset_id}")
        except Exception as e:
            if e.errno == errno.EEXIST:
                print(f"{out_dir}/{dataset_id} already exists, not creating")
            else:
                print("Unable to create directory for timetables, will not save")
                save_tt = False

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zfile:
        for zipinfo in zfile.infolist():
            extension = zipinfo.filename.split(".")[-1]
            if extension == "xml":
                with zfile.open(zipinfo.filename) as xmlfile:
                    try:
                        xml = xmlfile.read()
                        if save_tt:
                            with open(f"{out_dir}/{dataset_id}/{zipinfo.filename}", "w") as fp:
                                fp.write(str(xml))
                        xmls.append(xml)
                    except Exception as e:
                        print("Error reading XML:", file=sys.stderr)
                        print(e, file=sys.stderr)



    return xmls

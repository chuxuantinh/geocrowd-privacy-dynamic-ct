import math
import sys
import json
import os
# noinspection PyDeprecation
from sets import Set

import tornado.web
import tornado.ioloop
from tornado_cors import CorsMixin

sys.path.append('.')

sys.path.append('../minball')
sys.path.append('../grid')
sys.path.append('../common')
sys.path.append('../exp')
sys.path.append('../geocast')
sys.path.append('../geocrowd')
sys.path.append('../icde12')

import numpy as np
from Params import Params
from PSDExp import data_readin

from Grid_adaptiveM import Grid_adaptiveM
from GeocastM import geocast, post_geocast
from GeocastLog import geocast_log
from GeocastInfo import GeocastInfo
from Utils import performed_tasks, is_rect_cover, distance_to_rect, rect_area, rect_vertex_set
from smallestenclosingcircle import make_circle


# workerPSD parameters
all_data = {}
tree = []
# datasets = ["yelp", "gowallasf", "gowallala"]
# all_datafiles = {"yelp": "yelp", "gowallasf": "gowalla_SF", "gowallala": "gowalla_LA"}
# datasets2 = ["Yelp_Phoenix", "Gowalla_SF", "Gowalla_LA"]
# areas = [20342, 179, 2373]
# pearson_skewness = [-0.4, 0.18, 0.07]
# spearman_skewness = [0.41, 0.14, 0.26]

datasets = ["yelp", "gowallasf", "gowallala", "foursquare"]
all_datafiles = {"yelp": "yelp", "gowallasf": "gowalla_SF", "gowallala": "gowalla_LA", "foursquare": "Foursquare_PB"}
datasets2 = ["Yelp_Phoenix", "Gowalla_SF", "Gowalla_LA", "Foursquare_PB"]
areas = [20342, 179, 2373, 0]
pearson_skewness = [-0.4, 0.18, 0.07, 0]
spearman_skewness = [0.41, 0.14, 0.26, 0]

boundaries = []
worker_counts = []
MTDs = []

eps = 1
com_range = None

# geocast parameters
mar = None  # maximum acceptance rate
arf = None  # acceptance rate function
utl = None  # utility	
heuristic = None
subcell = None
localness = None
percent = None
constraint = None


class ResetHandler(CorsMixin, tornado.web.RequestHandler):
    # Value for the Access-Control-Allow-Origin header.
    # Default: None (no header).
    CORS_ORIGIN = '*'

    # Value for the Access-Control-Allow-Headers header.
    # Default: None (no header).
    CORS_HEADERS = 'Content-Type'

    # Value for the Access-Control-Allow-Methods header.
    # Default: Methods defined in handler class.
    # None means no header.
    CORS_METHODS = 'GET'

    # Value for the Access-Control-Allow-Credentials header.
    # Default: None (no header).
    # None means no header.
    CORS_CREDENTIALS = True

    # Value for the Access-Control-Max-Age header.
    # Default: 86400.
    # None means no header.
    CORS_MAX_AGE = 21600

    """
    Reset data set 
    http://ubriela.cloudapp.net/reset
    """

    def get(self):
        global tree, eps, all_data, datasets
        print "Reset data``"
        all_data = {}
        for dataset in datasets:
            Params.DATASET = dataset
            p = Params(1000)
            data = data_readin(p)
            eps = p.Eps
            tree = Grid_adaptiveM(data, 1, p)
            tree.buildIndex()
            bounds = np.array([[p.x_min, p.y_min], [p.x_max, p.y_max]])
            all_data[dataset] = (tree, bounds, p.NDATA)


class DatasetHandler(CorsMixin, tornado.web.RequestHandler):
    # Value for the Access-Control-Allow-Origin header.
    # Default: None (no header).
    CORS_ORIGIN = '*'

    # Value for the Access-Control-Allow-Headers header.
    # Default: None (no header).
    CORS_HEADERS = 'Content-Type'

    # Value for the Access-Control-Allow-Methods header.
    # Default: Methods defined in handler class.
    # None means no header.
    CORS_METHODS = 'GET, POST'

    # Value for the Access-Control-Allow-Credentials header.
    # Default: None (no header).
    # None means no header.
    CORS_CREDENTIALS = True

    # Value for the Access-Control-Max-Age header.
    # Default: 86400.
    # None means no header.
    CORS_MAX_AGE = 21600

    def initialize(self):
        global boundaries, datasets, MTDs, worker_counts
        print "dataset init"
        if len(boundaries) == 0:
            for i in range(len(datasets)):
                Params.DATASET = datasets[i]
                p = Params(1000)
                data = data_readin(p)
                p.select_dataset()
                MTDs.append(p.MTD)
                worker_counts.append(p.NDATA)
                boundaries.append(
                    str(p.x_min) + "," + str(p.y_min) + "," + str(p.x_max) + "," + str(p.y_max))

        """
        Return information about datasets
        http://ubriela.cloudapp.net/dataset
        """

    def get(self, url):
        global datasets, datasets2, boundaries, pearson_skewness, MTDs, areas, worker_counts, spearman_skewness

        task = self.get_argument("task", default=None)
        if task is None:
            return

        if task == "info":
            self.write(
                json.dumps({"names": datasets,
                            "names2": datasets2,
                            "boundaries": boundaries,
                            "worker_counts": worker_counts,
                            "mtds": MTDs,
                            "areas": areas,
                            "pearson_skewness": pearson_skewness,
                            "spearman_skewness": spearman_skewness
                           }, sort_keys=True))
        elif task == "data":
            dataset = self.get_argument("dataset", default=None)
            if dataset is not None and dataset in datasets:
                with file("../../dataset/" + all_datafiles[dataset] + ".dat") as f:
                    s = f.read()
                self.write(s)


class GeocastHandler(CorsMixin, tornado.web.RequestHandler):
    # Value for the Access-Control-Allow-Origin header.
    # Default: None (no header).
    CORS_ORIGIN = '*'

    # Value for the Access-Control-Allow-Headers header.
    # Default: None (no header).
    CORS_HEADERS = 'Content-Type'

    # Value for the Access-Control-Allow-Methods header.
    # Default: Methods defined in handler class.
    # None means no header.
    CORS_METHODS = 'GET, POST'

    # Value for the Access-Control-Allow-Credentials header.
    # Default: None (no header).
    # None means no header.
    CORS_CREDENTIALS = True

    # Value for the Access-Control-Max-Age header.
    # Default: 86400.
    # None means no header.
    CORS_MAX_AGE = 21600

    def initialize(self):
        """
        Hook for subclass initialization
        A dictionary passed as the third argument of a url spec will be 
        supplied as keyword arguments to initialize().
        """
        global tree, eps, all_data, datasets
        if len(all_data) == 0:
            for dataset in datasets:
                Params.DATASET = dataset
                p = Params(1000)
                data = data_readin(p)
                eps = p.Eps
                tree = Grid_adaptiveM(data, 1, p)
                tree.buildIndex()
                bounds = np.array([[p.x_min, p.y_min], [p.x_max, p.y_max]])
                all_data[dataset] = (tree, bounds, p.NDATA)

    def prepare(self):
        """
        Called at the beginning of a request before `get`/`post`/etc.
        Override this method to perform common initialization regardless
        of the request method.
        """
        pass

    def on_finish(self):
        """
        Called after the end of a request.
        Override this method to perform cleanup, logging, etc.
        """
        pass

    """
    Response to a geocast query
    
        geocast/gowallasf/37.767712,-122.426834
    """

    def get(self, geocast_id):
        """
        Override the standard GET
        """
        global all_data, eps
        parts = geocast_id.split('/')
        dataset = parts[0]
        print parts
        t = map(float, parts[1].split(','))
        print dataset, t
        # if task not in region
        if not is_rect_cover(all_data[dataset][1], t):
            self.write(json.dumps({"error": "invalid task"}))
            return

        q, q_log = geocast(all_data[dataset][0], t, float(eps))
        no_workers, workers, Cells, no_hops, coverage, no_hops2 = post_geocast(t, q, q_log)
        performed, worker, dist = performed_tasks(workers, Params.MTD, t, True)
        x_min, y_min, x_max, y_max = [], [], [], []
        worker_counts, utilities, distances, compactnesses, areas = [], [], [], [], []
        if worker is not None:
            worker = worker.tolist()

        corner_points = Set([])
        for cell in Cells:
            x_min.append(cell[0].n_box[0][0])
            y_min.append(cell[0].n_box[0][1])
            x_max.append(cell[0].n_box[1][0])
            y_max.append(cell[0].n_box[1][1])
            worker_counts.append(cell[0].n_count)
            utilities.append([cell[2][1], cell[2][2]])
            compactnesses.append(cell[2][3])
            distances.append(float("%.3f" % distance_to_rect(t[0], t[1], cell[0].n_box)))
            distances.append(float("%.3f" % distance_to_rect(t[0], t[1], cell[0].n_box)))
            areas.append(float("%.3f" % rect_area(cell[0].n_box)))
            corner_points = corner_points | rect_vertex_set(cell[0].n_box)

        points = list(corner_points)
        x = make_circle(points)
        if x is not None:
            cx, cy, r = x
            print cx, cy, r
        else:
            cx, cy, r = 0, 0, 0
        no_hops2 = math.ceil(no_hops2)
        if performed:
            self.write(
                json.dumps({"is_performed": performed,
                            "notified_workers": {"no_workers": no_workers,
                                                 "x_coords": workers[0].tolist(),
                                                 "y_coords": workers[1].tolist()},
                            "geocast_query": {"no_cell": len(Cells),
                                              "compactness": q_log[-1][3],
                                              "x_min_coords": x_min,
                                              "y_min_coords": y_min,
                                              "x_max_coords": x_max,
                                              "y_max_coords": y_max,
                                              "worker_counts": worker_counts,
                                              "utilities": utilities,
                                              "compactnesses": compactnesses,
                                              "distances": distances,
                                              "areas": areas},
                            "spatial_task": {"location": t},
                            "volunteer_worker": {"location": worker,
                                                 "distance": dist},
                            "hop_count": no_hops2,
                            "bounding_circle": [cx, cy, r]},
                           sort_keys=False)
            )
        else:
            self.write(
                json.dumps({"is_performed": False,
                            "notified_workers": {"no_workers": no_workers,
                                                 "x_coords": workers[0].tolist(),
                                                 "y_coords": workers[1].tolist()},
                            "geocast_query": {"no_cell": len(Cells),
                                              "x_min_coords": x_min,
                                              "y_min_coords": y_min,
                                              "x_max_coords": x_max,
                                              "y_max_coords": y_max,
                                              "worker_counts": worker_counts,
                                              "utilities": utilities,
                                              "compactnesses": compactnesses,
                                              "distances": distances,
                                              "areas": areas},
                            "spatial_task": {"location": t},
                            "volunteer_worker": {"location": worker,
                                                 "distance": dist},
                            "hop_count": no_hops2,
                            "bounding_circle": [cx, cy, r]},
                           sort_keys=False)
            )


        # logging
        if Params.GEOCAST_LOG:
            info = GeocastInfo(int(performed), t, Cells)
            log_str = str(info.logging()) + "\n"
            geocast_log("geocast_server", log_str, eps)


class ParamHandler(CorsMixin, tornado.web.RequestHandler):
    # Value for the Access-Control-Allow-Origin header.
    # Default: None (no header).
    CORS_ORIGIN = '*'

    # Value for the Access-Control-Allow-Headers header.
    # Default: None (no header).
    CORS_HEADERS = 'Content-Type'

    # Value for the Access-Control-Allow-Methods header.
    # Default: Methods defined in handler class.
    # None means no header.
    CORS_METHODS = 'POST'

    # Value for the Access-Control-Allow-Credentials header.
    # Default: None (no header).
    # None means no header.
    CORS_CREDENTIALS = True

    # Value for the Access-Control-Max-Age header.
    # Default: 86400.
    # None means no header.
    CORS_MAX_AGE = 21600

    """
    Set parameters at server
	/param/?dataset=yelp&eps=1.0&percent=0.4&localness=false&rebuild=0
    """

    def get(self, param_id):
        """
        Update geocast parameters
        """
        global datasets, tree, all_data
        global eps, percent, com_range, mar, arf, utl, heuristic, subcell, localness, constraint
        dataset = self.get_argument("dataset", default=Params.DATASET)
        eps = self.get_argument("eps", default=eps)
        percent = self.get_argument("percent", default=Params.PercentGrid)
        com_range = self.get_argument("range", default=Params.NETWORK_DIAMETER)

        # geocast parameters
        mar = self.get_argument("mar", default=Params.MAR)
        arf = self.get_argument("arf", default=Params.AR_FUNCTION)
        utl = self.get_argument("utl", default=Params.U)
        heuristic = self.get_argument("heuristic", default=Params.COST_FUNCTION)
        subcell = self.get_argument("subcell", default=Params.PARTIAL_CELL_SELECTION)
        localness = self.get_argument("localness", default=Params.CUSTOMIZED_GRANULARITY)
        constraint = self.get_argument("constraint", default=Params.CONSTRAINT_INFERENCE)

        Params.DATASET = dataset
        Params.Eps = float(eps)
        Params.PercentGrid = float(percent)
        Params.NETWORK_DIAMETER = float(com_range) / 1000.0
        Params.MAR = float(mar)
        Params.AR_FUNCTION = arf
        Params.U = float(utl)
        Params.COST_FUNCTION = heuristic
        Params.PARTIAL_CELL_SELECTION = (subcell == "true" or subcell == True)
        Params.CUSTOMIZED_GRANULARITY = (localness == "true" or localness == True)
        Params.CONSTRAINT_INFERENCE = constraint == "true"
        print "Update parameters ... "
        print Params.DATASET, Params.Eps, Params.PercentGrid, Params.NETWORK_DIAMETER, Params.MAR, Params.AR_FUNCTION, Params.U, Params.COST_FUNCTION, Params.PARTIAL_CELL_SELECTION, Params.CUSTOMIZED_GRANULARITY

        # workerPSD parameters
        rebuild = self.get_argument("rebuild", default=0)
        rebuild = int(rebuild)
        if rebuild == 1:
            print "Reading data ... " + dataset
            p = Params(1000)
            data = data_readin(p)
            print "Creating WorkerPSD..."
            tree = Grid_adaptiveM(data, 1, p)
            tree.buildIndex()
            bounds = np.array([[p.x_min, p.y_min], [p.x_max, p.y_max]])
            all_data[dataset] = (tree, bounds, p.NDATA)
            print "Created WorkerPSD..." + dataset

        self.write(
            json.dumps({"status": "update successfully"}, sort_keys=True))


"""
Update data set
"""


class UpdateHandler(CorsMixin, tornado.web.RequestHandler):
    # Value for the Access-Control-Allow-Origin header.
    # Default: None (no header).
    CORS_ORIGIN = '*'

    # Value for the Access-Control-Allow-Headers header.
    # Default: None (no header).
    CORS_HEADERS = 'Content-Type'

    # Value for the Access-Control-Allow-Methods header.
    # Default: Methods defined in handler class.
    # None means no header.
    CORS_METHODS = 'GET, PUT, POST, HEAD, DELETE'

    # Value for the Access-Control-Allow-Credentials header.
    # Default: None (no header).
    # None means no header.
    CORS_CREDENTIALS = True

    # Value for the Access-Control-Max-Age header.
    # Default: 86400.
    # None means no header.
    CORS_MAX_AGE = 21600

    """
    Set parameters at server
	/update/?data=xxxx
    """

    def post(self, param_id):
        """
        Update geocast parameters
        """
        global datasets, tree, all_data
        global eps, percent, com_range, mar, arf, utl, heuristic, subcell, localness, constraint
        workers = tornado.escape.json_decode(self.request.body)

        # print simplejson.dumps(workers)

        # np.fromiter(json.loads(workers),dtype)

        # save data to a file
        # tmp_workers_file = "../../dataset/tmp_workers_file.dat"

        # data = np.genfromtxt("../../dataset/yelp.dat",unpack = True)

        print "Start updating worker locations"
        i = 0
        all_workers = []
        for worker in workers:
            i += 1
            if i % 1000 == 0:
                print "Updated ", i, " workers"
            pair = [worker['k'], worker['B']]
            all_workers.append(pair)
            data = np.array(all_workers)
            np.savetxt('../../dataset/update.txt', data, delimiter='\t')
            data = data.transpose()
        Params.NDIM, Params.NDATA = data.shape[0], data.shape[1]

        Params.LOW, Params.HIGH = np.amin(data, axis=1), np.amax(data, axis=1)
        print Params.NDIM, Params.NDATA
        print Params.LOW, Params.HIGH

        p = Params(1000)
        print "Creating WorkerPSD..."
        dataset = self.get_argument("dataset", default=Params.DATASET)
        Params.DATASET = dataset
        p.select_dataset()
        print dataset
        tree = Grid_adaptiveM(data, 1, p)
        tree.buildIndex()
        bounds = np.array([[Params.x_min, Params.y_min], [Params.x_max, Params.y_max]])
        print bounds
        all_data[dataset] = (tree, bounds, p.NDATA)

        self.write(
            json.dumps({"status": "update successfully"}, sort_keys=True))


class MyFormHandler(tornado.web.RequestHandler):
    def get(self, test_id):
        self.write("You requested the main page ")
        self.write("Page: " + test_id)
        self.write("\nParameter: " + self.get_argument("param"))

    def post(self):
        """
        Override the standard POST
        """
        self.set_header("Content-Type", "text/plain")
        self.write("You wrote " + self.get_argument("message"))


__UPLOADS__ = "../../dataset/"


class Userform(tornado.web.RequestHandler):
    def get(self):
        self.render("fileuploadform.html")


class Upload(CorsMixin, tornado.web.RequestHandler):
    # Value for the Access-Control-Allow-Origin header.
    # Default: None (no header).
    CORS_ORIGIN = '*'

    # Value for the Access-Control-Allow-Headers header.
    # Default: None (no header).
    CORS_HEADERS = 'Content-Type'

    # Value for the Access-Control-Allow-Methods header.
    # Default: Methods defined in handler class.
    # None means no header.
    CORS_METHODS = 'GET, PUT, POST, HEAD, DELETE'

    # Value for the Access-Control-Allow-Credentials header.
    # Default: None (no header).
    # None means no header.
    CORS_CREDENTIALS = True

    # Value for the Access-Control-Max-Age header.
    # Default: 86400.
    # None means no header.
    CORS_MAX_AGE = 21600

    def post(self):
        global all_data, datasets, datasets2, boundaries, MTDs, worker_counts, all_datafiles, pearson_skewness, areas, spearman_skewness

        fileinfo = self.request.files['dataset'][0]
        print "fileinfo is", fileinfo
        fname = fileinfo['filename']
        fname = os.path.splitext(fname)[0]
        # cname = str(uuid.uuid4()) + extn
        cname = fname
        fh = open(__UPLOADS__ + cname, 'w')
        fh.write(fileinfo['body'])

        # update variables
        datasets.append(fname)
        datasets2.append(fname)
        all_datafiles[fname] = fname

        Params.DATASET = fname + '.dat'
        p = Params(1000)
        data = data_readin(p)
        eps = p.Eps
        tree = Grid_adaptiveM(data, 1, p)
        tree.buildIndex()
        bounds = np.array([[Params.LOW[0], Params.LOW[1]], [Params.HIGH[0], Params.HIGH[1]]])

        MTDs.append(Params.MTD)
        worker_counts.append(p.NDATA)
        pearson_skewness.append(0)
        areas.append(0)
        spearman_skewness.append(0)
        boundaries.append(
            str(Params.LOW[0]) + "," + str(Params.LOW[1]) + "," + str(Params.HIGH[0]) + "," + str(Params.HIGH[1]))

        all_data[fname] = (tree, bounds, data)

        self.finish(Params.DATASET + " is uploaded to the server. Its PSD is constructed.")


application = tornado.web.Application([
                                          (r"/test/(.*)", MyFormHandler),
                                          (r"/geocast/([/,0-9,-.a-z]+)", GeocastHandler),
                                          (r"/dataset/(.*)", DatasetHandler),
                                          (r"/param/(.*)", ParamHandler),
                                          (r"/update/(.*)", UpdateHandler),
                                          (r"/reset", ResetHandler),
                                          (r"/", Userform),
                                          (r"/upload", Upload),
                                      ], debug=True)

if __name__ == "__main__":
    # An I/O event loop for non-blocking sockets.
    print "PSD Server started"
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()

import math
# # Basic parameters
class Params(object):
    """
    Class level variables
    """
    # dataset, x_min, y_min, x_max, y_max = None, None, None, None, None
    # NDATA = None
    # NDIM = None
    # LOW = None
    #    HIGH = None

    SRT = 0.01  # sampling rate
    nQuery = 50  # number of queries
    maxHeight = 8  # maximum tree height, for kdtrees and quadtrees
    unitGrid = 0.01  # cell unit in kd-cell

    # Common parameters
    WorstCase = False  # worst case in selectivity estimation
    Hx = 4  # max query height
    queryUnit = [10, 10]
    LevelExpansion = True

    # HTree
    maxHeightHTree = 2  # = 4 for ht-composite and ht-hybrid
    partitionsHTree = [64, 64]  # m,m
    switchPartitionsHTree = [8, 8]  # m2,m2
    PercentSplit = 0.4  # budget allocated for split
    minPartSizeHTree = 2 ** 5  # maximum number of data points in a leaf node
    maxRelativeError = .95  # maximum error allowed in median selection
    dynamicGranularity = False  # automatically compute granularity for htree
    c_htree = 1
    useLeafOnlyHTree = True

    # Grid (the parameter setting is recommended in ICDE'13)
    PercentGrid = 0.5  # budget allocated for first level, used for adaptive grid
    PercentGridLocalness = 0.3
    m = partitionsHTree[1]  # grid size, computed in Grid_uniform
    c = 10  # the smaller c, the higher first-level granunality
    c2 = 5  # the smaller c2, the higher second-level granunality
    c2_c = math.sqrt(2)  # customized c2

    ONE_KM = 0.0089982311916  # convert km to degree

    CUSTOMIZED_GRANULARITY = True  # apply for adaptive grid
    PARTIAL_CELL_SELECTION = True  # allow select a sub-region of a cell
    CONSTRAINT_INFERENCE = True

    maxHeightAdaptiveGrid = 2
    NEGATIVE_CELL = False  # couting cells with negative count into geocast query
    ZIPF_STEPS = 100
    s = 1  # the value of the exponent characterizing the zipf distribution
    GAMMA = 0.9  # level expansion parameter
    LEVEL_EXPANSION = False
    GEOCAST_LOG = False
    LOGGING_STEPS = 200
    FIX_GRANULARITY = False  # apply for first level of adaptive grid
    PARTITION_AG = [9, 9]
    ALPHA = 0.3  # the larger alpha the more important compactness
    ALGO = "greedy"

    # ## Geocast algorithm
    # Variables
    COST_FUNCTION = "hybrid"  # "utility", "hybrid", "compactness", "distance"
    MAR = 0.1
    U = 0.9  # Utility
    NETWORK_DIAMETER = 0.05  # kme
    TASK_NO = 100  # tasks per instance
    DATASET, AR_FUNCTION = "yelp", "linear"
    K = 1

    # multiple time instances
    samplingRate = 0.25  # 2%
    MTD = 5.0  # kms, mtd depends on dataset
    dataset_task = ""
    TASKPATH = ""
    dataset = ""

    def setData(self, param):
        self = param

    #        self.dataset, self.x_min, self.y_min, self.x_max, self.y_max = param.dataset, param.x_min, param.y_min, param.x_max, param.y_max
    #        self.TASKPATH = param.TASKPATH
    #        self.MTD = param.MTD
    #        self.resdir = param.resdir
    #
    #        self.NDATA = param.NDATA
    #        self.NDIM = param.NDIM
    #        self.LOW = param.LOW
    #        self.HIGH = param.HIGH

    def debug(self):
        print Params.dataset, Params.TASKPATH, Params.MTD, self.resdir
        print self.x_min, self.y_min, self.x_max, self.y_max
        print self.NDATA, self.NDIM, self.LOW, self.HIGH

    # This parameter setting is of the same as ICDE'12
    def __init__(self, seed):
        self.resdir = ""
        self.x_min, self.y_min, self.x_max, self.y_max = None, None, None, None
        self.NDATA = None
        self.NDIM = None
        self.LOW = None
        self.HIGH = None

        self.structureEps = 0.1  # 50%
        self.Eps = 0.5  # epsilon
        self.Seed = seed  # used in generating noisy counts
        self.minPartSize = 2  # maximum number of data points in a leaf node
        self.Percent = 0.3  # budget allocated for split
        self.switchLevel = 3  # switch level for hybrid tree
        self.Res = 18  # Hilbert-R tree resolution
        self.useLeafOnly = False  # only True for kd-cell and kd-noisymean
        self.cellDistance = 40  # threshold to test uniformity in kd-cell

        # self.geoBudget = 'none' # uniform budgeting
        # self.geoBudget = 'aggressive' # geometric exponent i
        # self.geoBudget = 'quadratic' # geometric exponent i/2
        self.geoBudget = 'optimal'  # geometric exponent i/3
        # self.geoBudget = 'quartic' # geometric exponent i/4

        self.splitScheme = 'expo'  # exponential mechanism

        # self.splitScheme = 'noisyMean' # noisy mean approximation

    def select_dataset(self):
        if Params.DATASET == "gowallasf":
            if Params.AR_FUNCTION == "linear":
                self.resdir = '../../output/gowalla_sf/'
            else:
                self.resdir = '../../output/gowalla_sf_zipf/'

            Params.dataset = '../../dataset/gowalla_SF.dat'
            # Params.dataset_task = '../../dataset/gowalla_SF.dat'
            Params.dataset_task = '../../dataset/gowalla_SF_task.dat'
            Params.MTD = 5
            Params.TASKPATH = '../log/gowalla_sf_tasks.dat'
            self.x_min = 37.71127146
            self.y_min = -122.51350164
            self.x_max = 37.83266118
            self.y_max = -122.3627126
        elif Params.DATASET == "gowallala":
            if Params.AR_FUNCTION == "linear":
                Params.resdir = '../../output/gowalla_la/'
            else:
                Params.resdir = '../../output/gowalla_la_zipf/'
            Params.dataset = '../../dataset/gowalla_la.dat'
            Params.dataset_task = '../../dataset/gowalla_la_task.dat'
            Params.MTD = 13.6
            Params.TASKPATH = '../log/gowalla_la_tasks.dat'
            Params.x_min = 33.699476
            Params.y_min = -118.570633
            Params.x_max = 34.319887
            Params.y_max = -118.192978
        elif Params.DATASET == "yelp":
            if Params.AR_FUNCTION == "linear":
                self.resdir = '../../output/yelp/'
            else:
                self.resdir = '../../output/yelp_zipf/'
            Params.dataset = '../../dataset/yelp.dat'
            Params.dataset_task = '../../dataset/yelp_task.dat'
            # Params.MTD = 3.5
            Params.MTD = 5
            Params.TASKPATH = '../log/yelp_tasks.dat'

            self.x_min = 32.8768481
            self.y_min = -112.875481
            self.x_max = 33.806805
            self.y_max = -111.671219
        elif Params.DATASET == "foursquare":
            if Params.AR_FUNCTION == "linear":
                self.resdir = '../../output/foursquare/'
            else:
                self.resdir = '../../output/foursquare_zipf/'
            Params.dataset = '../../dataset/foursquare_PB.dat'
            Params.dataset_task = '../../dataset/foursquare_PB.dat'
            Params.MTD = 5
            Params.TASKPATH = '../log/foursquare_tasks.dat'
            self.x_min = 40.084029918076254
            self.y_min = -80.422608999999994
            self.x_max = 40.750032220137363
            self.y_max = -79.520651000000001
        elif Params.DATASET == "test":
            Params.resdir = '../../output/test/'
            Params.dataset = '../../dataset/gowalla_SF.dat'
            Params.dataset_task = '../../dataset/gowalla_SF.dat'
            # Params.dataset_task = '../../dataset/gowalla_SF_task.dat'
            Params.MTD = 3.6
            Params.TASKPATH = '../log/test_tasks.dat'
            Params.x_min = 37.71127146
            Params.y_min = -122.51350164
            Params.x_max = 37.83266118
            Params.y_max = -122.3627126
        elif Params.DATASET == "mcdonald":
            Params.dataset = '../../dataset/mcdonald.dat'
            Params.dataset_task = '../../dataset/mcdonald.dat'
            Params.resdir = '../../output/mcdonald/'
            Params.x_min = 32.1714
            Params.y_min = -124.3041
            Params.x_max = 64.8490
            Params.y_max = -67.2804  # mcdonald
        elif Params.DATASET == "gowalla_ca":
            Params.dataset = '../../dataset/gowalla_CA.dat'
            Params.resdir = '../../output/gowalla_ca/'
            Params.x_min = -124.3041
            Params.y_min = 32.1714
            Params.x_max = -114.0043
            Params.y_max = 41.9984  # gowalla_CA
        elif Params.DATASET == "tiger":
            Params.dataset = '../../dataset/tiger_NMWA.dat'
            Params.resdir = '../../output/tiger/'
            Params.x_min = -124.8193
            Params.y_min = 31.3322
            Params.x_max = -103.0020
            Params.y_max = 49.0025  # tiger
        elif Params.DATASET == "landmark":
            Params.dataset = '../../dataset/landmark.dat'
            Params.resdir = '../../output/landmark/'
            Params.x_min = -124.4384
            Params.y_min = 24.5526
            Params.x_max = -67.0255
            Params.y_max = 49.0016  # landmark
        elif Params.DATASET == "restrnts":
            Params.dataset = '../../dataset/restrnts.dat'
            Params.resdir = '../../output/restrnts/'
            Params.x_min = -124.4972
            Params.y_min = 24.5473
            Params.x_max = -66.9844
            Params.y_max = 48.9999  # restrnts
        elif Params.DATASET == "shopping":
            Params.dataset = '../../dataset/shopping.dat'
            Params.resdir = '../../output/shopping/'
            Params.x_min = -124.2640
            Params.y_min = 24.5515
            Params.x_max = -68.2106
            Params.y_max = 48.9939  # shopping
        elif Params.DATASET == "parkrec":
            Params.dataset = '../../dataset/parkrec.dat'
            Params.resdir = '../../output/parkrec/'
            Params.x_min = -124.5249
            Params.y_min = 24.5510
            Params.x_max = -66.9687
            Params.y_max = 49.0010  # parkrec
        elif Params.DATASET == "zipcode":
            Params.dataset = '../../dataset/zipcode.dat'
            Params.resdir = '../../output/zipcode/'
            Params.x_min = -176.6368
            Params.y_min = 17.9622
            Params.x_max = -65.2926
            Params.y_max = 71.2995  # zipcode
        elif Params.DATASET == "truck":
            Params.dataset = '../../dataset/truck.dat'
            Params.resdir = '../../output/truck/'
            Params.x_min = 23.5100
            Params.y_min = 37.8103
            Params.x_max = 24.0178
            Params.y_max = 38.2966  # truck
        elif Params.DATASET == "ne":
            Params.dataset = '../../dataset/ne.dat'
            Params.resdir = '../../output/ne/'
            Params.x_min = 0.0470
            Params.y_min = 0.0543
            Params.x_max = 0.9530
            Params.y_max = 0.9457  # ne
        elif Params.DATASET == "na":
            Params.dataset = '../../dataset/na.dat'
            Params.resdir = '../../output/na/'
            Params.x_min = -174.2057
            Params.y_min = 14.6805
            Params.x_max = -52.7316
            Params.y_max = 79.9842  # na
        elif Params.DATASET == "buses":
            Params.dataset = '../../dataset/buses.dat'
            Params.resdir = '../../output/buses/'
            Params.x_min = 22.3331
            Params.y_min = 37.8329
            Params.x_max = 24.0203
            Params.y_max = 38.7417  # buses
        elif Params.DATASET == "gowalla_sa":
            Params.dataset = '../../dataset/gowalla_SA.dat'
            Params.resdir = '../../output/gowalla_sa/'
            Params.x_min = -63.3209
            Params.y_min = -176.3086
            Params.x_max = 13.5330
            Params.y_max = -32.4150  # gowalla_SA
        elif Params.DATASET == "brightkite":
            Params.dataset = '../../dataset/brightkite.dat'
            Params.resdir = '../../output/brightkite/'
            Params.x_min = -94.5786
            Params.y_min = -179.1541
            Params.x_max = 90
            Params.y_max = 178  # brightkite
        else:  # new dataset
            Params.dataset = '../../dataset/' + Params.DATASET
            Params.MTD = 10
            # Params.x_min=37.71127146 ; Params.y_min=-122.51350164; Params.x_max=37.83266118; Params.y_max=-122.3627126
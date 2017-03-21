# -*- coding: utf-8 -*-

import os

from osgeo import gdal

from qgis.core import QgsFeatureRequest


class Points:

    def __init__(self, layer):
        self.layer = layer
        self.data = dict()
        self.maxSearchRadius = 0.0

    def loadData(self, boundingBox, pixelSize, searchRadius, observerHeight, targetHeight, idField=None):
        xMin = boundingBox.xMinimum()
        yMax = boundingBox.yMaximum()

        self.maxSearchRadius = searchRadius / pixelSize

        # if passed searchRadius, observerHeight, targetHeight and
        # idField are strings, we assume that they are field names
        # and add fetch them. Otherwise only feature geometry will
        # be fetched.
        attrs = []
        provider = self.layer.dataProvider()
        if idField is not None:
            idx = provider.fieldNameIndex(idField)
            if idx != -1:
                attrs.append(idx)

        if isinstance(observerHeight, str):
            idx = provider.fieldNameIndex(observerHeight)
            if idx != -1:
                attrs.append(idx)

        if isinstance(targetHeight, str):
            idx = provider.fieldNameIndex(targetHeight)
            if idx != -1:
                attrs.append(idx)

        if isinstance(searchRadius, str):
            idx = provider.fieldNameIndex(searchRadius)
            if idx != -1:
                attrs.append(idx)

        request = QgsFeatureRequest()
        request.setFilterRect(boundingBox)
        request.setSubsetOfAttributes(attrs)
        for f in self.layer.getFeatures(request):
            p = f.geometry().asPoint()

            # pixel coordinates
            x = int((p.x() - xMin) / pixelSize)
            y = int((yMax - p.y()) / pixelSize)

            # retrieve other attributes
            if idField is not None:
                fid = f[idField]
            else:
                fid = f.id()

            if isinstance(observerHeight, str):
                zObserver = f[observerHeight]
            else:
                zObserver = observerHeight

            if isinstance(targetHeight, str):
                zTarget = f[targetHeight]
            else:
                zTarget = targetHeight

            if isinstance(searchRadius, str):
                try:
                    r = float(f[searchRadius]) / pixelSize
                    if r > self.maxSearchRadius:
                        self.maxSearchRadius = r
                except:
                    r = self.maxSearchRadius

            self.data[fid] = {"p": p,
                              "x": x,
                              "y": y,
                              "zObserver": zObserver,
                              "zTarget": zTarget,
                              "searchRadius": r}


def _ellipsoid(layer):
    """Extract ellipsoid parameters from the layer CRS
    """
    crs = layer.crs().toWkt()
    start = crs.find("SPHEROID") + len("SPHEROID[")
    end = crs.find("]],", start) + 1
    tmp = crs[start:end].split(",")

    try:
        semiMajor = float(tmp[1])
        if not 6000000 < semiMajor < 7000000:
            semiMajor = 6378137
    except:
        semiMajor = 6378137

    try:
        flattening = float(tmp[2])
        if not 296 < flattening < 301:
            flattening = 298.257223563
    except:
        flattening = 298.257223563

    semiMinor = semiMajor - semiMajor / flattening
    diameter = semiMajor + semiMinor

    return {"semiMajor": semiMajor,
            "semiMinor": semiMinor,
            "flattening": flattening,
            "diameter": diameter}


def writeRaster(filePath, matrix, xOffset, yOffset, srcDs, dataFormat):
    """Helper function which writes given matrix as new raster file using
    metadata from the given raster dataset.
    """
    driver = gdal.GetDriverByName('GTiff')
    ds = driver.Create(filePath, srcDs.RasterXSize, srcDs.RasterYSize, 1, dataFormat)
    ds.SetProjection(srcDs.GetProjection())
    ds.SetGeoTransform(srcDs.GetGeoTransform())

    ds.GetRasterBand(1).Fill(numpy.nan)
    ds.GetRasterBand(1).SetNoDataValue(numpy.nan)
    ds.GetRasterBand(1).WriteArray(matrix, xOffset, yOffset)

    ds = None


def errorMatrix(radius, size_factor=1):
    """Create a set of lines of sight which can be reused for all
    calculations. Each line (departing from the observer point) has
    its target and a set of pixels it passes through. Only 1/8th of
    full radius is enough: the rest can be copied/mirrored.
    """

    if size_factor == 0:
        size_factor = 1

    radius_large = radius * size_factor

    mx_index = numpy.zeros((radius_large + 1, radius, 2)).astype(int)
    mx_err = numpy.zeros((radius_large + 1, radius))
    mx_mask = numpy.zeros(mx_err.shape).astype(bool)

    min_err = {}

    # keep 0 line empty
    j = 0
    # 45 deg line is added (+1)
    for m in range(radius_large + 1):
        x_f = radius
        y_f = radius

        # dy = x; dx = y
        # FIXME: swapped x and y. Messy
        dy = m
        dx = radius_large

        # x and y = delta x and y but y is steep.
        # fist line is min y then it ascends till 45°
        d = 0
        # restrict iteration to actual radius
        for i in range(radius):
            x_f += 1
            if 2 * (d + dy) < dx:
                d += dy # y_f remains
            else:
                y_f += 1
                d += dy - dx

            # reverse x and y for data array
            yx = (y_f, x_f)
            mx_index[j, i, 0:2] = yx

            if d:
                e = d/dx
                err=abs(e)
            else:
                e = 0.0
                err = 0.0

            mx_err[j, i]=e

            # keep pixel dictionary to sort out best pixels
            try:
                err_old = min_err[yx][0]
                if err < err_old:
                    min_err[yx] = [err, j, i]
            except:
                min_err[yx] = [err, j, i]

        j += 1

    # check-out minimum errors
    for key in min_err:
        ix = min_err[key][1:3]
        er = min_err[key][0]
        mx_mask[ix[0], ix[1]] = 1

    # take the best pixels
    # cannot simply use indices as pairs [[x,y], [...]] - numpy thing...
    # cannot use mx : has a lot of duplicate indices
    mx_err_dir = numpy.where(mx_err > 0, 1, -1)
    mx_err_dir[mx_err == 0] = 0

    # we do not need negative errors any more
    mx_err_index = mx_index [:, :, 0] + mx_err_dir

    return mx_index, mx_err_index, numpy.absolute(mx_err), mx_mask


def readRaster(dataset, x, y, radius_pix, square=True):
    """Read chunck of data from the given raster dataset.
    """
    raster_y_size = dataset.RasterYSize
    raster_x_size = dataset.RasterXSize

    if x <= radius_pix:
        # cropping from the front
        x_offset = 0
        x_offset_dist_mx = radius_pix - x
    else:
        # cropping from the back
        x_offset = x - radius_pix
        x_offset_dist_mx = 0

    x_offset2 = min(x + radius_pix + 1, dataset.RasterXSize)

    if y <= radius_pix:
        y_offset = 0
        y_offset_dist_mx = radius_pix - y
    else:
        y_offset = y - radius_pix
        y_offset_dist_mx = 0

    y_offset2 = min(y + radius_pix + 1, dataset.RasterYSize)

    window_size_y = y_offset2 - y_offset
    window_size_x = x_offset2 - x_offset

    if square:
        full_size = radius_pix * 2 + 1
        mx = numpy.zeros((full_size, full_size))

        mx[y_offset_dist_mx : y_offset_dist_mx + window_size_y,
           x_offset_dist_mx : x_offset_dist_mx + window_size_x] = dataset.ReadAsArray(x_offset, y_offset, window_size_x, window_size_y).astype(float)
    else:
        mx = dataset.ReadAsArray(x_offset, y_offset, window_size_x, window_size_y).astype(float)

    return mx, (x_offset, y_offset, x_offset_dist_mx, y_offset_dist_mx, window_size_x, window_size_y)


def calculateViewshed(data, error_matrix, error_mask, indices, indices_interpolation, analysisType, target_matrix=None, precision=1):
    """ Calculate viewsed for single point.
    Works on a number of precalculated matrices for speed. Takes
    prepared errors and indices of best pixels (with least offset from
    the line of sight). Cannot be much simplified (?) - without loosing
    speed...
    Note that only 1/8 of the entire analysed zone is enough for
    interpolation etc, the rest is filled by flipping arrays.
    """
    # TODO: np.take is  much more efficient than using "fancy" indexing
    # (stackoverflow says)... but it flattens arrays.
    # ones so that the centre gets True val
    mx_vis = numpy.ones(data.shape)

    mx = indices[:, :, 1]
    my = indices[:, :, 0]

    me_x = mx
    me_y = indices_interpolation

    for steep in [False, True]:
        if steep:
            # swap x and y
            # actually, me_x = mx, but unswapped
            me_x, me_y = me_y , me_x
            mx, my = my, mx

        for quad in [1, 2, 3, 4]:
            # cca 700 nanosec per view - not that expensive...
            # otherwise all possible indices can be precalculated
            # = some 12 matrices for x, y & err, which is ugly
            # or calculate 'on the fly', but this could be expensive
            #
            # TODO 3 * 2D matrix (3Ds are slower than 2D (eg. sorting))
            # or try: flipping only axes x and y, not 4 quads = 3 options(?)
            # if rev x: flip 1 (over [:])
            # if rev_y: flip 2 (over second flip)
            # speed?
            if quad == 1:
                view = data[:]
                view_o = mx_vis[:]
                if target_matrix is not None:
                    view_tg = target_matrix[:]
            elif quad == 4:
                view_o = mx_vis[:, ::-1]
                # y flip
                view = data[:, ::-1]
                if target_matrix is not None:
                    view_tg = target_matrix[:, ::-1]
            elif quad == 2:
                # x flip
                view = data [::-1, :]
                view_o = mx_vis[::-1, :]
                if target_matrix is not None:
                    view_tg = target_matrix[::-1, :]
            else:
                view = data[::-1, ::-1]
                view_o = mx_vis[::-1, ::-1]
                if target_matrix is not None:
                    view_tg = target_matrix[::-1, ::-1]

            interp = view[mx, my]

            if precision > 0:
                # do interpolation
                interp += (view[me_x, me_y] - interp) * error_matrix

            # do it here so we can subsitute target below
            test_val = numpy.maximum.accumulate(interp, axis=1)

            if target_matrix is not None:
                # substitute target matrix, but only after test matrix
                # is calculated
                interp = view_tg[mx, my]

                if precision > 0:
                    # could be done only on "good pixels", those with
                    # minimal error!
                    # use mask on mx, my etc - test for speed...
                    interp += (view_tg[me_x, me_y] - interp) * error_matrix

            if analysisType == BINARY_VIEWSHED:
                # if it's True/False raster then False is written as
                # NoData by gdal (i.e. nothing is written)
                v = interp >= test_val
            elif analysisType == INVISIBILITY_DEPTH:
                v = interp - test_val
            elif analysisType == ANGULAR_SIZE:
                # This is INEFFICIENT
                v = numpy.zeros(interp.shape)
                v[:, 1:] = numpy.diff(test_val)
            elif analysisType == HORIZON:
                v = interp >= test_val
                # to avoid confusion because of hidden corners
                # problematic : cannot be un-masked for rectangular output
                v[view_d >= radius_pix + 2] = False

                # select last pixel (find max value in a reversed array (last axis!)
                # argmax stops at first occurence
                # indices have to be re-reversed
                # gives a flat array of 1 index for each row (axis=1)
                rev_max = radius_pix - numpy.argmax(v[:, ::-1], axis=1) - 1
                v[:] = False

                # radius = row n° for fancy index (should be some nicer way...)
                v[numpy.arange(radius_pix + 1), rev_max.flat] = True
                # artifacts at borders (false horizons)
                # (all matrix edges are marked as horizon - if visibilty
                # zone gets cut off there)
                v[:, -1] = 0

            # view of mx_vis, NOT A COPY!
            view_o[mx[error_mask], my[error_mask]] = v[error_mask]

    return mx_vis


def viewshed(dem, observer, observerHeight, targetHeight, searchRadius, useEarthCurvature, refraction, analysisType, precision, outputPath):
    """
    """
    dsDem = gdal.Open(dem.source(), gdal.GA_ReadOnly)
    geoTransform = dsDem.GetGeoTransform()
    pix = geoTransform[1]
    rasterXMin = geoTransform[0]
    rasterYMax = geoTransform[3]

    rasterYMin = rasterYMax - dsDem.RasterYSize * pix
    rasterXMax = rasterXMin + dsDem.RasterXSize * pix

    p = Points(observer)
    p.loadData(dem.extent(), pix, searchRadius, observerHeight, targetHeight)
    points = p.data

    radius_pix = int(p.maxSearchRadius)

    # pre_calculate distance matrix
    full_window_size = radius_pix * 2 + 1

    temp_x = ((numpy.arange(full_window_size) - radius_pix)) ** 2
    temp_y = ((numpy.arange(full_window_size) - radius_pix)) ** 2
    mx_dist = numpy.sqrt(temp_x[:, None] + temp_y[None, :])

    if useEarthCurvature:
        ellipsoid = _ellipsoid(dem)
        # distances are in pixels
        mx_curv = (temp_x[:, None] + temp_y[None, :]) / (ellipsoid['diameter'] / pix)
        mx_curv *= 1 - refraction

    # index matrix
    mx_indices, mx_err_indices, mx_err, mask = errorMatrix(radius_pix, precision)
    # for speed : precalculate maximum mask - can be shrunk for lesser diameters
    mask_circ_max = mx_dist [:] > p.maxSearchRadius

    for i in points :
        x = points[i]["x"]
        y = points[i]["y"]

        # gives full window size by default
        data, cropping = readRaster(dsDem, x, y, radius_pix)

        (x_offset, y_offset, x_offset_dist_mx, y_offset_dist_mx, window_size_x, window_size_y) = cropping

        z = points[i]["zObserver"]
        z_targ= points[i]["zTarget"]
        z_abs = z + data[radius_pix, radius_pix]

        if points[i]["searchRadius"] != p.maxSearchRadius:
           # this is to reduce unnecessary numpy query for each point
           # everything else is made on maximum radius !
            mask_circ = mx_dist [:] > points[i]["searchRadius"]
        else:
            mask_circ = mask_circ_max

        # level all according to observer
        if useEarthCurvature:
            data -= mx_curv + z_abs
        else:
            data -= z_abs

        # all one line = (data -z - mxcurv) /mx_dist
        data /= mx_dist

        if z_targ > 0:
            # it's ( data + z_target ) / dist,
            # but / dist is already made above
            mx_target = data + z_targ / mx_dist
        else:
            mx_target = None

        matrix_vis = calculateViewshed(data, mx_err, mask, mx_indices, mx_err_indices, analysisType, mx_target, precision)

        if analysisType == INVISIBILITY_DEPTH:
            matrix_vis *= mx_dist
            # assign target height to the centre (not observer!)
            # = first neigbour that is always visible
            matrix_vis[radius_pix, radius_pix] = matrix_vis[radius_pix, radius_pix + 1]

        # mask out corners
        matrix_vis[mask_circ]=numpy.nan

        if os.path.isdir(outputPath):
            filePath = os.path.join(outputPath, '{}_{}.tif'.format(fid, TYPE_NAME[analysisType]))
        else:
            filePath = outputPath

        writeRaster(outputPath,
                    matrix_vis[y_offset_dist_mx : y_offset_dist_mx + window_size_y,
                               x_offset_dist_mx : x_offset_dist_mx + window_size_x],
                    x_offset,
                    y_offset,
                    dsDem,
                    gdal.GDT_Float32)
        matrix_vis= None

    matrix_final = None
    data = None

    dsDem = None

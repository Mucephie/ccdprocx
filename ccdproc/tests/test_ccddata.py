# Licensed under a 3-clause BSD style license - see LICENSE.rst
# This module implements the base CCDData class.

import numpy as np
from astropy.io import fits

from numpy.testing import assert_array_equal
from astropy.tests.helper import pytest
from astropy.utils import NumpyRNGContext

from ..ccddata import CCDData, electrons, fromFITS, toFITS


def test_ccddata_empty():
    with pytest.raises(TypeError):
        CCDData()  # empty initializer should fail


def test_ccddata_simple():
    with NumpyRNGContext(123):
        cd = CCDData(np.random.random((10, 10)))
    assert cd.shape == (10, 10)
    assert cd.size == 100
    assert cd.dtype == np.dtype(float)


def test_fromFITS():
    with NumpyRNGContext(123):
        nd = np.random.random((10, 10))
    hdu = fits.PrimaryHDU(nd)
    hdulist = fits.HDUList([hdu])
    cd = fromFITS(hdulist)
    assert cd.shape == (10, 10)
    assert cd.size == 100
    assert cd.dtype == np.dtype(float)
    assert cd.meta == hdu.header


def test_fromMEF():
    with NumpyRNGContext(123):
        nd = np.random.random((10, 10))
    hdu = fits.PrimaryHDU(nd)
    hdulist = fits.HDUList([hdu, hdu])
    with pytest.raises(ValueError):
        cd = fromFITS(hdulist)


def test_metafromheader():
    hdr = fits.header.Header()
    hdr.set('observer', 'Edwin Hubble')
    hdr.set('exptime', '3600')

    d1 = CCDData(np.ones((5, 5)), meta=hdr)
    assert d1.meta['OBSERVER'] == 'Edwin Hubble'
    assert d1.header['OBSERVER'] == 'Edwin Hubble'


def test_metafromdict():
    dic = {'OBSERVER': 'Edwin Hubble', 'EXPTIME': 3600}
    d1 = CCDData(np.ones((5, 5)), meta=dic)
    assert d1.meta['OBSERVER'] == 'Edwin Hubble'


def test_header2meta():
    hdr = fits.header.Header()
    hdr.set('observer', 'Edwin Hubble')
    hdr.set('exptime', '3600')

    d1 = CCDData(np.ones((5, 5)))
    d1.header = hdr
    assert d1.meta['OBSERVER'] == 'Edwin Hubble'
    assert d1.header['OBSERVER'] == 'Edwin Hubble'


def test_metafromstring_fail():
    hdr = 'this is not a valid header'
    with pytest.raises(TypeError):
        d1 = CCDData(np.ones((5, 5)), meta=hdr)


def test_create_variance():
    with NumpyRNGContext(123):
        cd = CCDData(np.random.random((10, 10)), unit=electrons)
    cd.create_variance(5)
    assert cd.uncertainty.array.shape == (10, 10)
    assert cd.uncertainty.array.size == 100
    assert cd.uncertainty.array.dtype == np.dtype(float)


def test_setting_bad_uncertainty_raises_error():
    cd = CCDData(np.ones((100, 100)))
    with pytest.raises(TypeError):
        # Uncertainty is supposed to be an instance of NDUncertainty
        cd.uncertainty = 10


def test_create_variance_with_bad_image_units_raises_error():
    cd = CCDData(np.ones((100, 100)))
    with pytest.raises(TypeError):
        cd.create_variance(10)


def test_toFITS():
    cd = CCDData(np.ones((100, 100)), meta={'observer': 'Edwin Hubble'})
    fits_hdulist = toFITS(cd)
    assert isinstance(fits_hdulist, fits.HDUList)


if __name__ == '__main__':
    test_ccddata_empty()
    test_ccddata_simple()
    test_fromFITS()
    test_fromMEF()
    test_metafromheader()
    test_metafromstring_fail()
    test_metafromdict()
    test_header2meta()
    test_create_variance()

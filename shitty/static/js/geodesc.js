"use strict";

// This file is part of Leaflet.Geodesic.
// Copyright (C) 2017  Henry Thasler
// based on code by Chris Veness Copyright (C) 2014 https://github.com/chrisveness/geodesy
//
// Leaflet.Geodesic is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Leaflet.Geodesic is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Leaflet.Geodesic.  If not, see <http://www.gnu.org/licenses/>.


/** Extend Number object with method to convert numeric degrees to radians */
if (typeof Number.prototype.toRadians === "undefined") {
  Number.prototype.toRadians = function() {
    return this * Math.PI / 180;
  };
}

/** Extend Number object with method to convert radians to numeric (signed) degrees */
if (typeof Number.prototype.toDegrees === "undefined") {
  Number.prototype.toDegrees = function() {
    return this * 180 / Math.PI;
  };
}

var INTERSECT_LNG = 179.999; // Lng used for intersection and wrap around on map edges

L.Geodesic = L.Polyline.extend({
  options: {
    color: "blue",
    steps: 10,
    dash: 1,
    wrap: true
  },

  initialize: function(latlngs, options) {
    this.options = this._merge_options(this.options, options);
    this.options.dash = Math.max(1e-3, Math.min(1, parseFloat(this.options.dash) || 1));
    this.datum = {};
    this.datum.ellipsoid = {
        a: 6378137,
        b: 6356752.3142,
        f: 1 / 298.257223563
      }; // WGS-84
    this._latlngs = this._generate_Geodesic(latlngs);
    L.Polyline.prototype.initialize.call(this, this._latlngs, this.options);
  },

  setLatLngs: function(latlngs) {
    this._latlngs = this._generate_Geodesic(latlngs);
    L.Polyline.prototype.setLatLngs.call(this, this._latlngs);
  },

  /**
   * Calculates some statistic values of current geodesic multipolyline
   * @returns (Object} Object with several properties (e.g. overall distance)
   */
  getStats: function() {
    let obj = {
        distance: 0,
        points: 0,
        polygons: this._latlngs.length
      }, poly, points;

    for (poly = 0; poly < this._latlngs.length; poly++) {
      obj.points += this._latlngs[poly].length;
      for (points = 0; points < (this._latlngs[poly].length - 1); points++) {
        obj.distance += this._vincenty_inverse(this._latlngs[poly][points],
          this._latlngs[poly][points + 1]).distance;
      }
    }
    return obj;
  },


  /**
   * Creates geodesic lines from geoJson. Replaces all current features of this instance.
   * Supports LineString, MultiLineString and Polygon
   * @param {Object} geojson - geosjon as object.
   */
  geoJson: function(geojson) {

    let normalized = L.GeoJSON.asFeature(geojson);
    let features = normalized.type === "FeatureCollection" ? normalized.features : [
      normalized
    ];
    this._latlngs = [];
    for (let feature of features) {
      let geometry = feature.type === "Feature" ? feature.geometry :
        feature,
        coords = geometry.coordinates;

      switch (geometry.type) {
        case "LineString":
          this._latlngs.push(this._generate_Geodesic([L.GeoJSON.coordsToLatLngs(
            coords, 0)]));
          break;
        case "MultiLineString":
        case "Polygon":
          this._latlngs.push(this._generate_Geodesic(L.GeoJSON.coordsToLatLngs(
            coords, 1)));
          break;
        case "Point":
        case "MultiPoint":
          console.log("Dude, points can't be drawn as geodesic lines...");
          break;
        default:
          console.log("Drawing " + geometry.type +
            " as a geodesic is not supported. Skipping...");
      }
    }
    L.Polyline.prototype.setLatLngs.call(this, this._latlngs);
  },

  /**
   * Creates a great circle. Replaces all current lines.
   * @param {Object} center - geographic position
   * @param {number} radius - radius of the circle in metres
   */
  createCircle: function(center, radius) {
    let polylineIndex = 0;
    let prev = {
      lat: 0,
      lng: 0,
      brg: 0
    };
    let step;

    this._latlngs = [];
    this._latlngs[polylineIndex] = [];

    let direct = this._vincenty_direct(L.latLng(center), 0, radius, this.options
      .wrap);
    prev = L.latLng(direct.lat, direct.lng);
    this._latlngs[polylineIndex].push(prev);
    for (step = 1; step <= this.options.steps;) {
      direct = this._vincenty_direct(L.latLng(center), 360 / this.options
        .steps * step, radius, this.options.wrap);
      let gp = L.latLng(direct.lat, direct.lng);
      if (Math.abs(gp.lng - prev.lng) > 180) {
        let inverse = this._vincenty_inverse(prev, gp);
        let sec = this._intersection(prev, inverse.initialBearing, {
          lat: -89,
          lng: ((gp.lng - prev.lng) > 0) ? -INTERSECT_LNG : INTERSECT_LNG
        }, 0);
        if (sec) {
          this._latlngs[polylineIndex].push(L.latLng(sec.lat, sec.lng));
          polylineIndex++;
          this._latlngs[polylineIndex] = [];
          prev = L.latLng(sec.lat, -sec.lng);
          this._latlngs[polylineIndex].push(prev);
        } else {
          polylineIndex++;
          this._latlngs[polylineIndex] = [];
          this._latlngs[polylineIndex].push(gp);
          prev = gp;
          step++;
        }
      } else {
        this._latlngs[polylineIndex].push(gp);
        prev = gp;
        step++;
      }
    }

    L.Polyline.prototype.setLatLngs.call(this, this._latlngs);
  },

  /**
   * Creates a geodesic Polyline from given coordinates
   * Note: dashed lines are under work
   * @param {Object} latlngs - One or more polylines as an array. See Leaflet doc about Polyline
   * @returns (Object} An array of arrays of geographical points.
   */
  _generate_Geodesic: function(latlngs) {
    let _geo = [], _geocnt = 0;

    for (let poly = 0; poly < latlngs.length; poly++) {
      _geo[_geocnt] = [];
      let prev = L.latLng(latlngs[poly][0]);
      for (let points = 0; points < (latlngs[poly].length - 1); points++) {
        // use prev, so that wrapping behaves correctly
        let pointA = prev;
        let pointB = L.latLng(latlngs[poly][points + 1]);
        if (pointA.equals(pointB)) {
          continue;
        }
        let inverse = this._vincenty_inverse(pointA, pointB);
        _geo[_geocnt].push(prev);
        for (let s = 1; s <= this.options.steps;) {
          let distance = inverse.distance / this.options.steps;
          // dashed lines don't go the full distance between the points
          let dist_mult = s - 1 + this.options.dash;
          let direct = this._vincenty_direct(pointA, inverse.initialBearing, distance*dist_mult, this.options.wrap);
          let gp = L.latLng(direct.lat, direct.lng);
          if (Math.abs(gp.lng - prev.lng) > 180) {
            let sec = this._intersection(pointA, inverse.initialBearing, {
              lat: -89,
              lng: ((gp.lng - prev.lng) > 0) ? -INTERSECT_LNG : INTERSECT_LNG
            }, 0);
            if (sec) {
              _geo[_geocnt].push(L.latLng(sec.lat, sec.lng));
              _geocnt++;
              _geo[_geocnt] = [];
              prev = L.latLng(sec.lat, -sec.lng);
              _geo[_geocnt].push(prev);
            } else {
              _geocnt++;
              _geo[_geocnt] = [];
              _geo[_geocnt].push(gp);
              prev = gp;
              s++;
            }
          } else {
            _geo[_geocnt].push(gp);
            // Dashed lines start a new line
            if (this.options.dash < 1){
                _geocnt++;
                // go full distance this time, to get starting point for next line
                let direct_full = this._vincenty_direct(pointA, inverse.initialBearing, distance*s, this.options.wrap);
                _geo[_geocnt] = [];
                prev = L.latLng(direct_full.lat, direct_full.lng);
                _geo[_geocnt].push(prev);
            }
            else prev = gp;
            s++;
          }
        }
      }
      _geocnt++;
    }
    return _geo;
  },

  /**
   * Vincenty direct calculation.
   * based on the work of Chris Veness (https://github.com/chrisveness/geodesy)
   *
   * @private
   * @param {number} initialBearing - Initial bearing in degrees from north.
   * @param {number} distance - Distance along bearing in metres.
   * @returns (Object} Object including point (destination point), finalBearing.
   */

  _vincenty_direct: function(p1, initialBearing, distance, wrap) {
    var Ï†1 = p1.lat.toRadians(),
      Î»1 = p1.lng.toRadians();
    var Î±1 = initialBearing.toRadians();
    var s = distance;

    var a = this.datum.ellipsoid.a,
      b = this.datum.ellipsoid.b,
      f = this.datum.ellipsoid.f;

    var sinÎ±1 = Math.sin(Î±1);
    var cosÎ±1 = Math.cos(Î±1);

    var tanU1 = (1 - f) * Math.tan(Ï†1),
      cosU1 = 1 / Math.sqrt((1 + tanU1 * tanU1)),
      sinU1 = tanU1 * cosU1;
    var Ïƒ1 = Math.atan2(tanU1, cosÎ±1);
    var sinÎ± = cosU1 * sinÎ±1;
    var cosSqÎ± = 1 - sinÎ± * sinÎ±;
    var uSq = cosSqÎ± * (a * a - b * b) / (b * b);
    var A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 *
      uSq)));
    var B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)));

    var Ïƒ = s / (b * A),
      ÏƒÊ¹, iterations = 0;
    var sinÏƒ, cosÏƒ;
    var cos2ÏƒM;
    do {
      cos2ÏƒM = Math.cos(2 * Ïƒ1 + Ïƒ);
      sinÏƒ = Math.sin(Ïƒ);
      cosÏƒ = Math.cos(Ïƒ);
      var Î”Ïƒ = B * sinÏƒ * (cos2ÏƒM + B / 4 * (cosÏƒ * (-1 + 2 * cos2ÏƒM *
          cos2ÏƒM) -
        B / 6 * cos2ÏƒM * (-3 + 4 * sinÏƒ * sinÏƒ) * (-3 + 4 * cos2ÏƒM *
          cos2ÏƒM)));
      ÏƒÊ¹ = Ïƒ;
      Ïƒ = s / (b * A) + Î”Ïƒ;
    } while (Math.abs(Ïƒ - ÏƒÊ¹) > 1e-12 && ++iterations);

    var x = sinU1 * sinÏƒ - cosU1 * cosÏƒ * cosÎ±1;
    var Ï†2 = Math.atan2(sinU1 * cosÏƒ + cosU1 * sinÏƒ * cosÎ±1, (1 - f) *
      Math.sqrt(sinÎ± * sinÎ± + x * x));
    var Î» = Math.atan2(sinÏƒ * sinÎ±1, cosU1 * cosÏƒ - sinU1 * sinÏƒ * cosÎ±1);
    var C = f / 16 * cosSqÎ± * (4 + f * (4 - 3 * cosSqÎ±));
    var L = Î» - (1 - C) * f * sinÎ± *
      (Ïƒ + C * sinÏƒ * (cos2ÏƒM + C * cosÏƒ * (-1 + 2 * cos2ÏƒM * cos2ÏƒM)));

    var Î»2;
    if (wrap) {
      Î»2 = (Î»1 + L + 3 * Math.PI) % (2 * Math.PI) - Math.PI; // normalise to -180...+180
    } else {
      Î»2 = (Î»1 + L); // do not normalize
    }

    var revAz = Math.atan2(sinÎ±, -x);

    return {
      lat: Ï†2.toDegrees(),
      lng: Î»2.toDegrees(),
      finalBearing: revAz.toDegrees()
    };
  },

  /**
   * Vincenty inverse calculation.
   * based on the work of Chris Veness (https://github.com/chrisveness/geodesy)
   *
   * @private
   * @param {LatLng} p1 - Latitude/longitude of start point.
   * @param {LatLng} p2 - Latitude/longitude of destination point.
   * @returns {Object} Object including distance, initialBearing, finalBearing.
   * @throws {Error} If formula failed to converge.
   */
  _vincenty_inverse: function(p1, p2) {
    var Ï†1 = p1.lat.toRadians(),
      Î»1 = p1.lng.toRadians();
    var Ï†2 = p2.lat.toRadians(),
      Î»2 = p2.lng.toRadians();

    var a = this.datum.ellipsoid.a,
      b = this.datum.ellipsoid.b,
      f = this.datum.ellipsoid.f;

    var L = Î»2 - Î»1;
    var tanU1 = (1 - f) * Math.tan(Ï†1),
      cosU1 = 1 / Math.sqrt((1 + tanU1 * tanU1)),
      sinU1 = tanU1 * cosU1;
    var tanU2 = (1 - f) * Math.tan(Ï†2),
      cosU2 = 1 / Math.sqrt((1 + tanU2 * tanU2)),
      sinU2 = tanU2 * cosU2;

    var Î» = L,
      Î»Ê¹, iterations = 0;
    var cosSqÎ±, sinÏƒ, cos2ÏƒM, cosÏƒ, Ïƒ, sinÎ», cosÎ»;
    do {
      sinÎ» = Math.sin(Î»);
      cosÎ» = Math.cos(Î»);
      var sinSqÏƒ = (cosU2 * sinÎ») * (cosU2 * sinÎ») + (cosU1 * sinU2 -
        sinU1 * cosU2 * cosÎ») * (cosU1 * sinU2 - sinU1 * cosU2 * cosÎ»);
      sinÏƒ = Math.sqrt(sinSqÏƒ);
      if (sinÏƒ == 0) return 0; // co-incident points
      cosÏƒ = sinU1 * sinU2 + cosU1 * cosU2 * cosÎ»;
      Ïƒ = Math.atan2(sinÏƒ, cosÏƒ);
      var sinÎ± = cosU1 * cosU2 * sinÎ» / sinÏƒ;
      cosSqÎ± = 1 - sinÎ± * sinÎ±;
      cos2ÏƒM = cosÏƒ - 2 * sinU1 * sinU2 / cosSqÎ±;
      if (isNaN(cos2ÏƒM)) cos2ÏƒM = 0; // equatorial line: cosSqÎ±=0 (Â§6)
      var C = f / 16 * cosSqÎ± * (4 + f * (4 - 3 * cosSqÎ±));
      Î»Ê¹ = Î»;
      Î» = L + (1 - C) * f * sinÎ± * (Ïƒ + C * sinÏƒ * (cos2ÏƒM + C * cosÏƒ * (-
        1 + 2 * cos2ÏƒM * cos2ÏƒM)));
    } while (Math.abs(Î» - Î»Ê¹) > 1e-12 && ++iterations < 100);
    if (iterations >= 100) {
      console.log("Formula failed to converge. Altering target position.");
      return this._vincenty_inverse(p1, {
          lat: p2.lat,
          lng: p2.lng - 0.01
        });
        //  throw new Error('Formula failed to converge');
    }

    var uSq = cosSqÎ± * (a * a - b * b) / (b * b);
    var A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 *
      uSq)));
    var B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)));
    var Î”Ïƒ = B * sinÏƒ * (cos2ÏƒM + B / 4 * (cosÏƒ * (-1 + 2 * cos2ÏƒM *
        cos2ÏƒM) -
      B / 6 * cos2ÏƒM * (-3 + 4 * sinÏƒ * sinÏƒ) * (-3 + 4 * cos2ÏƒM *
        cos2ÏƒM)));

    var s = b * A * (Ïƒ - Î”Ïƒ);

    var fwdAz = Math.atan2(cosU2 * sinÎ», cosU1 * sinU2 - sinU1 * cosU2 *
      cosÎ»);
    var revAz = Math.atan2(cosU1 * sinÎ», -sinU1 * cosU2 + cosU1 * sinU2 *
      cosÎ»);

    s = Number(s.toFixed(3)); // round to 1mm precision
    return {
      distance: s,
      initialBearing: fwdAz.toDegrees(),
      finalBearing: revAz.toDegrees()
    };
  },


  /**
   * Returns the point of intersection of two paths defined by point and bearing.
   * based on the work of Chris Veness (https://github.com/chrisveness/geodesy)
   *
   * @param {LatLon} p1 - First point.
   * @param {number} brng1 - Initial bearing from first point.
   * @param {LatLon} p2 - Second point.
   * @param {number} brng2 - Initial bearing from second point.
   * @returns {Object} containing lat/lng information of intersection.
   *
   * @example
   * var p1 = LatLon(51.8853, 0.2545), brng1 = 108.55;
   * var p2 = LatLon(49.0034, 2.5735), brng2 = 32.44;
   * var pInt = LatLon.intersection(p1, brng1, p2, brng2); // pInt.toString(): 50.9078Â°N, 4.5084Â°E
   */
  _intersection: function(p1, brng1, p2, brng2) {
    // see http://williams.best.vwh.net/avform.htm#Intersection

    var Ï†1 = p1.lat.toRadians(),
      Î»1 = p1.lng.toRadians();
    var Ï†2 = p2.lat.toRadians(),
      Î»2 = p2.lng.toRadians();
    var Î¸13 = Number(brng1).toRadians(),
      Î¸23 = Number(brng2).toRadians();
    var Î”Ï† = Ï†2 - Ï†1,
      Î”Î» = Î»2 - Î»1;

    var Î´12 = 2 * Math.asin(Math.sqrt(Math.sin(Î”Ï† / 2) * Math.sin(Î”Ï† / 2) +
      Math.cos(Ï†1) * Math.cos(Ï†2) * Math.sin(Î”Î» / 2) * Math.sin(Î”Î» /
        2)));
    if (Î´12 == 0) return null;

    // initial/final bearings between points
    var Î¸1 = Math.acos((Math.sin(Ï†2) - Math.sin(Ï†1) * Math.cos(Î´12)) /
      (Math.sin(Î´12) * Math.cos(Ï†1)));
    if (isNaN(Î¸1)) Î¸1 = 0; // protect against rounding
    var Î¸2 = Math.acos((Math.sin(Ï†1) - Math.sin(Ï†2) * Math.cos(Î´12)) /
      (Math.sin(Î´12) * Math.cos(Ï†2)));
    var Î¸12, Î¸21;
    if (Math.sin(Î»2 - Î»1) > 0) {
      Î¸12 = Î¸1;
      Î¸21 = 2 * Math.PI - Î¸2;
    } else {
      Î¸12 = 2 * Math.PI - Î¸1;
      Î¸21 = Î¸2;
    }

    var Î±1 = (Î¸13 - Î¸12 + Math.PI) % (2 * Math.PI) - Math.PI; // angle 2-1-3
    var Î±2 = (Î¸21 - Î¸23 + Math.PI) % (2 * Math.PI) - Math.PI; // angle 1-2-3

    if (Math.sin(Î±1) == 0 && Math.sin(Î±2) == 0) return null; // infinite intersections
    if (Math.sin(Î±1) * Math.sin(Î±2) < 0) return null; // ambiguous intersection

    //Î±1 = Math.abs(Î±1);
    //Î±2 = Math.abs(Î±2);
    // ... Ed Williams takes abs of Î±1/Î±2, but seems to break calculation?

    var Î±3 = Math.acos(-Math.cos(Î±1) * Math.cos(Î±2) +
      Math.sin(Î±1) * Math.sin(Î±2) * Math.cos(Î´12));
    var Î´13 = Math.atan2(Math.sin(Î´12) * Math.sin(Î±1) * Math.sin(Î±2),
      Math.cos(Î±2) + Math.cos(Î±1) * Math.cos(Î±3));
    var Ï†3 = Math.asin(Math.sin(Ï†1) * Math.cos(Î´13) +
      Math.cos(Ï†1) * Math.sin(Î´13) * Math.cos(Î¸13));
    var Î”Î»13 = Math.atan2(Math.sin(Î¸13) * Math.sin(Î´13) * Math.cos(Ï†1),
      Math.cos(Î´13) - Math.sin(Ï†1) * Math.sin(Ï†3));
    var Î»3 = Î»1 + Î”Î»13;
    Î»3 = (Î»3 + 3 * Math.PI) % (2 * Math.PI) - Math.PI; // normalise to -180..+180Âº

    return {
      lat: Ï†3.toDegrees(),
      lng: Î»3.toDegrees()
    };
  },

  /**
   * Overwrites obj1's values with obj2's and adds obj2's if non existent in obj1
   * @param obj1
   * @param obj2
   * @returns obj3 a new object based on obj1 and obj2
   */
  _merge_options: function(obj1, obj2) {
    let obj3 = {};
    for (let attrname in obj1) {
      obj3[attrname] = obj1[attrname];
    }
    for (let attrname in obj2) {
      obj3[attrname] = obj2[attrname];
    }
    return obj3;
  }
});

L.geodesic = function(latlngs, options) {
  return new L.Geodesic(latlngs, options);
};

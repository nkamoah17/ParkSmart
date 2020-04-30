import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        title: 'Flutter Demo',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          accentColor: Colors.blueAccent
        ),
        home: MapSample());
  }
}

// adapted from the Google-maps api documentation
class MapSample extends StatefulWidget {
  @override
  State<MapSample> createState() => MapSampleState();
}

class MapSampleState extends State<MapSample> {
  Completer<GoogleMapController> _controller = Completer();

  Set<Marker> _markers = Set.from([
    Marker(markerId: MarkerId("Spot1"), position: LatLng(42.931050, -85.586290), icon: BitmapDescriptor.defaultMarker),
    Marker(markerId: MarkerId("Spot2"), position: LatLng(42.931039, -85.586323), icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen)),
    Marker(markerId: MarkerId("Spot3"), position: LatLng(42.931025, -85.586360), icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen)),
    Marker(markerId: MarkerId("Spot4"), position: LatLng(42.931018, -85.586395), icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen)),
    Marker(markerId: MarkerId("Spot5"), position: LatLng(42.931003, -85.586427), icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen)),
    Marker(markerId: MarkerId("Spot6"), position: LatLng(42.930986, -85.586463), icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen)),
    Marker(markerId: MarkerId("Spot7"), position: LatLng(42.930968, -85.586483), icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen)),
    Marker(markerId: MarkerId("Spot8"), position: LatLng(42.930953, -85.586522), icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen)),
    Marker(markerId: MarkerId("Spot9"), position: LatLng(42.930928, -85.586541)),
    Marker(markerId: MarkerId("Spot10"), position: LatLng(42.930902, -85.586567)),
  ]);

  final CameraPosition _kCalvin = CameraPosition(
    target: LatLng(42.930682, -85.586666),
    zoom: 14.4746,
  );

  @override
  Widget build(BuildContext context) {
    return GoogleMap(
        mapType: MapType.hybrid,
        initialCameraPosition: _kCalvin,
        onMapCreated: (GoogleMapController controller) {
          _controller.complete(controller);
        },
        markers: _markers,

      );
  }
}
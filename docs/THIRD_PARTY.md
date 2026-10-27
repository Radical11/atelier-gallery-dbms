# Bundled rendering dependency

The local 3D gallery uses **Three.js 0.186.1**, installed from the npm `three` package and bundled under `atelier/static/vendor/three/`. Only the WebGL build and required example modules are included. The upstream MIT license is preserved at `atelier/static/vendor/three/LICENSE`.

Source: https://github.com/mrdoob/three.js

The scene, procedural gallery objects, hover behavior and museum presentation are project code. The renderer requests a high-performance graphics context, uses up to 2× device pixel ratio, and renders up to the display refresh rate with a 120 fps ceiling. The browser and operating system choose which GPU supplies that context.

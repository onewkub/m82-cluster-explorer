# M82 Cluster Explorer

The star map is the workspace: a large, quiet celestial field with a fixed inspection panel, rather than a dashboard of cards. Selection connects the map, member count, size and CMD.

Palette: paper #eef2f5, instrument ink #192c40, sky #101e30, young stars #72d9f0, old stars #efbf79, selected #ff846b. System Thai typography uses Leelawadee UI, with Segoe UI for numbers. Controls are left aligned and use explicit Thai labels. The sky is the one bold element; surrounding panels remain pale and restrained.

Layout: method tabs above the map; searchable cluster index on the left; map in the middle; selected cluster and CMD on the right. On small screens the index collapses into a compact scrolling list and details sit below the map. No decorative hero, counters or marketing copy.

Scientific constraints: shared TAN plane with east left and north up; spherical member RMS radius at 17 pc/arcsec; 3D means position plus colour, not spatial depth. Quality selection remains the thesis baseline of 391 groups. Saved method labels are retained without rerunning clustering.

Background update: retain the existing layout, introduce a quiet layer strip below the map. A monochrome, WCS-registered F435W image is the context layer; population colours and coral selection remain distinct overlays. Background and star opacity are independently adjustable. The image and stars share one transform during all zoom and pan interactions.

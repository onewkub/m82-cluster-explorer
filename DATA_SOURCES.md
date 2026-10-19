# Data sources and interpretation

## Included web data

The viewer contains 408,213 catalog rows shared by all three methods. Saved labels are exported without rerunning clustering.

| Method | Original input | Groups |
| --- | --- | ---: |
| DBSCAN 2D | `m82_dwarf_galaxy_candidates_2d.csv` | 510 |
| DBSCAN 3D | `m82_clusters_3d_live.csv` | 49 |
| HDBSCAN | `m82_dwarf_galaxy_candidates_2d_hdbscan.csv` | 318 |

The original 391-candidate selection comes from `candidates_quality_screening.csv`. These four CSV files are needed only to rebuild the web data and are not included. The viewer preserves this research snapshot; subsequent thesis corrections have not been applied here.

Source filenames and SHA-256 hashes for the three clustering inputs are recorded in `dist/data/catalog.json`. Background FITS provenance and registration checks are recorded in `dist/data/background.json`.

## Background image

Credit: Hubble Space Telescope / ACS, ANGST (program 10776), reference F435W images for six M82 fields. The included grayscale mosaic is generated from the six `*_f435w_v1_ref.fits` files, reprojected to the viewer's common TAN plane. It is a display image, not new photometry or a NASA color composite. Raw FITS files are not included.

Rebuilding also requires the corresponding `hlsp_angst_hst_acs-wfc_10776-m82-posN_f555w-f814w_v1_gst.fits` catalog in each `posN` folder for coordinate checks. See `prepare_background.py` and `docs/research-notes.md` for processing details.

## Scientific scope

- RMS radius is measured from the saved member positions using spherical angular separations and 17 pc per arcsecond. It is not a half-light radius or a confirmed physical boundary.
- DF-E1 reference position: RA 149.1341 degrees, Dec 69.7126 degrees. Positional proximity does not establish object identity.
- Y-1075 in 2D has 13 members, RMS radius 24.587321 pc and reference offset 5.772542 arcsec.
- Cluster labels are method-specific. Matching numeric IDs across methods do not imply matching memberships.
- The candidate filter retains the original quality-screening list; the web export does not recompute PCA screening.
- The image, saved labels and stellar measurements are research data with their own provenance; no new license for third-party data is asserted by this repository.

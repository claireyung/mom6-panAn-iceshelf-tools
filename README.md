# mom6-panAn-iceshelf-tools

The purpose of this repository is to keep track of tools used to create a regional MOM6 pan-Antarctic ocean model with ice shelves and their evaluation.

<img width="454" height="444" alt="Screenshot 2025-10-29 at 2 54 44 pm" src="https://github.com/user-attachments/assets/c794628f-3e1a-4b3d-bb65-ad54e5746729" />

### Useful links:
- [Existing COSIMA pan-Antarctic model](https://github.com/COSIMA/mom6-panan)
- [Ocean Model Grid Generator (ACCESS-NRI fork)](https://github.com/ACCESS-NRI/ocean_model_grid_generator/tree/main)
- [COSIMA Bathymetry tools](https://github.com/COSIMA/bathymetry-tools)

Feel free to contribute back to this repository and push any changes you make, notebooks and documentation you add back via pull request
- [This list of issues](https://github.com/claireyung/mom6-panAn-iceshelf-tools/issues) has a list of things to work on
- [The wiki](https://github.com/claireyung/mom6-panAn-iceshelf-tools/wiki) has some notes about the ice shelf configuration setup


### pan-Antarctic regional ACCESS-OM3 config (no ice shelves)
#### 10-year spun-up config for evaluation
- [Configuration](https://github.com/claireyung/access-om3-configs/tree/8km_jra_ryf_obc2-sapphirerapid-Charrassin-newparams-rerun-Wright-spinup-accessom2IC-yr9)
- [Instructions](https://github.com/claireyung/access-om3-configs/blob/8km_jra_ryf_obc2-sapphirerapid-Charrassin-newparams-rerun-Wright-spinup-accessom2IC-yr9/panantarctic_instructions.md)
- [Evaluation notebooks](https://github.com/claireyung/mom6-panAn-iceshelf-tools/tree/main/evaluation) and [discussions](https://github.com/claireyung/mom6-panAn-iceshelf-tools/issues/15)
#### Improved config for ACCESS-NRI
- [Configuration](https://github.com/ACCESS-NRI/access-om3-configs/pull/713)

### pan-Antarctic regional ACCESS-OM3 config (with ice shelves)
Links from various places! 
- Repository with notebooks used to generate input files and evaluate model https://github.com/claireyung/mom6-panAn-iceshelf-tools
- Wiki with instructions on how to make the config (quite a few steps) https://github.com/claireyung/mom6-panAn-iceshelf-tools/wiki/ACCESS%E2%80%90OM3-config-with-ice-shelves-%E2%80%90-input-files-and-config-details
- IAF OM3 panan ice shelf config that I ran https://github.com/claireyung/access-om3-configs/tree/ice_shelf_panan-iaf_v2026_2
- How-to-run instructions for that config (running for the first month is a bit different) https://github.com/claireyung/access-om3-configs/blob/ice_shelf_panan-iaf_v2026_2/ice_shelf_instructions.md
- List of issues to be considered for om3 ice shelf model development https://github.com/claireyung/mom6-panAn-iceshelf-tools/issues/49
- ACCESS-NRI progress towards alpha ice shelf config (basically the old RYF config with a couple of bug fixes, https://github.com/ACCESS-NRI/access-om3-configs/pull/1078)
- ACCESS-OM3 executable used uses this MOM6 version https://github.com/ACCESS-NRI/MOM6/tree/ice-shelf-dev and is compiled using spack prerelease tool here https://github.com/ACCESS-NRI/ACCESS-OM3/pull/142 Requires code changes to nuopc mom cap and ice shelf code described here https://github.com/ACCESS-NRI/MOM6/issues/29 and here https://github.com/ACCESS-NRI/MOM6/pull/38

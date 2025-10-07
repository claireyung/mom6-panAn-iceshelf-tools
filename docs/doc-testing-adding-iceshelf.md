# Ice Shelf Progress

Last updated August 23, 2025

This wiki page is to document my attempts at getting ice shelves in a MOM6 panan. Starting from a copy of [this document](https://github.com/claireyung/mom6-panAn-iceshelf-tools/blob/main/docs/doc-testing-adding-iceshelf.md). Turned into a wiki to make editing easier now that folks are using this repo for evaluation.

**Removed from wiki October 6, 2025

# mom6 panan ice shelf testing

In this file we document some of the tests I've tried with adding ice shelves to the 1/12th degree panan

### Basic stuff
- Needed to add a line into input.nml so that ice shelf initialises 
```
&MOM_input_nml 
    input_filename = 'n'
```
- need to turn runoff off. In SIS2 it's fine, just remove from data table. 
- [ ] ask OSIT team how to turn runoff off with ACCESS-OM3

- Olga has a SMB ice file. I was also getting a `shelf_sfc_mass_flux` variable in the ice shelf ICs of OM3 config. Is this because of JRA forcing?? -> *no difference to stability when I remove this from data_table in MOM6-SIS2 simualtions*

### Starting from Olga's panan and putting my 1/12th deg files in it

I have Olga's 1/4 degree layer mode panAn that she sent me last year working, with the ik11 MOM6-SIS2 executable. I tried to put in my new files and see if that would run. This involved changing the netcdfs and also the x/y numbers. I also needed to drop the DTBT RESET PERIOD and the DT THERM. I also needed to change a line in the input.nml to do with the saturation vapour pressure error because the first crash I got was the saturation vapour pressure error GFDL folks complain about.

change made:
```
 &surface_flux_nml
	ncar_ocean_flux = .true.,
	raoult_sat_vap = .true.
/

! &surface_flux_nml
!        gust_min = 1.e-10
!/
```
I got errors like 
```
NOTE from PE     0: MOM_vert_friction: updateCFLtruncationValue set CFL limit to    7.380E-02
NOTE from PE     0: MOM_vert_friction: updateCFLtruncationValue set CFL limit to    7.701E-02
FATAL from PE     0: btstep: number of barotropic step (nstep+nfilter) is 0
```
which I think might be related to the fact that in some parts of the domain, looking at the `IceShelf_IC_2.nc` output, I can see that there are parts where one density layer is the entire column (everything else vanished). Also i'm a bit confused why the first layer (bulk mixed layer) is evrywhere except in cavities. I needed to swap to Olga's 63 layer `Vertical_coordinate.nc` because the version I made did not have sufficient (nonlinear) resolution and a big section of 4000m layers in the Weddell polynya. Max depth is ~3000m ish (but mostly <1500m) with Olga's version. 

This runs for 1 day (in 1.5hrs walltime) with the debug executable Angus gave me `/g/data/x77/ahg157/exes/MOM6_SIS2/MOM6-dbg-e9dbc6c`. I think the updateCFLtruncation things are each timestep, you can see it progressing. Output looked okay, but this is with a 50m thick grounding line and the FRIS islands look way too big. It crashed with no GL and with 5m GL. I also did one with 125 layers with doubled resolution which wasn't much better.

- [ ] check why the ice shelf diags don't have NaNs with ice shelf islands but the ocean diags do -> **looks like it just didn't get coded up**

With other executables (faster ones), e.g. the ik11 one or ones I made with both the most recent mom-ocean and NOAA-GFDL/dev/gfdl versions crash after a few (~15-30) timesteps with the btstep error. This is kinda puzzling, why is the debug exe more stable than the normal ones.

The difference between MOM_parameter_doc.all of the debug one and mom-ocean one is
```
[cy8964@gadi-login-02 panAnt_config112]$ diff archive/output000/MOM_parameter_doc.all ../panAnt_config112-broken/work/MOM_parameter_doc.all 
54,61d53
< ENABLE_BUGS_BY_DEFAULT = True   !   [Boolean] default = True
<                                 ! If true, the defaults for certain recently added bug-fix flags are set to
<                                 ! recreate the bugs so that the code can be moved forward without changing
<                                 ! answers for existing configurations.  The defaults for groups of bug-fix flags
<                                 ! are periodcially changed to correct the bugs, at which point this parameter
<                                 ! will no longer be used to set their default.  Setting this to false means that
<                                 ! bugs are only used if they are actively selected, but it also means that
<                                 ! answers may change when code is updated due to newly found bugs.
349,355d340
< TFREEZE_S_IS_PRACS = True       !   [Boolean] default = True
<                                 ! When True, the model will check if the model internal salinity is practical
<                                 ! salinity.  If the model uses absolute salinity, a conversion will be applied.
< TFREEZE_T_IS_POTT = True        !   [Boolean] default = True
<                                 ! When True, the model will check if the model internal temperature is potential
<                                 ! temperature.  If the model uses conservative temperature, a conversion will be
<                                 ! applied.
392a378,379
> USE_MARBL_TRACERS = False       !   [Boolean] default = False
>                                 ! If true, use the MARBL tracer package.
```
and debug one and gfdl one is
```
[cy8964@gadi-login-02 panAnt_config112]$ diff archive/output000/MOM_parameter_doc.all ../panAnt_config112-gfdlexe/work/MOM_parameter_doc.all 
392a393,394
> USE_MARBL_TRACERS = False       !   [Boolean] default = False
>                                 ! If true, use the MARBL tracer package.
455c457
< DEBUG_IS = False                !   [Boolean] default = False
---
> DEBUG_IS = True                 !   [Boolean] default = True
803,805d804
< SQG_EXPO = 1.0                  !   [nondim] default = 1.0
<                                 ! Nondimensional exponent coeffecient of the SQG mode that is used for the
<                                 ! vertical struture of diffusivities.
1474a1474,1478
> MASK_COASTAL_PRESSURE_FORCE = False !   [Boolean] default = False
>                                 ! If true, use the land masks to zero out the diagnosed barotropic pressure
>                                 ! gradient accelerations at coastal or land points.  This changes diagnostics
>                                 ! and improves the reproducibility of certain debugging checksums, but it does
>                                 ! not alter the solutions themselves.
1570a1575,1577
> BMLD_EN_VALS = 25.0, 2500.0, 2.5E+05 !   [J/m2] default = 25.0, 2500.0, 2.5E+05
>                                 ! The energy values used to compute Bottom MLDs.  If not set (or all set to 0.),
>                                 ! the default will overwrite to 25., 2500., 250000.
2058a2066,2067
> ISO_DATE_STAMPED_STDOUT = False !   [Boolean] default = False
>                                 ! If true, use ISO formatted dates in messages to stdout

```
so it's not like parameters have been changed. Initial conditions checksums are identical.

With `DEBUG = True`, both debug and gfdl ones crash after 2 timesteps with
```
FATAL from PE  1094: regularize_surface: d_ea mismatch.
```
Points to this code https://github.com/NOAA-GFDL/MOM6/blob/c478543ebb78b2451b7370db05c49cf695acb843/src/parameterizations/vertical/MOM_regularize_layers.F90#L568

Initialisation checksums are identical, but log suggests different values at 6th decimal place. Still crash in same place though.

- [ ] try use Olga's T-S initial condiitons and regrid them to 1/12th -> likely not the issue based on 1/4 stuff below
- [ ] make sure ice shelf area and topo NaNs match
- [x] check if fill nan value matters, e.g. is fillna 1e-20 like zero? What does Olga use? - didn't seem to make a difference when i did a differnt nanfill, Olga's files have NaN
- [x] drop all the timesteps further?

I messaged Olga, she did no topo edits for her 1/4 deg.


### Starting from running panAn rOM3 (CICE6)
- I started with this. This is how I found the `input.nml` missing thing. We also made an executable with the new code (i.e. my PG + init fixes) as a pre-release, which needed a bit of mucking around with openmpi version stuff
- I was getting segfaults instead of `FATAL` mom errors. Not very helpful for debugging
- Made a debug exe, but crashed with sea ice initialisation even in non-ice-shelf panan. [Anton fixed it](https://github.com/ACCESS-NRI/ACCESS-OM3/pull/120#issuecomment-3082064434) but then crashed with a time error in OBC. Haven't tried it again with ice shelves

- After dev with mom6 panan SIS2, returned to this one and lowered the timestep, trying with sigma shelf zstar. Since there is a GL, crashed with ALE initialisation.
- [ ] make an ESMF mesh for 5m GL version.

- FOr some reason (maybe with the SMB IC) I needed the simplifying `SHELF_S_ROOT = True`

### Starting from running mom6-panan-SIS2 (COSIMA)
#### ALE mode
- Crashes in initialisation if GL. Strange since it's fine with ISOMIP. With 5m GL, initialises but crashes quickly with 
```
 h<0 at k=           1 h_old=  1.000000000000000E-012 wup=
  0.000000000000000E+000 wdn=  4.803268893738277E-012 dw_dz=
 -4.803268893738277E-012 h_new= -3.803268893738277E-012 h_err=
  1.066539943858808E-027

FATAL from PE   894: MOM_regridding: adjust_interface_motion() - implied h<0 is larger than roundoff!
```
Angus made an exe (`/g/data/x77/ahg157/exes/MOM6_SIS2/MOM6-aledbg-38a7d55`) that picks out the location and lists all the hs of the fail location, this showed a column with all 1e-12 thickness. Also played with value of Angstrom 1e-10 vs 1e-15, no difference. 

- Can initialise with no GL (get topo mask from layer mode)
```
WARNING from PE  1325: btstep: eta has dropped below bathyT:  -5.2367076876266410E+01 vs.  -5.0326725006103516E+01 at  -2.6292E+01 -5.8401E+01   3046   10
61

....

WARNING from PE  1381: MOM_diabatic_driver.F90, applyBoundaryFluxesInOut(): Mass created. x,y,dh=      -2.596E+01     -5.638E+01      2.396E-11


FATAL from PE  1214:  Could not find target coordinate   1033.00000000000      in get_polynomial_coordinate. This is caused by an inconsistent interpolant (perhaps not monotonically increasing):   1033.00000000000                          NaN                     NaN

```
(confused, should be using SIGMA_SHELF_ZSTAR?? No 1033 in any z inputs??)
- [ ] understand how layer intialistion works. Why can I not initialise vanished layers in ALE?

#### Layer mode
- expanding NaN blob (from data every timestep) (plots https://github.com/claireyung/mom6-panAn-iceshelf-tools/blob/main/docs/16july25.pdf and https://github.com/claireyung/mom6-panAn-iceshelf-tools/blob/claire_working/verification/debugging/ice-shelf-cradh.ipynb)
- debug executable more stable
- somehting near vanished layers creating instability, but still crashes < 1 day with 50m GL. This version also intilised layers in z levels strangely. I think because regridding coordinate mode was still on?? Even though USE_REGRDDING FAlse. Confused.
- [ ] what does regridding coordinate mode do when not ALE??
- can initialise fine with vanished layers (get ocean thick info from this run)
- runs a little longer with no GL but still crashes < 1 day

## Starting from Olga's config again

This time, rather than above where we go straight to 1/12th degree, I regenerated the files on the working 1/4 degree grid and swapped them one by one into the new config. Adding the new topography and initial conditions were totally fine (ran for 5 days). Adding the ice thickness but keeping the same ice area file also worked fine. The problems start when changing the sea ice topography and ice area. A table summarises my attempts. O means the original files, MY means my regenerated files from Charrassin, which has the 10 point grounding line and ice sheet area only covering wet ocean. In all cases, my topography (`TOPO_FILE` in `MOM_override`) and salt/temp ICs have been used. Note that in Olga's files, the sea ice topography is the same as the ocean topography (except it doesnt have the same max depth applied) except there is no sea ice where there is ice sheet area and thickness. Ice sheet area and thickness are nonzero in the same cells. Every ocean wet cell has either sea ice or ice sheet. There is no sea ice in ocean dry cells. The ice sheet initial condition file is not super helpful because it doesn't NaN out ocean dry cells (e.g. from topo being < 0m depth) and is just the initial conditions you give it plus a computed mass variable. Olga also has a `h_mask` variable in the ice shelf file which I don't, but there is an automatic code that computes it based on ice thickness in the code.

| sea ice topo | ice thickness | ice area | result|
| ----------- | -------------- | -------- | ------ |
| O          | O             | O      | runs 5 days |
| O  | MY | O | runs 5 days |
| O  | MY | MY | bad ice state (makes sense, don't want sea ice under ice shelf |
| MY  | O  | O |   saturation vapour pressure table overflow  |
| MY  | MY  | O |  saturation vapour pressure table overflow    |
| MY  | MY  | MY |  saturation vapour pressure table overflow    |

Depending whether I use `debug = True` or not, the FATAL error can be different e.g. `NaN in reproducing EPF overflow` or `saturation vapour pressure table overflow` or error with `d_ea` (regularization of layers[?](https://github.com/NOAA-GFDL/MOM6/blob/c478543ebb78b2451b7370db05c49cf695acb843/src/parameterizations/vertical/MOM_regularize_layers.F90#L568)) or `DTBT` error above. There seems to be some sort of NaN somewhere and then it depends where the model first notices as to what error gets presented.

I feel like I've tried every perturbation of the files, plus different NaNs or zeros or Nan fill values (e.g. Olga's topo files have zeros, the ones I used for the no ice shelf panan do have NaNs, doesn't make a difference). Olga's Nan fill values are NaNf.... I've checked that in my files the sea ice and ice sheet don't overlap. Also tried to used both ice sheet elevation and ice sheet thickness to define the sea ice mask, they are slightly different but same result. Also when I make a sea ice file using Olga's ice file and topo file the resultant file works so my pipeline seems fine.... the difference between the sea ice files is the topography differences plus also a few places where coastlines change. I've tried topo files with no grounding line, with my 10pt expansion and with no edits.

Also tried turning ice shelf thermodynamics off but having sea ice, still the same error so it's not due to high melt affecting neighbouring sea ice...

With a debug executable with FPEs on `/g/data/x77/ahg157/exes/MOM6_SIS2/MOM6-dbg-dcb7ded` it crashes even in the working configs with layer mode, (floating point exception during the initialisation) but it seems to be fine if you remove sea ice. I can't see any NaNs in `sea_ice_geometry.nc` or the ocean one or the initial conditions file. There are no other netCDFs of initial conditions for sea ice. This is not very helpful.

Earlier, I had added 
```
 &surface_flux_nml
	ncar_ocean_flux = .true.,
	raoult_sat_vap = .true.
/
```
to the input.nml when I had a saturation vapour pressure issue. With this re-added to the input.nml and ALE and the 1/4 degree with sea ice I got the error
`FATAL from PE     0: NaN detected: End of unpack_land_ice_boundary FIA%WindStr_x
` which points to [this](https://github.com/NOAA-GFDL/SIS2/blob/dev/gfdl/src/ice_model.F90#L420) but I don't think you can turn fast ice off and I don't know if the sea ice is the issue or if it's just the first place that it finds a NaN and complains.

In the `mom6.out` the 1/4 degree crashed at the same place with both layer and sigma shelf zstar (same CFL limit number) which suggests to me that it's not the ocean model but something with the sea ice/coupler.

I am slightly (very) stuck but here are some options:
- [ ] some sort of file bisect thing to find out where problem points are (Chris' idea). Might cause gradients though because topo definitely changes between products.
- [ ] try cice6/access-om3. Would be annoying to do it on 1/4 degree though since then I'd need to change everything else too, generate new meshes. And I haven't worked out the nuopc mesh stuff and how to turn off runoff.
- [ ] examine connectivity/isolated cells (Olga's suggestion), I've kind of done this though
- [ ] work out where NaN in sea ice initialisation comes in?? Print statements??
- [ ] work out where the stuff goes wrong e.g. where I'm getting the surface below bathymetry stuff. I did this a bit and it looked like the grounded ocean.
- [ ] investigate surface fluxes/sea ice/sea ice boundary based on the above `unpack_land_ice_boundary` error


### No sea ice
If I turn sea ice off (do ice false in input.nml and comment out the namelist stuff in input.nml) then it runs for 5 days with my files (and GL) in the 1/4 degree config in layer mode. For the 1/12th degree (with 50m GL, haven't tried other options) it ran for 1 day 6 hours before crashing and also required dt/dt_therm = 150, 300 did not work. 

I ran the 1/4 degree one for a day with sigma_shelf_zstar on and it was fine, but the 1/12th one crashed in 6 hours. Haven't extensively tested parameters e.g. mixing params. (Note actually the sigma_shelf_zstar 1/4 degree runs WITH sea ice too if I use olga's sea ice topo and ice area, and my topo, IC and ice draft for 5m GL)

some options
- [ ] regenerate 1/12th degree files again, possibly there is inconsistency in ice sheet and ocean topo that's causing crashses
- [ ] likewise, use more ALE-friendly params in 12th degree and hope it runs longer than 6 hours in ocean only mode.

### Mask
I realised I have been silly and forgot to change the mosaic files (coupler files) for the new run. It's a bit hidden because the file names are not mentioned in any of the namelists...

I followed Angus' instructions [here](https://github.com/COSIMA/mom6-panan/wiki/Preparing-inputs-for-a-new-configuration). I had already done this previously for the 12th degree but I had set the mask to be based on the open cavity topography which is incorrect (confirmed with Olga). 

Instructions: [(FRE-NCtools)](https://github.com/NOAA-GFDL/FRE-NCtools/tree/main)
```
git clone git@github.com:NOAA-GFDL/FRE-NCtools.git 
module load intel-compiler
module load openmpi
module load netcdf
module load nco

autoreconf -i
./configure
make
make install

### (Didn’t finish running, but made the stuff in src so maybe ok)

cd src

cp /g/data/x77/cy8964/mom6/input/input-Olga-grid/topog_Charrassin_sea_ice_from_iceelev_no_edits.nc .
## (need to add dim “tile”)
ncap2 -s 'defdim("ntiles",1)' -A topog_Charrassin_sea_ice_from_iceelev_no_edits.nc topog_Charrassin_sea_ice_from_iceelev_no_edits.nc 
cp /g/data/x77/cy8964/mom6/input/input-Olga-grid/ocean_hgrid.nc .

./make_solo_mosaic --num_tiles 1 --dir . --mosaic_name ocean_mosaic  --tile_file ocean_hgrid.nc --periodx 360

./make_quick_mosaic --input_mosaic ocean_mosaic.nc --mosaic_name grid_spec  --ocean_topog topog_Charrassin_sea_ice_from_iceelev_no_edits.nc 
```

I made the new file consistent with my sea ice mask and this did two things
1. Now with Olga's sea ice and ice area it crashes, which makes sense because now the mask is inconsistent with her files
2. With my files (covereage all consistent) it still crashes
 ^^ Interestingly, they crashed at the same timestep which I didn't expect.

^^ Above problem with Olga's files fixed in layer mode if `DEBUG = False`. Might possibly be fine with `DEBUG = True` in ALE mode with no GL.

**3. Now they both work!!! With `DEBUG = False.`**

I also checked that I could regenerate Olga's mosaic files by using the SIS2 topog (note I think she generated her files from a topo-edited version of this file...). I could regenerate them, the masks were the same, and the model ran.

Probably topo edits need to be applied before the mosaic mask is made, but by comparing the mosaic mask and the sea_ice_geometry mask it didn't look like that applying the min/max depth changed coverage, just depths.

Things to check:
- [x] repeat with `DEBUG = False` for all my new files -> works now!!
- [ ] exact versions used? Have things changed?
- [x] doing topo edits first? Removing isolated ocean points?
- [x] compare files
- [x] do it for 1/12th with the closed cavity topo -> crashed after 6 hours with timestep 150 and ALE mode 50m no GL, and again with timestep 60 (`Ocean velocity has been truncated too many times.`) -> check masks/IS mask coverage....

For 1/12th degree model I got the error
```
FATAL from PE     0: NetCDF: One or more variable sizes violate format constraints: set_netcdf_mode
```
Angus resolved this by adding the following to `input.nml`:
```
&fms2_io_nml
    netcdf_default_format = "netcdf4"
/
```
And then it ran for 2 months. Then I realised it had sea ice still turned off in the `input.nml`, but when I turned it back on all I had to do was drop the DT_ICE_DYNAMICS timestep and then it also ran fine for a month.

### Going back to the config version derived from COSIMA mom6-panan.

I managed to make it work with this version (https://github.com/claireyung/mom6-panan/tree/1_12_IS_ALE_working_faster), which is the 1/10th panan plus the MOM_overrides from the ACCESS-rOM3 config without ice shelves that I'd been using. So, parameters are a bit different. In order for it to work (and also for correctness), there were a few key parameters in `MOM_override_IS` that I added (other than what I knew was important for correct PG and ice shelf initialisation)
```
#override DTFREEZE_DP = -7.75E-08 ! previously had been 0 for linear EOS
#override WRITE_GEOM = 1 !useful for seeing `ocean_geometry` file. 
#override Z_INIT_REMAP_GENERAL = True !otherwise just remaps to zstar coords? But we have sigma shelf zstar
#override PRESSURE_RECONSTRUCTION_SCHEME = 2 ! higher order pressure scheme, possibly not necessary
#override HARMONIC_VISC = True ! calcualtes viscosity based on u thickness calculated with harmonic mean of tracer thicknesses (rather than arithmetic). Helpful for arresting flows out of vanished layers.
#override DTBT_RESET_PERIOD = 0 ! in case it is hardcoded to be longer. Might not be needed after being spun up for a while.

! I needed a seriously short timestep for it to start, after 10 days it was happy with DT=300
#override DT = 180 ! can bump up to 300 after a few days
#override DT_THERM = 180 ! can bump up to 300 after a few days
```
and likewise for `SIS_input`:
```
#override WRITE_GEOM = 1
DT_ICE_DYNAMICS = 180 ! can bump up to 300 after a few days
```

Ideally, your minimum and maximum depths should agree between MOM6 and SIS2:
```
#override MASKING_DEPTH = 0
#override MAXIMUM_DEPTH = 6500
#override MINIMUM_DEPTH = 9.9
```
It is rather slow and expensive, but my MOM6-SIS2 layout is probably not well optimised.

## Summary Table
This table might be helpful for seeing where we're at in the development.

| coord | panan 1/4 | my panan | idealised |
| -- | -- | -- | -- |
|  z* (ALE) |  :x: | :x: | :x: (-> [really cold temps](https://github.com/claireyung/mom6-panAn-iceshelf-tools/issues/5))| 
|$\sigma$ z* (ALE, no incrop in ice shelf) | :white_check_mark: seems ok if no grounding line but Olga's sea ice/ice area |  :white_check_mark:(1/4)/:white_check_mark:(1/12th, Olga params)/ ✅ : (1/12th) | :white_check_mark: (even with grounding line) | 
| layer | :white_check_mark: |  ?? unknown, haven't tested since mosaic mask fix |  :white_check_mark: | 


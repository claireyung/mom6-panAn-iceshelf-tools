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

- Olga has a SMB ice file. I was also getting a `shelf_sfc_mass_flux` variable in the ice shelf ICs of OM3 config. Is this because of JRA forcing??

### Starting from Olga's panan

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

This runs for 1 day (in 1.5hrs walltime) with the debug executable Angus gave me `/g/data/x77/ahg157/exes/MOM6_SIS2/MOM6-dbg-e9dbc6c`. I think the updateCFLtruncation things are each timestep, you can see it progressing. Output looked okay, but this is with a 50m thick grounding line and the FRIS islands look way too big. It crashed with no GL and with 5m GL.

- [ ] check why the ice shelf diags don't have NaNs with ice shelf islands but the ocean diags do

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

- [ ] try use Olga's T-S initial condiitons and regrid them to 1/12th
- [ ] make sure ice shelf area and topo NaNs match
- [ ] check if fill nan value matters, e.g. is fillna 1e-20 like zero? What does Olga use?
- [ ] drop all the timesteps further?

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
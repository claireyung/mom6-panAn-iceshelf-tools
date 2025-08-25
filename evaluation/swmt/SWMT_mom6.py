import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from dask.distributed import Client
import intake
import cmocean as cm
import gsw

import os
import pathlib
import shutil

from dask.distributed import Client

if __name__ == '__main__':

    print('--- start the script...')

    client = Client(threads_per_worker=1)

    esm_datastore = intake.open_esm_datastore(
        "/g/data/ol01/cy8964/access-om3/archive/8km_jra_ryf_obc_Charrassin/experiment_datastore.json",
        columns_with_iterables=[
                "variable",
                "variable_long_name",
                "variable_standard_name",
                "variable_cell_methods",
                "variable_units",
        ] # This is important
    )
    
    # esm_datastore
    
    variables = esm_datastore.unique().variable
    
    mo0_esm_datastore = intake.open_esm_datastore(
        "/g/data/ol01/cy8964/access-om3/datastores/8km_jra_ryf_obc_Charrassin-output000/experiment_datastore.json",
        columns_with_iterables=[
                "variable",
                "variable_long_name",
                "variable_standard_name",
                "variable_cell_methods",
                "variable_units",
        ] # This is important
    )
    
    ds_good_yh = mo0_esm_datastore.search(variable="umo_2d").to_dask(xarray_open_kwargs={'decode_timedelta':True})
    good_yh_coords = ds_good_yh.yh.copy().load()
    ds_good_yq = mo0_esm_datastore.search(variable="vmo_2d").to_dask(xarray_open_kwargs={'decode_timedelta':True})
    good_yq_coords = ds_good_yq.yq.copy().load()
    def reset_y_coords(ds): #thanks to Jemma Jeffree for helping make this work!!
        ds = ds.assign_coords({'yh':good_yh_coords})
        ds = ds.assign_coords({'yq':good_yq_coords})
        return ds
    
    # Make sure these match the available restarts:
    start_time='1908-01-01'
    end_time='1910-12-31'
    time_slice = slice(start_time,end_time)
    lat_slice  = slice(-80,-59)
    lon_slice  = slice(-280,80)
    
    outpath = '/g/data/gv90/fbd581/access-om3-iceshelves/mom6-panAn-iceshelf-tools/Hackathon_evaluation/Figures/'
    
    # DOING SWMT:
    
    def get_variables(expt, freq, start_time, end_time, lon_slice, lat_slice, model = 'mom6'):
    
        # The models require different diagnostics to calculate the heat and salt fluxes.
        # mom6 outputs a net flux, whilst with mom5 we need to work with the separate components.
        model_vars = {
                        "mom6": {
                            "temperature":           ["thetao"],
                            "salinity":              ["so"],
                            "water_flux_into_ocean": ["wfo"],
                            "salt_flux":             ["salt_flux"],
                            "heat_flux":             ["hfds"],
                            "area":                  ["areacello"],
                            "maximum_depth":         ["deptho"],
                        }
                    }
        # Load variables in a dictionary
        ds = {}
        keys = list(model_vars[model].keys())
        for k in keys:
            ds[k] = {}
            for var in model_vars[model][k]:
                if var=='wfo':
                    fileid='access_om3_mom6_2d_wfo_1mon_mean_XXXX'
                elif var=='hfds':
                    fileid='access_om3_mom6_2d_hfds_1mon_mean_XXXX'
                elif var=='salt_flux':
                    fileid='ocean_month'
                elif var=='areacello' or var=='deptho':
                    fileid='access_om3_mom6_static'
                elif var=='thetao' or var=='so':
                    fileid='ocean_month_z'
   
                if var=='wfo' or var=='hfds' or var=='salt_flux' or var=='thetao' or var=='so':
                    ds[k][var] = esm_datastore.search(variable=var, file_id=fileid).to_dask(
                        preprocess=reset_y_coords,xarray_open_kwargs={"chunks": {"time": 1}, 'decode_timedelta':True})[var]
                else:
                    ds[k][var] = esm_datastore.search(variable=var, file_id=fileid).to_dask(
                        preprocess=reset_y_coords,xarray_open_kwargs={'decode_timedelta':True})[var]
                if k in ["area", "maximum_depth"]:
                    ds[k][var] = ds[k][var].sel(xh = lon_slice, yh = lat_slice)
                else:
                    ds[k][var] = ds[k][var].sel(xh = lon_slice, yh = lat_slice, time = slice(start_time, end_time))
    
                # Correct temperatures (if in K convert to C)
                if k == 'temperature' and np.max(ds[k][var]) > 100:
                    ds[k][var] = ds[k][var] - 273.15
    
                # If 3D field, grab the surface
                if 'z_l' in ds[k][var].dims:
                    surface_z = ds[k][var]['z_l'][0].values
                    ds[k][var] = ds[k][var].sel(z_l = 0, method = 'nearest')
    
        # Get temperature and salinity to calculate few other things we'll need later on
        SP = ds['salinity'][model_vars[model]['salinity'][0]]
        CT = ds['temperature'][model_vars[model]['temperature'][0]]
    
        # Calculate pressure
        pressure = gsw.p_from_z(-surface_z, SP['yh']).rename('pressure')
    
        # Calculate absolute salinity
        SA = gsw.SA_from_SP(SP, pressure, SP['xh'], SP['yh']).rename('SA')
    
        # Ensure we have conservative temperature; Convert MOM6's potential temperature to conservative
        if model == 'mom6':
            CT = gsw.CT_from_pt(SA, CT)
            ds['temperature'][model_vars[model]['temperature'][0]].data = CT.values
    
        # Calculate potential density
        pot_rho_1 = gsw.sigma1(SA, CT)#.rename('pot_rho_11')
    
        # Save everything to our dictionary
        ds['pressure'] = pressure
        ds['SA'] = SA
        ds['pot_rho_1'] = pot_rho_1
    
        # Calculate days per month accounting for leap years
        months_standard_noleap = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
        months_standard_leap = np.array([31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
        if 'ryf' or 'panan' in expt:
            nyears = len(np.unique(CT['time.year']))
            days_per_month = np.tile(months_standard_noleap, nyears)
        elif 'iaf' in expt:
            nyears = len(np.unique(CT['time.year']))
            if CT['time.year'][0] % 4 == 0:
                days_per_month = months_standard_leap
            else:
                days_per_month = months_standard_noleap
            for yr in CT['time.year'][::12][1:]:
                if yr % 4 == 0:
                    days_per_month = np.concatenate([days_per_month, months_standard_leap])
                else:
                    days_per_month = np.concatenate([days_per_month, months_standard_noleap])
        days_per_month = xr.DataArray(days_per_month, dims = ['time'], coords = {'time': CT['time']}, name = 'days_per_month')
        ds['days_per_month'] = days_per_month
    
        return ds
    
    ds = get_variables(esm_datastore, '1mon', start_time, end_time, lon_slice, lat_slice, model = 'mom6')
    
    def compute_salt_transformation(ds):
    
        # First retrieve temperature and water_flux as an xarray instead of a dictionary
        CT = xr.Dataset(ds['temperature']).to_array().squeeze().drop_vars('variable')
    
        # Multiply the water flux by absolute salinity to get it in the correct units
        water_flux_into_ocean = xr.Dataset(ds['water_flux_into_ocean']).to_array().squeeze().drop_vars('variable')
        water_flux_into_ocean = ds['SA'] * water_flux_into_ocean
    
        # Caculate the haline contraction coefficient
        haline_contraction = gsw.beta(ds['SA'], CT, ds['pressure']).rename('beta')
    
        # Calculate the net salt flux and multiply by 1000 to convert units
        net_salt_flux = xr.Dataset(ds['salt_flux']).to_array().sum(dim = 'variable') * 1000
    
        # Note that we also multiply pme_river by absolute salinity to have the correct units
        salt_transformation = haline_contraction * (water_flux_into_ocean - net_salt_flux) * ds['days_per_month']
        salt_transformation = salt_transformation.load()
    
        return salt_transformation
    
    def compute_heat_transformation(ds):
    
        # First retrieve temperature as an xarray instead of a dictionary
        CT = xr.Dataset(ds['temperature']).to_array().squeeze().drop_vars('variable')
    
        # Calculate the thermal expansion coefficient
        thermal_expansion = gsw.alpha(ds['SA'], CT, ds['pressure']).rename('alpha')
    
        # Calculate the net surface heating
        net_surface_heating = xr.Dataset(ds['heat_flux']).to_array().sum(dim = 'variable')
    
        # Calculate the heat transformation
        heat_transformation = thermal_expansion * net_surface_heating * ds['days_per_month']
        heat_transformation = heat_transformation.load()
    
        return heat_transformation
    
    def isopycnal_bins(ds, salt_transformation, heat_transformation):
    
        # Next section does a few things. It cycles through isopycnal bins, determines which cells are
        # within the given bin for each month, finds the transformation values for those cells for each month,
        # and sums these through time. You are left with an array of shape (isopyncal bins * lats * lons)
        # where the array associated with a given isopycnal bin is NaN everywhere except where pot_rho_1
        # was within the bin, there it has a time summed transformation value.
    
        # Choose appropriate bin range
        isopycnal_bins = np.arange(31, 33.5, 0.02)  # 125 bins - 31, 33.5, 0.02 (sigma1)
        #isopycnal_bins = np.concatenate([np.arange(25.0, 26.5, 0.05), np.arange(26.5, 28.5, 0.02)])  # 130 bins (sigma0)
        bin_bottoms = isopycnal_bins[:-1]
        isopycnal_bin_mid = (isopycnal_bins[1:] + bin_bottoms) / 2
        isopycnal_bin_diff = np.diff(isopycnal_bins)
    
        pot_rho_1 = ds['pot_rho_1']
    
        results_salt = []
        results_heat = []
    
        for i in range(len(bin_bottoms)):
            # Create binary mask for each bin
            bin_mask = xr.where((pot_rho_1 > bin_bottoms[i]) & (pot_rho_1 <= isopycnal_bins[i + 1]), 1, np.nan)
    
            # Multiply and sum over time
            salt_sum = (salt_transformation * bin_mask).sum(dim='time')
            heat_sum = (heat_transformation * bin_mask).sum(dim='time')
    
            results_salt.append(salt_sum.expand_dims({'isopycnal_bins': [isopycnal_bin_mid[i]]}))
            results_heat.append(heat_sum.expand_dims({'isopycnal_bins': [isopycnal_bin_mid[i]]}))
    
        # Concatenate results along isopycnal dimension
        salt_transformation = xr.concat(results_salt, dim='isopycnal_bins')
        heat_transformation = xr.concat(results_heat, dim='isopycnal_bins')
    
        # Normalise by number of days and bin thickness
        ndays = ds['days_per_month'].sum()
        c_p = 3992.1 # J kg-1 degC-1
    
        salt_transformation /= ndays
        heat_transformation /= (c_p * ndays)
    
        salt_transformation /= isopycnal_bin_diff[:, np.newaxis, np.newaxis]
        heat_transformation /= isopycnal_bin_diff[:, np.newaxis, np.newaxis]
    
        # Overwrite zeros with NANs
        # (Note: the code within the for-loop should provide nans but lazy computing with dask can sometimes give unpredictable results)
        salt_transformation = salt_transformation.where(salt_transformation != 0)
        heat_transformation = heat_transformation.where(heat_transformation != 0)
    
        # Change the sign so that positive means conversion into denser water masses
        salt_transformation *= -1
        heat_transformation *= -1
    
        # Renaming
        salt_transformation.name = "salt_transformation"
        heat_transformation.name = "heat_transformation"
    
        return salt_transformation.load(), heat_transformation.load()
    
    salt_transformation = compute_salt_transformation(ds)
    heat_transformation = compute_heat_transformation(ds)
    
    
    # Set temp_dir to a directory to store ~8GB of temporary output files
    temp_dir = os.path.expandvars("/g/data/gv90/fbd581/access-om3-iceshelves/swmt")
    temp_path = pathlib.Path(temp_dir)
    
    # Ensure a fresh start
    if temp_path.exists():
        shutil.rmtree(temp_path)  # Delete the directory and all its contents
    temp_path.mkdir(parents=True, exist_ok=True)  # Create it again
    
    salt_transformation_binned, heat_transformation_binned = isopycnal_bins(ds, salt_transformation, heat_transformation)
    
    print('Finish binning salt/heat transformation!')
    
    salt_transformation_binned.to_netcdf(pathlib.Path(temp_dir, "binned_salt_transformation_mom6-8km.nc"), mode="w")
    print('Saved salt transf. binned!')
    
    heat_transformation_binned.to_netcdf(pathlib.Path(temp_dir, "binned_heat_transformation_mom6-8km.nc"), mode="w")
    print('Saved heat transf. binned!')

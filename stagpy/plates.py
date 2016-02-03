"""Plots position of subduction and ridge at the surface.

Date: 2016/26/01
"""
import numpy as np
import sys
from . import misc
from .stagdata import BinData, RprofData
from scipy.signal import argrelextrema
from copy import deepcopy
#from statsmodels.nonparametric.smoothers_lowess import lowess

def detectPlates(stagdat_t,stagdat_vp,rprof_data,args):
    Vz = stagdat_vp.fields['w']
    Vphi = stagdat_vp.fields['v']
    Tcell = stagdat_t.fields['t']
    data, nzi = rprof_data.data, rprof_data.nzi
    nz = len(Vz)
    nphi = len(Vz[0])-1
    radius = list(map(float,data[0:nz,0]))
    spherical = args.par_nml['geometry']['shape'].lower() == 'spherical'
    if spherical:
        rcmb = args.par_nml['geometry']['r_cmb']
    else:
        rcmb = 0.
    dphi = 1/nphi

    #calculing radius on the grid
    radiusgrid = len(radius)*[0]
    radiusgrid += [1]
    for i in range(1,len(radius)):
        radiusgrid[i] = 2*radius[i-1]-radiusgrid[i-1]
    for i in range(len(radiusgrid)):
        radiusgrid[i] += rcmb
    for i in range(len(radius)):
        radius[i] += rcmb

    #calculing Tmean
    Tmean=0
    for r in range(len(radius)):
        for phi in range(nphi):
            Tmean+=(radiusgrid[r+1]**2-radiusgrid[r]**2)*dphi*Tcell[r,phi]
    Tmean = Tmean/(radiusgrid[-1]**2-rcmb**2)

    #calculing temperature on the grid and Vzmean/Vrms
    Vrms=0
    Vzmean=0
    Tgrid=np.zeros((nz+1,nphi))
    for phi in range(nphi):
        Tgrid[0,phi]=1
    for z in range(1,nz):
        for phi in range(nphi):
            Tgrid[z,phi]=(Tcell[z-1,phi]*(radiusgrid[z]-radius[z-1])+Tcell[z,phi]*(-radiusgrid[z]+radius[z]))/(radius[z]-radius[z-1])
            Vrms+=(Vz[z,phi,0]**2+Vphi[z,phi,0]**2)/(nphi*nz)
            Vzmean+=abs(Vz[z,phi,0])/(nphi*nz)
    Vrms=Vrms**0.5
    print(Vrms,Vzmean)

    flux_c=nz*[0]
    for z in range(1,nz-1):
        for phi in range(nphi):
            flux_c[z]+=(Tgrid[z,phi]-Tmean)*Vz[z,phi,0]*radiusgrid[z]*dphi

    #checking stagnant lid
    stagnant_lid = True
    max_flx = np.max(flux_c)
    for z in range(nz-int(nz/20),nz):
        if abs(flux_c[z]) > max_flx/50:
            stagnant_lid = False
    if stagnant_lid:
        print('stagnant lid')
        sys.exit()
    else:
        #verifying horizontal plate speed
        dVphi=nphi*[0]
        seuildVphi=10*Vrms
        for phi in range(0,nphi):
            dVphi[phi]=(Vphi[nz-1,phi,0]-Vphi[nz-1,phi-1,0])/((1+rcmb)*dphi)
        limits=[]
        max_dVphi=0
        for i in dVphi:
            if abs(i)>max_dVphi:
                max_dVphi=abs(i)
        for phi in range(0,nphi-1):
            if abs(dVphi[phi])>=abs(dVphi[phi-1]) and abs(dVphi[phi])>=abs(dVphi[phi+1]) and abs(dVphi[phi])>=seuildVphi:
                limits+=[phi]
        if abs(dVphi[nphi-1])>=abs(dVphi[nphi-2]) and abs(dVphi[nphi-1])>=abs(dVphi[0]) and abs(dVphi[nphi-1])>=seuildVphi:
            limits+=[nphi-1]
        print(limits)

        #verifying vertical speed
        k=0
        for i in range(len(limits)):
            Vzm=0
            phi=limits[i-k]
            if phi == nphi-1:
                for z in range(1,nz):
                    Vzm+=(abs(Vz[z,phi,0])+abs(Vz[z,phi-1,0])+abs(Vz[z,0,0]))/(nz*3)
            else:
                for z in range(0,nz):
                    Vzm+=(abs(Vz[z,phi,0])+abs(Vz[z,phi-1,0])+abs(Vz[z,phi+1,0]))/(nz*3)
            seuilVz=Vzmean*0.3
            if Vzm<seuilVz:
                limits.remove(phi)
                k+=1
        print(limits)

        #verifying closeness of limits
        while abs(nphi-limits[-1]+limits[0])<=(nphi/100):
            newlimit=(-nphi+limits[-1]+limits[0])/2
            if newlimit<0:
                newlimit=nphi+newlimit
            limits=[newlimit]+limits[1:-1]
            limits.sort()
        i=1
        while i < len(limits):
            if abs(limits[i-1]-limits[i])<=(nphi/50):
                limits=limits[:i-1]+[(limits[i-1]+limits[i])/2]+limits[i+1:]
            else:
                i+=1


        print(limits)
        print('\n')
        for i in range(len(limits)):
            limits[i]=int(limits[i])
    return(limits,nphi,dVphi)

def plot_plates(args,velocity,temp,conc,age,timestep):
        plt = args.plt
        lw=1
        meanvrms=605.0 ### to be changed
        ttransit=1.78e15 ### My
        yearins=2.16E7
        dsa=0.05
        plot_age=True
        velocityfld=velocity.fields['v']
        tempfld=temp.fields['t']
        concfld=conc.fields['c']
        agefld=age.fields['a']

          #if stgdat.par_type == 'vp':
           # fld = fld[:, :, 0]
        newline = tempfld[:, 0, 0]
        tempfld = np.vstack([tempfld[:, :, 0].T, newline]).T
        newline = concfld[:, 0, 0]
        concfld = np.vstack([concfld[:, :, 0].T, newline]).T
        newline = agefld[:, 0, 0]
        agefld = np.vstack([agefld[:, :, 0].T, newline]).T

        indsurf=np.argmin(abs((1-dsa)-np.array(temp.r_coord)))-4 #### we are a bit below the surface; delete "-some number" to be just below the surface (that is considered plane here); should check if you are in the mechanical/thermal boundary layer
        indcont=np.argmin(abs((1-dsa)-np.array(velocity.r_coord)))-10 ### depth to detect the continents
        continents=np.ma.masked_where(np.logical_or(concfld[indcont,:-1]<3,concfld[indcont,:-1]>4),concfld[indcont,:-1])
        continentsall=continents/continents # masked array, only continents are true
        #if(vp.r_coord[indsurf]>1.-dsa):
        #    print 'WARNING lowering index for surface'
        #    indsurf=indsurf-1
        #if verbose_figures:
        ##################### age just below the surface
        if plot_age:
            age_surface=np.ma.masked_where(agefld[indsurf,:]<0.00001,agefld[indsurf,:])
            age_surface_dim=age_surface*meanvrms*ttransit/yearins/1.e6

        ph_coord=conc.ph_coord
        ph_coord=np.append(ph_coord,conc.ph_coord[1]-conc.ph_coord[0])
        # ############################################################### velocity
        vphi=velocityfld[:,:,0]
        vph2=0.5*(vphi+np.roll(vphi,1,1)) # interpolate to the same phi
        dvph2=(np.diff(vph2[indsurf,:])/(ph_coord[0]*2.))
        #dvph2=dvph2/amax(abs(dvph2))  # normalization
        # ############################################################## heat flux
        #heatflux=-(tempfld[indsurf,:-1]-tempfld[indsurf-1,:-1])/(temp.r_coord[indsurf]-temp.r_coord[indsurf-1])

        # ############################################################## plotting
        f,(ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True,figsize=(10,12))
        ax1.plot(ph_coord[:-1],concfld[indsurf,:-1],color='g',linewidth=lw,label='Conc')
        ax2.plot(ph_coord[:-1],tempfld[indsurf,:-1],color='m',linewidth=lw,label='Temp')
        ax3.plot(ph_coord[:-1]+ph_coord[0],dvph2,color='c',linewidth=lw,label='dv')
        ###ax4.plot(ph_coord[:-1],viscfld[indsurf,:-1],color='y',linewidth=lw,label='Visc')
        ax4.plot(ph_coord[:-1],vph2[indsurf,:-1],linewidth=lw,label='Vel')

        ax1.fill_between(ph_coord[:-1],continents,1.,facecolor='gray',alpha=0.25)
        ax2.fill_between(ph_coord[:-1],continentsall,0.,facecolor='gray',alpha=0.25)
        ax2.set_ylim(0,1)
        ax3.fill_between(ph_coord[:-1],continentsall*round(1.5*np.amax(dvph2),1),round(np.amin(dvph2)*1.1,1),facecolor='gray',alpha=0.25)
        ax3.set_ylim(round(np.amin(dvph2)*1.1,1),round(1.5*np.amax(dvph2),1))
        ax4.fill_between(ph_coord[:-1],continentsall*5e3,-5000,facecolor='gray',alpha=0.25)
        ax4.set_ylim(-5000,5000)

        ax1.set_ylabel("Concentration")
        ax2.set_ylabel("Temperature")
        ax3.set_ylabel("dv")
        ax4.set_ylabel("Velocity")

        # ################################################################## prepare stuff to find trenches and ridges
        myorder=500
        myorderdv=40
        myorderdv2=10# threshold
        arglessT=argrelextrema(tempfld[indsurf,:-1], np.less,order=myorder,mode='wrap')[0]
        maskbigdvel=np.amin(dvph2)*0.5 # user, putting threshold
        pom2=deepcopy(dvph2)
        pom2[pom2>-40000]=0   # user putting threshold
        arglessDV=argrelextrema(pom2, np.less,order=myorderdv,mode='wrap')[0]
        ###dvph2smooth = np.lowess(dvph2, ph_coord[:-1], is_sorted=True, frac=0.004, it=0) # smoothing derivatives first
        masksmalldvel=np.amax(dvph2)*0.4 # user, putting threshold
        ###pom2=deepcopy(dvph2smooth[:,1])
        #pom2[pom2<masksmalldvel]=0
        arggreatDV=argrelextrema(pom2, np.greater,order=myorderdv2,mode='wrap')[0]
        #arglessETA=argrelextrema(viscfld[indsurf,:-1], np.less,order=myorder,mode='wrap')[0]
        argmax=argrelextrema(tempfld[indsurf,:-1], np.greater)

        # ################################################ position of trench and ridges using the velocity derivative
        trench=ph_coord[arglessDV]
        agetrench=age_surface_dim[arglessDV] # age of the trench
        ridge=ph_coord[arggreatDV]

        ################### elimination of ridges that are too close to trench
        argdel=[]
        if (len(trench)>0 and len(ridge)>0):
           for ii in arange(len(ridge)):
               mdistance=amin(abs(trench-ridge[ii]))
               if mdistance<0.016:
                   argdel.append(ii)
           if len(np.array(argdel))>0:
               print('deleting from ridge',trench,ridge[argdel])
               ridge=delete(ridge,np.array(argdel))
               arggreatDV=delete(arggreatDV,np.array(argdel))

        ## ################################################ plotting
        ax2.plot(ph_coord[arglessT],tempfld[indsurf,arglessT],'ro')
        ax3.plot(ph_coord[arglessDV],dvph2[arglessDV],'ro')
        ax3.plot(ph_coord[arggreatDV],dvph2[arggreatDV],'go')
        ###ax4.plot(ph_coord[arglessETA],viscfld[indsurf,arglessETA],'ro')
        ax1.set_title(timestep)

        ############################## topography
        par_type='sc'
        fname=misc.file_name(args,par_type).format(temp.step)+'.dat'   #name of the file to read
        depth_mantle=2890.0 # in km
        topo=np.genfromtxt(fname)
        topo[:,1]=topo[:,1]/(1.-dsa) #### rescaling topography !!!!!!!!!!!!!!!
        topomin=-50
        topomax=50
        #majorLocator   = MultipleLocator(20)

        ax31=ax3.twinx()
        ax31.set_ylabel("Topography [km]")
        ax31.plot(topo[:,0],topo[:,1]*depth_mantle,color='black',alpha=0.4)
        ax31.set_ylim(topomin,topomax)

        ax41=ax4.twinx()
        ax41.set_ylabel("Topography [km]")
        ax41.axhline(y=0,xmin=0,xmax=2*np.pi,color='black',ls='dashed',alpha=0.7)

        for ii in np.arange(len(trench)):
           ax41.axvline(x=trench[ii],ymin=topomin,ymax=topomax,color='red',ls='dashed',alpha=0.4)
        for ii in np.arange(len(ridge)):
           ax41.axvline(x=ridge[ii],ymin=topomin,ymax=topomax,color='green',ls='dashed',alpha=0.8)
        ax41.plot(topo[:,0],topo[:,1]*depth_mantle,color='black',alpha=0.7)
        ax41.set_ylim(topomin,topomax)

        ax1.set_xlim(0,2*np.pi)

        figname=misc.out_name(args,'surf').format(temp.step)+'.pdf'
        plt.savefig(figname,format='PDF')
        plt.close()

        ######################################################### plotting only velocity and topography
        f,(ax1, ax2) = plt.subplots(2, 1, sharex=True,figsize=(12,8))
        ax1.plot(ph_coord[:-1],vph2[indsurf,:-1],linewidth=lw,label='Vel')
        #ax1.fill_between(ph_coord[:-1],continentsall*5e3,-5000,facecolor='#8B6914',alpha=0.2)
        ax1.axhline(y=0,xmin=0,xmax=2*np.pi,color='black',ls='dashed',alpha=0.4)
        ax1.set_ylim(-5000,5000)
        ax1.set_ylabel("Velocity")
        topomax=30
        topomin=-60
        for ii in np.arange(len(trench)):
           ax1.axvline(x=trench[ii],ymin=topomin,ymax=topomax,color='red',ls='dashed',alpha=0.8)
           ################# detection of the distance in between subduction and continent
           ph_coord_noendpoint=ph_coord[:-1]
           distancecont=min(abs(ph_coord_noendpoint[continentsall==1]-trench[ii]))
           argdistancecont=np.argmin(abs(ph_coord_noendpoint[continentsall==1]-trench[ii]))
           continentpos=ph_coord_noendpoint[continentsall==1][argdistancecont]
           ########## do i have a ridge in between continent edge and trench?
           if (len(ridge)>0):
            if ((min(abs(continentpos-ridge))>distancecont)):
             ph_trench_subd.append(trench[ii])
             age_subd.append(agetrench[ii])
             ph_cont_subd.append(continentpos)
             distance_subd.append(distancecont)
             times_subd.append(temp.ti_ad)
             if ((continentpos-trench[ii])<0): ###continent is on the left
                ax1.annotate("",xy=(trench[ii]-distancecont,2000),xycoords='data',
                        xytext=(trench[ii],2000),textcoords='data',
                        arrowprops=dict(arrowstyle="->",shrinkA=0,shrinkB=0))
             else: ### continent is on the right
                ax1.annotate("",xy=(trench[ii]+distancecont,2000),xycoords='data',
                        xytext=(trench[ii],2000),textcoords='data',
                        arrowprops=dict(arrowstyle="->",shrinkA=0,shrinkB=0))

           #ax1.arrow(0,4500,1,0,width=100,head_width=100,length_includes_head=True)
           #ax1.arrow(trench[ii],2000,distancecont,0,length_includes_head=True)
           #ax1.arrow(trench[ii],2000,-distancecont,0,length_includes_head=True)
           ax1.axvline(x=trench[ii],ymin=topomin,ymax=topomax,color='red',ls='dashed',alpha=0.8)
           #ax1.arrow(trench[ii],2000,-distancecont,0)
           ax1.grid()
        for ii in np.arange(len(ridge)):
           ax1.axvline(x=ridge[ii],ymin=topomin,ymax=topomax,color='green',ls='dashed',alpha=0.8)
        ax2.set_ylabel("Topography [km]")
        ax2.plot(topo[:,0],topo[:,1]*depth_mantle,color='black')
        #ax2.axhline(y=0,xmin=0,xmax=2*pi,color='black',ls='dashed',alpha=0.4)
        ax2.set_xlim(0,2*np.pi)
        dtopo=deepcopy(topo[:,1]*depth_mantle)
        mask=dtopo>0
        water=deepcopy(dtopo)
        water[mask]=0
        #ax2.fill_between(ph_coord[:-1],dtopo,0,where=dtopo<0,facecolor='blue',alpha=0.25)
        #ax2.fill_between(ph_coord[:-1],topomin,dtopo,facecolor='grey',alpha=0.25)
        #ax2.fill_between(ph_coord[:-1],continentsall*topomax,topomin,facecolor='#8B6914',alpha=0.2)
        ax2.set_ylim(topomin,topomax)
        for ii in np.arange(len(trench)):
           ax2.axvline(x=trench[ii],ymin=topomin,ymax=topomax,color='red',ls='dashed',alpha=0.8)
        for ii in np.arange(len(ridge)):
           ax2.axvline(x=ridge[ii],ymin=topomin,ymax=topomax,color='green',ls='dashed',alpha=0.8)
        #ax1.set_xlim(0,2*np.pi)
        ax1.set_title(timestep)
        figname=misc.out_name(args,'surfvel').format(temp.step)+'.pdf'
        plt.savefig(figname,format='PDF')
        plt.close()

        ######################################################### plotting only velocity and age at surface
        if plot_age:
         f,(ax1, ax2) = plt.subplots(2, 1, sharex=True,figsize=(12,8))
         ax1.plot(ph_coord[:-1],vph2[indsurf,:-1],linewidth=lw,label='Vel')
        # ax1.fill_between(ph_coord[:-1],continentsall*5e3,-5000,facecolor='#8B6914',alpha=0.2)
         ax1.axhline(y=0,xmin=0,xmax=2*np.pi,color='black',ls='dashed',alpha=0.4)
         ax1.set_ylim(-5000,5000)
         ax1.set_ylabel("Velocity")
         agemax=280
         agemin=0
         for ii in np.arange(len(trench)):
           ax1.axvline(x=trench[ii],ymin=agemin,ymax=agemax,color='red',ls='dashed',alpha=0.8)
         for ii in np.arange(len(ridge)):
           ax1.axvline(x=ridge[ii],ymin=agemin,ymax=agemax,color='green',ls='dashed',alpha=0.8)
         ax2.set_ylabel("Age [My]")
         ax2.plot(ph_coord[:-1],age_surface_dim[:-1],color='black') ### in dimensions
         ax2.set_xlim(0,2*np.pi)
         ax2.fill_between(ph_coord[:-1],continentsall*agemax,agemin,facecolor='#8B6914',alpha=0.2)
         ax2.set_ylim(agemin,agemax)
         for ii in np.arange(len(trench)):
          ax2.axvline(x=trench[ii],ymin=agemin,ymax=agemax,color='red',ls='dashed',alpha=0.8)
         for ii in np.arange(len(ridge)):
           ax2.axvline(x=ridge[ii],ymin=agemin,ymax=agemax,color='green',ls='dashed',alpha=0.8)
         ax1.set_title(timestep)
         figname=misc.out_name(args,'surfage').format(temp.step)+'.pdf'
         plt.savefig(figname,format='PDF')
         plt.close()
        return None


def plates_cmd(args):
    """find positions of trenches and subductions
       using velocity field (velocity derivation)
    """
    """plots the number of plates over a designated lapse of time"""

    nb_plates=[]
    for timestep in range(*args.timestep):
        velocity = BinData(args, 'v', timestep)
        temp = BinData(args, 't', timestep)
        rprof_data=RprofData(args)
        if args.vzcheck:
            plt = args.plt
            limits, nphi, dVphi = detectPlates(temp, velocity,
                    rprof_data, args)
            limits.sort()
            sizePlates=[limits[0]+nphi-limits[-1]]
            for l in range(1,len(limits)):
                sizePlates+=[limits[l]-limits[l-1]]
            l=len(limits)*[max(dVphi)]
            plt.figure(timestep)
            plt.subplot(121)
            plt.plot(dVphi)
            plt.scatter(limits,l,color='red')
            plt.subplot(122)
            plt.hist(sizePlates,10,(0,nphi/2))
            plt.savefig('plates'+ str(timestep) + '.pdf',format='PDF')
            nb_plates+=[len(limits)]
            plt.close(timestep)
        else:
            conc = BinData(args, 'c', timestep)
            age = BinData(args, 'a', timestep)
            plot_plates(args,velocity,temp,conc,age,timestep)
    if args.timeprofile and args.vzcheck:
        plt.figure(-1)
        plt.axis([0,int((args.timestep[1]-args.timestep[0])/args.timestep[2]),0,np.max(nb_plates)])
        plt.plot(nb_plates)
        plt.savefig('herewego.pdf',format='PDF')
        plt.close(-1)
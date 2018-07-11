pro decont_map
;+
; NAME:
;     decont_map
; PURPOSE:
;     Creates a decontamination map of a cluster-CMD, using the 
;	  CMD of the nearest field stars.
; EXPLANATION:
;     The process is similar to that described in Mighell+96. 
;
; CALLING SEQUENCE:
;      decont_map
;
; INPUTS:
;      cluster catalog - catalog of cluster stars with specific
;      					 format (see input catalog format)
;      MCPS corrected catalog - catalog containing extinctin corrected 
;	   				     MCPS stars to select field
;	   color and mag bins - bin sizes of the color and magnitude axis
;	   CMD color selection - either B-V vs V or V-I vs I
;	   maximum uncertainty - upper error of the magnitude estimation
;
; OUTPUTS:
;      decontamination map - a file containing the decontamination 
;	   					maps of all clusters in the cluster catalog
;
; DEPENDENCIES:
;	   GCIRC.PRO and ASTROLIB are required.
;
; HISTORY:
;	   Written by Theo Bitsakis (IRyA/UNAM) - 2016
;	   v.2 In the field stars does not contain any star that has been 
;		   included at any cluster (input lmc_corr_wo_clust_stars.cat)
;	   v.3 Changed BV for UV and included condition for u and i mags to
;		   to be larger than 0.0 since the extinction correction created
;		   negative values (subtracted from 0.0)
;-

name_in=''
name_out=''
name_in_clust=''
cluster_name=''
read,name_in,prompt='Give cluster STAR catalog: '
read,name_in_clust,prompt='Give cluster catalog: '
read,name_out,prompt='Give Output catalog: '
col=''
lala2:
read,col,prompt='Which color (UV, BV, VI): '
if col ne 'UV' and col ne 'uv' and col ne 'BV' and col ne 'bv' and col ne 'VI' and col ne 'vi' then goto, lala2

;progress,0.0,/reset ; reset before next use 

;READING ALL INPUT FILES
;;;;;;;;;;;;;;;;;;;;;;;;;;
readcol,name_in,clid1,ra1,dec1,dis1,u_cor1,ue1,b_cor1,be1,v_cor1,ve1,i_cor1,ie1,format='a,f,f,f,f,f,f,f,f,f,f,f'
print,'READ '+name_in
readcol,name_in_clust,clid2,ra2,dec2,rad2,format='a,f,f,f'
print,'READ '+name_in_clust
readcol,'lmc_corr_wo_clust_stars.cat',ra3,dec3,mu3,mue3,mb3,mbe3,mv3,mve3,mi3,mie3,format='f,f,f,f,f,f,f,f,f,f',/quick ;Extinction corrected MCPS catalogue
print,'READ MCPS corr'

openw,10,name_out
printf,10,'# Clid     Bin No.      Col_min        Col_max       Mag_min        Mag_max         Probabilty (to be in cluster)',format='(a)'

	n_st_cl=n_elements(clid1)-1  ;number of cluster stars
	n_cl=n_elements(clid2)-1 ;number of clusters

for i_clus=0,n_cl do begin ;loop over all clusters
	
		cluster_name=clid2[i_clus]
		rad_clust=rad2[i_clus]
	
	;SELECT FIELD REGION
	;;;;;;;;;;;;;;;;;;;;;
	;size of field region is [0.40deg,0.40deg]-[0.10dec,0.10deg] (big-small box to exclude cluster)
		i_field=where(((ra3 gt ra2[i_clus]-0.25 and ra3 lt ra2[i_clus]-0.08) and (dec3 gt dec2[i_clus]-0.20 and dec3 lt dec2[i_clus]+0.20)) or ((ra3 lt ra2[i_clus]+0.25 and ra3 gt ra2[i_clus]+0.08) and (dec3 gt dec2[i_clus]-0.20 and dec3 lt dec2[i_clus]+0.20)) or ((ra3 gt ra2[i_clus]-0.08 and ra3 lt ra2[i_clus]+0.08) and (dec3 gt dec2[i_clus]-0.20 and dec3 lt dec2[i_clus]-0.05)) or ((ra3 gt ra2[i_clus]-0.08 and ra3 lt ra2[i_clus]+0.08) and (dec3 gt dec2[i_clus]+0.05 and dec3 lt dec2[i_clus]+0.20)))
		u3=mu3[i_field]
		ue3=mue3[i_field]
		b3=mb3[i_field]
		be3=mbe3[i_field]
		v3=mv3[i_field]
		ve3=mve3[i_field]
		i3=mi3[i_field]
		ie3=mie3[i_field]

		gcirc,2,ra2[i_clus]-0.25,dec2[i_clus]-0.20,ra2[i_clus]+0.25,dec2[i_clus]-0.20,disf1 ;Big box
		gcirc,2,ra2[i_clus]-0.25,dec2[i_clus]+0.20,ra2[i_clus]+0.25,dec2[i_clus]+0.20,disf2

		gcirc,2,ra2[i_clus]-0.08,dec2[i_clus]-0.05,ra2[i_clus]+0.08,dec2[i_clus]-0.05,disf3 ;Small box
		gcirc,2,ra2[i_clus]-0.08,dec2[i_clus]+0.05,ra2[i_clus]+0.08,dec2[i_clus]+0.05,disf4

		Bigx=((disf1+disf2)/2.)/3600. ;RA mean in degress
		Bigy=0.40 ;Dec in degress
		Smallx=((disf3+disf4)/2.)/3600. ;RA mean in degress
		Smally=0.10 ;Dec in degress
	
	;SELECT COLOR
	;;;;;;;;;;;;;;
	
	;Select colors of cluster and field stars below the allowed uncertainty 
		uncer=0.25 ; maximum allowed photometric uncertainty 
		if col eq 'UV' or col eq 'uv' then begin
			cmd1=where(clid1 eq cluster_name and (ue1 lt uncer and ve1 lt uncer) and u_cor1 gt 0.0)
			cmd2=where(mu3 gt 0.0 and ue3 lt uncer and ve3 lt uncer)
		endif
		if col eq 'BV' or col eq 'bv' then begin
			cmd1=where(clid1 eq cluster_name and (be1 lt uncer and ve1 lt uncer) and b_cor1 gt 0.0)
			cmd2=where(mb3 gt 0.0 and be3 lt uncer and ve3 lt uncer)
		endif
		if col eq 'VI' or col eq 'vi' then begin
			cmd1=where(clid1 eq cluster_name and (ie1 lt uncer and ve1 lt uncer) and i_cor1 gt 0.0)
			cmd2=where(mi3 gt 0.0 and ve3 lt uncer and ie3 lt uncer)
		endif
	
		 u_cl = u_cor1[cmd1] ;cluster photometry
		ue_cl = ue1[cmd1]
		 b_cl = b_cor1[cmd1] 
		be_cl = be1[cmd1]
		 v_cl = v_cor1[cmd1]
		ve_cl = ve1[cmd1]
		 i_cl = i_cor1[cmd1]
		ie_cl = ie1[cmd1]
	
		 u_fi = u3[cmd2] ;field photometry
		ue_fi = ue3[cmd2]
		 b_fi = b3[cmd2]
		be_fi = be3[cmd2]
		 v_fi = v3[cmd2]
		ve_fi = ve3[cmd2]
		 i_fi = i3[cmd2]
		ie_fi = ie3;[cmd2]
	
		area_cluster=!pi*(rad_clust)^2
		area_field=((Bigx*Bigy)-(Smallx*Smally)) ; Field size box (Big box - small box)
		normal=(area_cluster/area_field) ;area normalization factor
	
	;MAKE COLOR-MAG DIAGRAMS
	;;;;;;;;;;;;;;;;;;;;;;;;;
		if col eq 'UV' or col eq 'uv' then begin
			x_min=-1.0
			x_max=2.0
			y_min=12.0
			y_max=22.0
			bin_col=0.5;2.*sqrt(2.*uncer^2) ;select bin sizes
			bin_mag=1.0;4.*uncer
	
			col_cl=u_cl-v_cl
			cole_cl=sqrt(ue_cl^2+ve_cl^2)
			y_cl=v_cl
			ye_cl=ve_cl
	
			col_fi=u_fi-v_fi
			cole_fi=sqrt(ue_fi^2+ve_fi^2)
			y_fi=v_fi
			ye_fi=ve_fi
		endif 
	
		if col eq 'BV' or col eq 'bv' then begin
			x_min=-1.0
			x_max=2.0
			y_min=12.0
			y_max=22.0
			bin_col=0.5;2.*sqrt(2.*uncer^2) ;select bin sizes
			bin_mag=1.0;4.*uncer
	
			col_cl=b_cl-v_cl
			cole_cl=sqrt(be_cl^2+ve_cl^2)
			y_cl=v_cl
			ye_cl=ve_cl
	
			col_fi=b_fi-v_fi
			cole_fi=sqrt(be_fi^2+ve_fi^2)
			y_fi=v_fi
			ye_fi=ve_fi
		endif 

		if col eq 'VI' or col eq 'vi' then begin
			x_min=-1.0
			x_max=3.0
			y_min=12.00
			y_max=21.00
			bin_col=0.5;4.*sqrt(2.*uncer^2)
			bin_mag=1.0;6.*uncer
	
			col_cl=v_cl-i_cl
			cole_cl=sqrt(ie_cl^2+ie_cl^2)
			y_cl=i_cl
			ye_cl=ie_cl
	
			col_fi=v_fi-i_fi
			cole_fi=sqrt(ve_fi^2+ie_fi^2)
			y_fi=i_fi
			ye_fi=ie_fi
		endif 
	
	; Bin the CMDs
		sz_x=fix((x_max-x_min)/bin_col)-1 ;number of bins in x,y axis (integer)
		sz_y=fix((y_max-y_min)/bin_mag)-1
		
		totbin=0
		for ibin=0,sz_x do begin
			for jbin=0,sz_y do begin
	
				x_axis=x_min+ibin*bin_col
				y_axis=y_min+jbin*bin_mag
	
				st_count1=where((col_cl ge x_axis and col_cl lt (x_axis+bin_col)) and (y_cl ge y_axis and y_cl lt (y_axis+bin_mag))) ;find cluster i-bin
				st_count2=where((col_fi ge x_axis and col_fi lt (x_axis+bin_col)) and (y_fi ge y_axis and y_fi lt (y_axis+bin_mag))) ;find field i-bin
	
				posib=1.0-(n_elements(st_count2)*normal/n_elements(st_count1)) ;area normalized probability of stars being in cluster
				if posib lt 0.0 then posib=0.
				totbin=totbin+1
	
				printf,10,cluster_name,totbin,x_axis,(x_axis+bin_col),y_axis,(y_axis+bin_mag),posib,format='(a,i,f,f,f,f,f)'
				;printf,10,cluster_name,totbin,x_axis,(x_axis+bin_col),y_axis,(y_axis+bin_mag),posib,n_elements(st_count1),n_elements(st_count2),normal,format='(a,i,f,f,f,f,f,i,i,f)'

			endfor
		endfor
		per=(i_clus*1./n_cl)*100 ;progress
		progress,per
	
endfor
	print,''
	print,'--- Created Decontamination maps ---'


close,10

end
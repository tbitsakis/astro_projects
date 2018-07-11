pro decont_map_2
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
;	   v.4 It decontaminates separately depending on the position of the
;		   stars in the cluster (R1, R2, R3 radii)
;-

; Radii to be used in decontamination
R1=0.5
R2=0.9
R3=1.5


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
print,'FINISH READING '+name_in
readcol,name_in_clust,clid2,ra2,dec2,rad2,format='a,f,f,f'
print,'FINISH READING '+name_in_clust
readcol,'lmc_corr_wo_clust_stars_2R.cat',ra3,dec3,mu3,mue3,mb3,mbe3,mv3,mve3,mi3,mie3,format='f,f,f,f,f,f,f,f,f,f',/quick ;Extinction corrected MCPS catalogue
print,'FINISH READING MCPS corrected table (without cluster stars)'

openw,10,name_out
printf,10,'# Clid     Bin No.      Col_min        Col_max       Mag_min        Mag_max         Probabilty (at R1, R2 and R3 cluster radii)',format='(a)'

	n_st_cl=n_elements(clid1)-1  ;number of cluster stars
	n_cl=n_elements(clid2)-1 ;number of clusters

for i_clus=0,n_cl do begin ;loop over all clusters
	
		cluster_name=clid2[i_clus]
		rad_clust=rad2[i_clus]
		dis1=dis1/3600.
	

	;SELECT FIELD REGION
	;;;;;;;;;;;;;;;;;;;;;
	; Despite we define a big box of size ra+/-0.25 deg around the RA and dec+/-0.2 around the Dec and a small of ra+/-0.08 and dec+/-0.05
	; in reality the RA distances change with Dec so the great circle distance is given by gcirc.pro
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
			cmd1_1=where(clid1 eq cluster_name and (ue1 lt uncer and ve1 lt uncer) and u_cor1 gt 0.0 and (dis1 lt R1*rad_clust)) ;All stars in radius <1sigma (70%) of cluster radius
			cmd1_2=where(clid1 eq cluster_name and (ue1 lt uncer and ve1 lt uncer) and u_cor1 gt 0.0 and (dis1 gt R1*rad_clust and dis1 lt R2*rad_clust)) ;All stars in radius <2sigma (90%) of cluster radius
			cmd1_3=where(clid1 eq cluster_name and (ue1 lt uncer and ve1 lt uncer) and u_cor1 gt 0.0 and (dis1 gt R2*rad_clust and dis1 lt R3*rad_clust)) ;All stars in radius >3sigma, 150% of cluster radius
			cmd_fi=where(mu3 gt 0.0 and ue3 lt uncer and ve3 lt uncer) ;For the field
		endif
		if col eq 'BV' or col eq 'bv' then begin
			cmd1_1=where(clid1 eq cluster_name and (be1 lt uncer and ve1 lt uncer) and b_cor1 gt 0.0 and (dis1 lt R1*rad_clust)) ;All stars in radius <1sigma (70%) of cluster radius
			cmd1_2=where(clid1 eq cluster_name and (be1 lt uncer and ve1 lt uncer) and b_cor1 gt 0.0 and (dis1 gt R1*rad_clust and dis1 lt R2*rad_clust)) ;All stars in radius <2sigma (90%) of cluster radius
			cmd1_3=where(clid1 eq cluster_name and (be1 lt uncer and ve1 lt uncer) and b_cor1 gt 0.0 and (dis1 gt R2*rad_clust and dis1 lt R3*rad_clust)) ;All stars in radius >3sigma, 150% of cluster radius
			cmd_fi=where(mb3 gt 0.0 and be3 lt uncer and ve3 lt uncer) ;For the field
		endif
		if col eq 'VI' or col eq 'vi' then begin
			cmd1_1=where(clid1 eq cluster_name and (ie1 lt uncer and ve1 lt uncer) and i_cor1 gt 0.0 and (dis1 lt R1*rad_clust)) ;All stars in radius <1sigma (70%) of cluster radius
			cmd1_2=where(clid1 eq cluster_name and (ie1 lt uncer and ve1 lt uncer) and i_cor1 gt 0.0 and (dis1 gt R1*rad_clust and dis1 lt R2*rad_clust)) ;All stars in radius <2sigma (90%) of cluster radius
			cmd1_3=where(clid1 eq cluster_name and (ie1 lt uncer and ve1 lt uncer) and i_cor1 gt 0.0 and (dis1 gt R2*rad_clust and dis1 lt R3*rad_clust)) ;All stars in radius >3sigma, 150% of cluster radius
			cmd_fi=where(mi3 gt 0.0 and ve3 lt uncer and ie3 lt uncer) ;For the field
		endif
	
		 u_cl1 = u_cor1[cmd1_1] ;cluster photometry - region 1
		ue_cl1 = ue1[cmd1_1]
		 b_cl1 = b_cor1[cmd1_1] 
		be_cl1 = be1[cmd1_1]
		 v_cl1 = v_cor1[cmd1_1]
		ve_cl1 = ve1[cmd1_1]
		 i_cl1 = i_cor1[cmd1_1]
		ie_cl1 = ie1[cmd1_1]
	
		 u_cl2 = u_cor1[cmd1_2] ;cluster photometry - region 2
		ue_cl2 = ue1[cmd1_2]
		 b_cl2 = b_cor1[cmd1_2] 
		be_cl2 = be1[cmd1_2]
		 v_cl2 = v_cor1[cmd1_2]
		ve_cl2 = ve1[cmd1_2]
		 i_cl2 = i_cor1[cmd1_2]
		ie_cl2 = ie1[cmd1_2]

		 u_cl3 = u_cor1[cmd1_3] ;cluster photometry - region 3
		ue_cl3 = ue1[cmd1_3]
		 b_cl3 = b_cor1[cmd1_3] 
		be_cl3 = be1[cmd1_3]
		 v_cl3 = v_cor1[cmd1_3]
		ve_cl3 = ve1[cmd1_3]
		 i_cl3 = i_cor1[cmd1_3]
		ie_cl3 = ie1[cmd1_3]

		 u_fi = u3[cmd_fi] ;field photometry
		ue_fi = ue3[cmd_fi]
		 b_fi = b3[cmd_fi]
		be_fi = be3[cmd_fi]
		 v_fi = v3[cmd_fi]
		ve_fi = ve3[cmd_fi]
		 i_fi = i3[cmd_fi]
		ie_fi = ie3[cmd_fi]
	
		area_cluster_1=!pi*(rad_clust*R1)^2 ;inner circle
		area_cluster_2=!pi*((rad_clust*R2)^2-(rad_clust*R1)^2) ;circular ring
		area_cluster_3=!pi*((rad_clust*R3)^2-(rad_clust*R2)^2) ;circular ring
		area_field=((Bigx*Bigy)-(Smallx*Smally)) ; Field size box (Big box - small box)

		normal1=(area_cluster_1/area_field) ;area normalization factor, 1 region
		normal2=(area_cluster_2/area_field) ;area normalization factor, 2 region
		normal3=(area_cluster_3/area_field) ;area normalization factor, 3 region
	
	;MAKE COLOR-MAG DIAGRAMS
	;;;;;;;;;;;;;;;;;;;;;;;;;
		if col eq 'UV' or col eq 'uv' then begin
			x_min=-1.0
			x_max=2.0
			y_min=12.0
			y_max=22.0
			bin_col=0.25;2.*sqrt(2.*uncer^2) ;select bin sizes
			bin_mag=0.5;4.*uncer
	
			col_cl1=u_cl1-v_cl1
			cole_cl1=sqrt(ue_cl1^2+ve_cl1^2)
			y_cl1=v_cl1
			ye_cl1=ve_cl1
	
			col_cl2=u_cl2-v_cl2
			cole_cl2=sqrt(ue_cl2^2+ve_cl2^2)
			y_cl2=v_cl2
			ye_cl2=ve_cl2

			col_cl3=u_cl3-v_cl3
			cole_cl3=sqrt(ue_cl3^2+ve_cl3^2)
			y_cl3=v_cl3
			ye_cl3=ve_cl3

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
			bin_col=0.25;2.*sqrt(2.*uncer^2) ;select bin sizes
			bin_mag=0.5;4.*uncer
	
			col_cl1=b_cl1-v_cl1
			cole_cl1=sqrt(be_cl1^2+ve_cl1^2)
			y_cl1=v_cl1
			ye_cl1=ve_cl1
	
			col_cl2=b_cl2-v_cl2
			cole_cl2=sqrt(be_cl2^2+ve_cl2^2)
			y_cl2=v_cl2
			ye_cl2=ve_cl2

			col_cl3=b_cl3-v_cl3
			cole_cl3=sqrt(be_cl3^2+ve_cl3^2)
			y_cl3=v_cl3
			ye_cl3=ve_cl3

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
			bin_col=0.25;4.*sqrt(2.*uncer^2)
			bin_mag=0.5;6.*uncer
	
			col_cl1=v_cl1-i_cl1
			cole_cl1=sqrt(ie_cl1^2+ie_cl1^2)
			y_cl1=i_cl1
			ye_cl1=ie_cl1
	
			col_cl2=v_cl2-i_cl2
			cole_cl2=sqrt(ie_cl2^2+ie_cl2^2)
			y_cl2=i_cl2
			ye_cl2=ie_cl2
	
			col_cl3=v_cl3-i_cl3
			cole_cl3=sqrt(ie_cl3^2+ie_cl3^2)
			y_cl3=i_cl3
			ye_cl3=ie_cl3
	
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
	
				st_count1=where((col_cl1 ge x_axis and col_cl1 lt (x_axis+bin_col)) and (y_cl1 ge y_axis and y_cl1 lt (y_axis+bin_mag))) ;find cluster i-bin, 1 region
				st_count2=where((col_cl2 ge x_axis and col_cl2 lt (x_axis+bin_col)) and (y_cl2 ge y_axis and y_cl2 lt (y_axis+bin_mag))) ;find cluster i-bin, 2 region
				st_count3=where((col_cl3 ge x_axis and col_cl3 lt (x_axis+bin_col)) and (y_cl3 ge y_axis and y_cl3 lt (y_axis+bin_mag))) ;find cluster i-bin, 3 region
				st_count_fi=where((col_fi ge x_axis and col_fi lt (x_axis+bin_col)) and (y_fi ge y_axis and y_fi lt (y_axis+bin_mag))) ;find field i-bin
	
				posib1=1.0-(n_elements(st_count_fi)*normal1/n_elements(st_count1)) ;area normalized probability of stars being in cluster, 1 region
				posib2=1.0-(n_elements(st_count_fi)*normal2/n_elements(st_count2)) ;area normalized probability of stars being in cluster, 2 region
				posib3=1.0-(n_elements(st_count_fi)*normal3/n_elements(st_count3)) ;area normalized probability of stars being in cluster, 3 region
				if posib1 lt 0.0 then posib1=0.01 ;Avoiding negative numbers
				if posib2 lt 0.0 then posib2=0.01
				if posib3 lt 0.0 then posib3=0.01
				if n_elements(st_count1) eq 1 then begin ;Avoiding empty bins
					if st_count1 eq -1 then posib1=0.01
				endif
				if n_elements(st_count2) eq 1 then begin 
					if st_count2 eq -1 then posib2=0.01
				endif
				if n_elements(st_count3) eq 1 then begin 
					if st_count3 eq -1 then posib3=0.01
				endif

				totbin=totbin+1
	
				printf,10,cluster_name,totbin,x_axis,(x_axis+bin_col),y_axis,(y_axis+bin_mag),posib1,posib2,posib3,format='(a,i,f,f,f,f,f,f,f)'

			endfor
		endfor
		per=(i_clus*1./n_cl)*100 ;progress
		progress,per
	
endfor
	print,''
	print,'--- Created Decontamination maps ---'


close,10

end
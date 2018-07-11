pro match_var_rad
;+
; NAME:
;     match_var_rad
; PURPOSE:
;     Finds all objects of a table (RA2, DEC2) that are found in a circle of center RA1 and DEC1 
;     and a given radius. It saves all the results in a file, indicating all objects found in every 
;	  circle.
; EXPLANATION:
;     Input position are Decimal RA-DEC, and radii in Degrees. 
;
; CALLING SEQUENCE:
;      match_var_rad, ra1, dec1, ra2, dec2, radius
;
; INPUTS:
;      ra1  -- Right ascension or longitude of point 1
;      dec1  -- Declination or latitude of point 1
;      ra2  -- Right ascension or longitude of point 2
;      dec2  -- Declination or latitude of point 2
;	   radius -- Radius of each circle corresponding to point 1
;
; OUTPUTS:
;      OUT  -- A file containing all matched points 2 with an index   
;	   of those found in the same group.
;
; DEPENDENCIES:
;	   GCIRC.PRO and ASTROLIB are required.
;
; HISTORY:
;	   Written by Theo Bitsakis (IRyA/UNAM) - 2016
;-

;readcol,'total_NUV_M2_IR1_M24.cat',ra1,dec1,radius,format='f,f,f' ;cluster catalogue
name_in=''
name_out=''
nm=''

read,name_in,prompt='Give input filename: '
read,name_out,prompt='Give output filename: '

readcol,name_in,nm,ra1,dec1,radius,format='a,f,f,f' ;field region catalogue
readcol,'/fs/galaxias/other0/tbitsakis/DATA/LMC/optical/MCPS_phot_cat/lmc.cat',ra2,dec2,mu,mue,mb,mbe,mv,mve,mi,mie,fl,mj,mje,mh,mhe,mk,mke,fl2,format='f,f,f,f,f,f,f,f,f,f,i,f,f,f,f,f,f,i',/quick ;MCPS catalogue


	n1=n_elements(ra1)-1
	radius=radius*3600.

	openw,10,name_out

	for i1=0,n1 do begin

		j2=where((ra2 gt ra1[i1]-0.1 and ra2 lt ra1[i1]+0.1) and (dec2 gt dec1[i1]-0.1 and dec2 lt dec1[i1]+0.1)) ;defines a smaller region where the iteration is going to take place

		ra2_j=ra2(j2)
		dec2_j=dec2(j2)
		mu_j=mu(j2)
		mue_j=mue(j2)
		mb_j=mb(j2)
		mbe_j=mbe(j2)
		mv_j=mv(j2)
		mve_j=mve(j2)
		mi_j=mi(j2)
		mie_j=mie(j2)
		fl_j=fl(j2)
		mj_j=mj(j2)
		mje_j=mje(j2)
		mh_j=mh(j2)
		mhe_j=mhe(j2)
		mk_j=mk(j2)
		mke_j=mke(j2)
		fl2_j=fl2(j2)

		n2=n_elements(ra2_j)-1

		for i2=0,n2 do begin

			gcirc,2,ra1[i1],dec1[i1],ra2_j[i2],dec2_j[i2],distance

			if distance le radius[i1] then printf,10,nm[i1],ra2_j[i2],dec2_j[i2],distance,mu_j[i2],mue_j[i2],mb_j[i2],mbe_j[i2],mv_j[i2],mve_j[i2],mi_j[i2],mie_j[i2],fl_j[i2],mj_j[i2],mje_j[i2],mh_j[i2],mhe_j[i2],mk_j[i2],mke_j[i2],fl2_j[i2],format='(a,f,f,f,f,f,f,f,f,f,f,f,i,f,f,f,f,f,f,i)' ;prints cluster stars

		endfor

	endfor

	close,10


end


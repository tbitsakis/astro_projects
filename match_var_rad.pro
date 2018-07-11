pro match_var_rad,ra1,dec1,ra2,dec2,radius
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
;      out_cross.cat  -- A file containing all matched points 2 with an index   
;	   of those found in the same group.
;
; DEPENDENCIES:
;	   GCIRC.PRO and ASTROLIB are required.
;
; HISTORY:
;	   Written by Theo Bitsakis (IRyA/UNAM) - 2016
;-

	n1=n_elements(ra1)-1

	openw,10,'out_cross.cat'

	for i1=0,n1 do begin

		j2=where((ra2 gt ra1[i1]-0.3 and ra2 lt ra1[i1]+0.3) and (dec2 gt dec1[i1]-0.3 and dec2 lt dec1[i1]+0.3)) ;defines a smaller region where the iteration is going to take place

		ra2_j=ra2(j2)
		dec2_j=dec2(j2)

		n2=n_elements(ra2_j)-1

		for i2=0,n2 do begin

			gcirc,2,ra1[i1],dec1[i1],ra2_j[i2],dec2_j[i2],distance

			if distance le radius[i1] then printf,10,i1,ra2_j[i2],dec2_j[i2],distance,mu[i2],mue[i2],mb[i2],mbe[i2],mv[i2],mve[i2],mi[i2],mie[i2],fl[i2],mj[i2],mje[i2],mh[i2],mhe[i2],mk[i2],mke[i2],fl2[i2],format='(i,f,f,f,f,f,f,f,f,f,f,f,i,f,f,f,f,f,f,i)' ;prints cluster stars

		endfor

	endfor

	close,10


end



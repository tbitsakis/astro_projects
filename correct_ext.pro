pro ext_corr
;+
; NAME:
;     ext_corr
; PURPOSE:
;     It finds the position and temperature (colour) of a star in the MCPS catalog and using the 
;     extinction maps from Zaritsky+04, it is correcting for the effect of attenuation.
;
; EXPLANATION:
;     Input star positions and photometry and the fits extinction maps. Details in the tables
;	  6 Schlegel+98 and 1 Pei+92.
;
; CALLING SEQUENCE:
;      ext_corr
;
; INPUTS:
;	   ra, dec, photometry for each star
;	   extinction maps (hot-cold) fits
;
; OUTPUTS:
;      output file with new stellar colours extinction corrected   
;
; DEPENDENCIES:
;	   ASTROLIB is required.
;
; HISTORY:
;	   Written by Theo Bitsakis (IRyA/UNAM) - 2016
;	   Revision to include U-band
;-

; For Cluster stars - uncomment next lines 

	name_in=''
	name_out=''
	clid=''
	read,name_in,prompt='Give input file: '
	read,name_out,prompt='Give output file (without extention): '

	readcol,name_in,clid,ra,dec,dis,u,ue,b,be,v,ve,mi,mie,fl,j,je,h,he,k,ke,fl2,format='a,f,f,f,f,f,f,f,f,f,f,f,i,f,f,f,f,f,f,i'
	openw,10,name_out+'_ext_hot.cat'
	openw,20,name_out+'_ext_cold.cat'

; For Field stars - uncomment next lines 
	; readcol,'Stars_field.cat',clid,ra,dec,dis,u,ue,b,be,v,ve,mi,mie,fl,j,je,h,he,k,ke,fl2,format='i,f,f,f,f,f,f,f,f,f,f,f,i,f,f,f,f,f,f,i'
	; openw,10,'Stars_field_extinction_hot.cat'
	; openw,20,'Stars_field_extinction_cold.cat'


	im_hot=mrdfits('$lmc/optical/mcps_extinction/lmc_hotav.fits',0,h1)
	im_cold=mrdfits('$lmc/optical/mcps_extinction/lmc_coolav.fits',0,h2)

	col=b-v
	Rv=3.16 ;Pei+92 Table 2 for LMC 

; For hot-stars apply the following corrections
	print,'START HOT'
	i_hot=where(col lt 0.20)

	clid_hot=clid(i_hot) 
	ra_hot=ra(i_hot)
	dec_hot=dec(i_hot)
	xh=ra_hot*0
	yh=ra_hot*0
	adxy,h1,ra_hot,dec_hot,xh,yh ;Use an image header to compute X and Y positions, given the RA and Dec (or longitude, latitude) in decimal degrees

	dis_hot=dis(i_hot)
	u_hot=u(i_hot)
	ue_hot=ue(i_hot)
	b_hot=b(i_hot)
	be_hot=be(i_hot)
	v_hot=v(i_hot)
	ve_hot=ve(i_hot)
	mi_hot=mi(i_hot)
	mie_hot=mie(i_hot)

	Av_hot=im_hot[xh,yh] ;find the Av from the map - corrections from Schlegel+98 table 6
	Ebv_hot=Av_hot/Rv
	Au_hot=1.664*Av_hot ;U_landolt
	Ab_hot=Ebv_hot+Av_hot
	Ai_hot=0.610*Av_hot ;Gunn-i
	u_cor_hot=u_hot-Au_hot	
	b_cor_hot=b_hot-Ab_hot
	v_cor_hot=v_hot-Av_hot
	i_cor_hot=mi_hot-Ai_hot

; For cold-stars apply the following corrections
	print,'START COLD'
	i_cold=where(col gt 0.20)

	clid_cold=clid(i_cold)
	ra_cold=ra(i_cold)
	dec_cold=dec(i_cold)
	xc=ra_cold*0
	yc=ra_cold*0
	adxy,h2,ra_cold,dec_cold,xc,yc

	dis_cold=dis(i_cold)
	u_cold=u(i_cold)
	ue_cold=ue(i_cold)
	b_cold=b(i_cold)
	be_cold=be(i_cold)
	v_cold=v(i_cold)
	ve_cold=ve(i_cold)
	mi_cold=mi(i_cold)
	mie_cold=mie(i_cold)

	Av_cold=im_cold[xc,yc] ;find the Av from the map
	Ebv_cold=Av_cold/Rv
	Au_cold=1.664*Av_cold ;U_landolt
	Ab_cold=Ebv_cold+Av_cold
	Ai_cold=0.610*Av_cold ;Gunn-i
	u_cor_cold=u_cold-Au_cold
	b_cor_cold=b_cold-Ab_cold
	v_cor_cold=v_cold-Av_cold
	i_cor_cold=mi_cold-Ai_cold

	n_hot=n_elements(clid_hot)-1
	n_cold=n_elements(clid_cold)-1


	print,'DONE'
	print,'Loops'

	print,10,'#ClusID     RA             Dec            Distance       U               e_U                 B               e_B           V               e_V           I               e_I     '
	print,20,'#ClusID     RA             Dec            Distance       U               e_U                 B               e_B           V               e_V           I               e_I     '

	for i1=0L,n_hot do begin
		printf,10,clid_hot[i1],ra_hot[i1],dec_hot[i1],dis_hot[i1],u_cor_hot[i1],ue_hot[i1],b_cor_hot[i1],be_hot[i1],v_cor_hot[i1],ve_hot[i1],i_cor_hot[i1],mie_hot[i1],format='(a,f,f,f,f,f,f,f,f,f,f,f)'
	endfor

	for i2=0L,n_cold do begin
		printf,20,clid_cold[i2],ra_cold[i2],dec_cold[i2],dis_cold[i2],u_cor_cold[i2],ue_cold[i2],b_cor_cold[i2],be_cold[i2],v_cor_cold[i2],ve_cold[i2],i_cor_cold[i2],mie_cold[i2],format='(a,f,f,f,f,f,f,f,f,f,f,f)'
	endfor

	close,10,20

end
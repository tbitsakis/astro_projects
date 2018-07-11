pro compl_test
; NAME:
;		compl_test
;
; PURPOSE:
;		It reads the DAOPHOT output and performs the completeness test.
;
; CALLING SEQUENCE:
;		compl_test
;
; INPUT:
;		A catalog containing x,y and mag of all stars detected by DAOPHOT (both original and artificial), 
; 		for each cluster of different spatial density.
;
; RESULT:
;		A catalog containing the completeness for each cluster of given spatial density.
;
; HISTORY:
;       Written, 2017, Theo Bitsakis, IRyA-UNAM.
;-

;=================== Edit only here =======================
; Edit and change only the following parameters
	catalog="input_images.cat" ; Input image catalog
	N_stars=5 ; Number of stars to input per image 
	N_image=10000 ; Number of images to generate each time
	s_radius=5 ; Search radius for each star (in px)
	mag_up=13 ; Upper magnitude to test completeness
	mag_low=23 ; Lower magnitude to test completenes
	mag_bin=0.5 ; Bin of the magnitude scale

	marg_size=2 ; Avoid margins (in px)
	col_up=2.0  ; Upper color limits
	col_low=-1.2  ; Lower color limits
;==========================================================

	readcol,catalog,nm,format='(a24)'

	n_clust=n_elements(nm)-1

	compl_final=fltarr(1+(mag_low-mag_up)/mag_bin) ; Creates empty array of completeness
	mag_final=mag_up+mag_bin*findgen(mag_low-mag_up+1) ; Creates array of magnitudes

	for i1=0,n_clust do begin

		im0=nm[i1]+'.als'
		readcol,im0,x0,y0,mag0,mag_err0,format='f,f,f,f' ; Reads photometry of original image

		for i2=0,N_image do begin

			im1=nm[i1]+'_'+strn(i2+1)+'.als'
			readcol,im1,x1,y1,mag1,mag_err1,format='f,f,f,f' ; Reads photometry of n artificial image

			srcor,x0,y0,x1,y1,s_radius,out0,out1 ; Cross-correlates the two catalogs and find common stars

			mag0_arr=mag0(out0) ; Only the mags of the matched stars of the first catalog are considered
			mag1_arr=mag1(out1) ; Only the mags of the matched stars of the artificial catalog are considered

			hist0=histogram(mag0_arr,binsize=mag_bin,min=mag_up,max=mag_low)
			hist1=histogram(mag1_arr,binsize=mag_bin,min=mag_up,max=mag_low)

			compl=hist1*1./hist0

		endfor

		compl_final=compl_final+compl

	endfor

	name_out=nm[i]+'_compl.dat'
	openw,10,name_out

	for j=0,n_elements(compl_final)-1 do printf,10,mag_final[j],compl_final[j],format='(f,f)'

	close,10


end
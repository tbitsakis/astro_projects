pro star_count,name_in,name_out

; NAME:
;		star_count
;
; PURPOSE:
;		Detection of star clusters. Counts the number of stars in a given kernel using a weight map and detects overdensities over  
;		the local background. Then smooths in the size of a cluster.
;
; CALLING SEQUENCE:
;		star_count, input_image, output_image
;
; INPUT:
;		input_image (2D array), output_image, the input sigma is variable and depends on the Noise (per band), s_smooth
;       WARNING: sigma is not the S/N (which is S/N = (Signal-Noise)*Area/sqrt(Noise*Area)) but rather the (Signal-Noise)/Noise.
;
; RESULT:
;		A gaussian smoothed image containing only the congregations of stars.
;
; HISTORY:
;       Written, 2016, Theo Bitsakis, IRyA-UNAM.
;-


;====== Edit only here ==============
; Edit and change only the following parameters
	x_box=25   ;box of star counts
	x_box2=200 ;box of noise counts
	s_smooth=10;gaussian smoothing sigma
;====================================

	im=mrdfits(name_in,0,h)

	sz=size(im)
	x_tot=sz[1]
	y_tot=sz[2]
	progress,0.0,/reset ; reset before next use 
	print,''
	print,'################# PARAMETERS #################'
	print,'--------> BOX SIZE ',2*x_box
	print,'--> NOISE BOX SIZE ',2*x_box2
	print,'----> SIGMA SMOOTH ',s_smooth
	print,'##############################################'
	print,'START...'

	for i=0,x_tot-1 do begin

		for j=0,y_tot-1 do begin

			if im(i,j) eq 0 then goto, endloop ;Skip pixels without stars

			signal=0
			thres=0

			i2_min=i-x_box
			i2_max=i+x_box
			j2_min=j-x_box
			j2_max=j+x_box
			if i2_min lt 0 then i2_min=0
			if i2_max gt x_tot-1 then i2_max=x_tot-1
			if j2_min lt 0 then j2_min=0
			if j2_max gt y_tot-1 then j2_max=y_tot-1	

			signal=total(im[i2_min:i2_max,j2_min:j2_max]) / (1d*(i2_max-i2_min)*(j2_max-j2_min)*1000.) ;calculate total in box (d for number overflow)

			i3_min=i-x_box2
			i3_max=i+x_box2
			j3_min=j-x_box2
			j3_max=j+x_box2
			if i3_min lt 0 then i3_min=0
			if i3_max gt x_tot-1 then i3_max=x_tot-1
			if j3_min lt 0 then j3_min=0
			if j3_max gt y_tot-1 then j3_max=y_tot-1	

			noise=total(im[i3_min:i3_max,j3_min:j3_max]) / (1d*(i3_max-i3_min)*(j3_max-j3_min)*1000.) ;calculate noise star density normalized by box area

;=====================================================================================
;                                   SNR Definitions  
;=====================================================================================
; To change the sensitivity of the detection, change only term c only (y=c+bx+ax^2)


		; IRAC 3.6um filter
			;sigma=3.75-1406.97*noise+247383.0*noise^2-1.96155e+07*noise^3+5.63594e+08*noise^4 ;creates variable sigma (for low S/N maps) using polynomial fit (original c=)

		; GALEX NUV
			;if noise gt 0.00050 then sigma=2.30-393.335*noise
			;if noise le 0.00050 then sigma=4
			;if noise le 0.00024 then sigma=12

		; SWIFT UVW2
			sigma=3.51245-1231.36*noise+116793.0*noise^2 ;creates variable sigma (for low S/N maps) (original c=3.61245)
;=====================================================================================
;=====================================================================================

			thres=sigma*noise
			if (signal-noise) lt thres then im[i,j]=1001.

			endloop:

		endfor

		per=(i*1./x_tot)*100 ;progress
		progress,per

	endfor

     print,''
	 print,'SETTING NON-CLUSTER STARS TO ZERO'
	 ii=where(im eq 1001.)
	 im(ii)=0.

	 print,'BEGIN SMOOTHING...'

	 im2=gauss_smooth(im,s_smooth)
	 print,'WRITING FITS...'

	writefits,name_out,im2,h

	bell, 5

end 



pro get_compl
; NAME:
;		get_compl
;
; PURPOSE:
;		It reads the DAOPHOT output and performs the completeness test.
;
; CALLING SEQUENCE:
;		get_compl
;
; INPUT:
;		It reads the completeness catalog of each cluster and gets the parameters of
;	    the Pritchet function using chi^2 minimization.
;
; RESULT:
;		A catalog containing the best values of the Pritchet function per cluster.
;		It also plots the best fit to the completeness of each cluster.
;
; HISTORY:
;       Written, 2017, Theo Bitsakis, IRyA-UNAM.
;-

;=================== Edit only here =======================
; Edit and change only the following parameters
	catalog="input_images.cat" ; Input image catalog
	a_min=1 ; Minimum Pritchet a value (McLaughlin+94 Table 4)
	a_max=3 ; Maximum Pritchet a value
	a_step=0.05 ; Step of a value 
	mlim_min=13 ; Minimum Pritchet mlim value
	mlim_max=23 ; Maximum Pritchet mlim value
	mlim_step=0.5 ;  Step of mlim value
;==========================================================

	readcol,catalog,nm,format='(a24)'
	n_clust=n_elements(nm)-1

	openw,10,'Pritchet_param.dat'

	for i1=0,n_clust do begin

		name_in=nm[i1]+'_compl.dat'

		readcol,name_in,mag_final,compl_final,format='f,f'

		f_pritchet=compl_final*0.0 ; Create the f_pritchet array
		chi_count=10000. ; Set an initially high chi^2 value
		a_fin=-999. & mlim_fin=-999. ; Set initial values

		for a=a_min,a_max,a_step do begin 
			for mlim=mlim_min,mlim_max,mlim_step do begin

				f_pritchet=0.5(1-a*(mag_final-mlim)/sqrt(1+a^2*(mag_final-mlim)^2)) ; The Pritchet function
				chi=total((compl_final-f_pritchet)^2/f_pritchet) ; The chi of Pritchet and completeness functions

				if chi lt chi_count then a_fin=a & mlim_fin=mlim ; Saving the values that minimize the chi

			endfor
		endfor

		printf,10,nm[i1],a_fin,mlim_fin,format='(a,f,f)'

		plotsym,0,1
		set_plot,'ps'
		device,filename=nm[i1]+'_Pritchet.ps',/color
			plot,mag_final,compl_final,xr=[23,13],yr=[0,1.1],xtitle='Mag [mag]',ytitle='Completeness',charsize=1.4
			oplot,mag_final,f_pritchet,color=3,thick=3
		device,/close
		set_plot,'x'

	endfor


end

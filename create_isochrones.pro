pro isoc
; Reads the isochrone list from Bruzual (stochastic/*cmd) and creates
; new isochrones to input to the CMD fitting script (with n number of stars)
; The code finds the mean V, i-band magnitude in each of the n-steps of the process.
; T. Bitsakis

    in_dir='stochastic/'
    out_dir='my_isoc_full/'

    readcol,'input_list.txt',names,id,ages,format='a,i,f' ;input isoc_list
    progress,0.0,/reset ; reset before next use 

    n_names=n_elements(names)-1

    for i=0,n_names do begin

            name=''
            name_new=''
            name_in=in_dir+names[i]

            readcol,name_in,mass,Uj,Bj,Vj,Rc,Ic,gG,rG,iG,zG,iso,format='f,f,f,f,f,f,f,f,f,f,i'
            print,'FINISH READING: ',i,'/',n_names

            age=alog10(ages[i])

            col=Bj-Vj
            mag=Vj 

            col_min=-0.4
            col_max=1.6
            mag_min=-3.75
            mag_max=3.5

            i_step_col=0.001 ;Bin size x-Axis DEFAULT 0.01
            i_step_mag=0.01 ;Bin size y-Axis DEFAULT 0.01

            name_new=out_dir+'cb2016_z008_'+strn(age)+'yr.cmd'
            openw,10,name_new

            printf,10,'#     Age     U_johnson   B_johnson       V_johnson      i_Gunn'

            for is1=col_min,col_max,i_step_col do begin
                for is2=mag_min,mag_max,i_step_mag do begin 

                    i_iG=where((col gt is1 and col le is1+i_step_col) and (mag gt is2 and mag le is2+i_step_mag))

                    if n_elements(i_iG) le 1 then begin
                        if i_iG eq -1 then goto, telos
                    endif
                    	    Uj_new=mean(Uj(i_iG))
                            Bj_new=mean(Bj(i_iG))
                            Vj_new=mean(Vj(i_iG))
                            iG_new=mean(iG(i_iG))
                            printf,10,age,Uj_new,Bj_new,Vj_new,iG_new,format='(f,f,f,f,f)'
                            telos:
                endfor
            endfor

            close,10
            ;print,'DONE: ',i,'/',n_names
        per=(i*1./n_names)*100 ;progress
        progress,per
    endfor


end
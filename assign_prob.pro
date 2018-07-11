pro assign_prob
;+
; NAME:
;     assign_prob
; PURPOSE:
;     Reads the decontamination map of each cluster and assigns with  
;         a probability to their stars to belong to the cluster (not field)
; EXPLANATION:
;     The decontamination map is created by decomp_map.pro (according to Mighell+96) 
;
; CALLING SEQUENCE:
;      assign_prob
;
; INPUTS:
;      cluster catalog - catalog of cluster stars with specific
;                                        format (see input catalog format)
;      field catalog - catalog of field stars
;      field regions - catalog containing only the field region 
;                                          centers
;          color and mag bins - bin sizes of the color and magnitude axis
;          CMD color selection - either B-V vs V or V-I vs I
;          maximum uncertainty - upper error of the magnitude estimation
;
; OUTPUTS:
;      star catalog with cluster membership probability for each star 
;
; DEPENDENCIES:
;          ASTROLIB is required.
;
; HISTORY:
;          Written by Theo Bitsakis (IRyA/UNAM) - 2016
;          v.2 Modified changing BV for UV and include 
;		   	   only positive mags
;-

name_in=''
name_decon=''
name_out=''
st_name=''
read,name_in,prompt='Give cluster STAR catalog: '
read,name_decon,prompt='Give decontamination map: '
read,name_out,prompt='Give Output STAR catalog: '

progress,0.0,/reset ; reset before next use 

uncer=0.25
col=''
lala2:
read,col,prompt='Which color (UV, BV, VI): '
if col ne 'UV' and col ne 'uv' and col ne 'BV' and col ne 'bv' and col ne 'VI' and col ne 'vi' then goto, lala2

readcol,name_in,clid1,ra1,dec1,dis1,u_cor1,ue1,b_cor1,be1,v_cor1,ve1,i_cor1,ie1,format='a,f,f,f,f,f,f,f,f,f,f,f'
readcol,name_decon,clid2,bin,colmin,colmax,magmin,magmax,prob,format='a,i,f,f,f,f,f'

ii=where(i_cor1 le 0)
ie1(ii)=999.

openw,10,name_out

if col eq 'UV' or col eq 'uv' then begin
        print,'You have selected the UV-vs-V decontamination map'
       	printf,10,'#ClID    RA     Dec    U_corr     e_U_corr    V_corr   e_V_corr   Probability(Membership probability)'

        i_uncer=where((ue1 lt uncer and ve1 lt uncer) and (u_cor1 gt 0.0 and v_cor1 gt 0.0))

        clid1=clid1[i_uncer]
        ra1=ra1[i_uncer]
        dec1=dec1[i_uncer]
        dis1=dis1[i_uncer]
        u_cor1=u_cor1[i_uncer]
        ue1=ue1[i_uncer]
        v_cor1=v_cor1[i_uncer]
        ve1=ve1[i_uncer]

        n_st=n_elements(ra1)-1

        for i=0,n_st do begin
        
                st_name=clid1[i]
                st_col=u_cor1[i]-v_cor1[i] ;star color
                st_mag=v_cor1[i] ;star mag

                star_bin=where(clid2 eq st_name and (colmin le st_col and colmax gt st_col) and (magmin le st_mag and magmax gt st_mag)) ;bin of decont map that contains the probability
                st_prob=prob(star_bin) ;probability to be assigned to the star
                if n_elements(star_bin) eq 0 then st_prob=0.05 ;in case it is out of range

                printf,10,st_name,ra1[i],dec1[i],u_cor1[i],ue1[i],v_cor1[i],ve1[i],st_prob,format='(a,f,f,f,f,f,f,f)'

                per=(i*1./n_st)*100 ;progress
                progress,per

        endfor
endif

if col eq 'BV' or col eq 'bv' then begin
        print,'You have selected the UV-vs-V decontamination map'
        printf,10,'#ClID    RA     Dec    U_corr     e_U_corr    V_corr   e_V_corr   Probability(Membership probability)'

        i_uncer=where((be1 lt uncer and ve1 lt uncer) and (b_cor1 gt 0.0 and v_cor1 gt 0.0))

        clid1=clid1[i_uncer]
        ra1=ra1[i_uncer]
        dec1=dec1[i_uncer]
        dis1=dis1[i_uncer]
        b_cor1=b_cor1[i_uncer]
        be1=be1[i_uncer]
        v_cor1=v_cor1[i_uncer]
        ve1=ve1[i_uncer]

        n_st=n_elements(ra1)-1

        for i=0,n_st do begin
        
                st_name=clid1[i]
                st_col=b_cor1[i]-v_cor1[i] ;star color
                st_mag=v_cor1[i] ;star mag

                star_bin=where(clid2 eq st_name and (colmin le st_col and colmax gt st_col) and (magmin le st_mag and magmax gt st_mag)) ;bin of decont map that contains the probability
                st_prob=prob(star_bin) ;probability to be assigned to the star
                if n_elements(star_bin) eq 0 then st_prob=0.05 ;in case it is out of range

                printf,10,st_name,ra1[i],dec1[i],b_cor1[i],be1[i],v_cor1[i],ve1[i],st_prob,format='(a,f,f,f,f,f,f,f)'

                per=(i*1./n_st)*100 ;progress
                progress,per

        endfor
endif


if col eq 'VI' or col eq 'vi' then begin
        print,'You have selected the VI-vs-I decontamination map'
       	printf,10,'#ClID    RA     Dec    V_corr     e_V_corr    i_corr   e_i_corr   Probability(Membership probability)'

        i_uncer=where((ve1 lt uncer and ie1 lt uncer) and (v_cor1 gt 0.0 and i_cor1 gt 0.0))

        clid1=clid1[i_uncer]
        ra1=ra1[i_uncer]
        dec1=dec1[i_uncer]
        dis1=dis1[i_uncer]
        v_cor1=v_cor1[i_uncer]
        ve1=ve1[i_uncer]
        i_cor1=i_cor1[i_uncer]
        ie1=ie1[i_uncer]

        n_st=n_elements(ra1)-1

        for i=0,n_st do begin
        
                st_name=clid1[i]
                st_col=v_cor1[i]-i_cor1[i] ;star color
                st_mag=i_cor1[i] ;star mag

                star_bin=where(clid2 eq st_name and (colmin le st_col and colmax gt st_col) and (magmin le st_mag and magmax gt st_mag)) ;bin of decont map that contains the probability
                st_prob=prob(star_bin) ;probability to be assigned to the star
                if n_elements(star_bin) eq 0 then st_prob=0.05 ;in case it is out of range

                printf,10,st_name,ra1[i],dec1[i],v_cor1[i],ve1[i],i_cor1[i],ie1[i],st_prob,format='(a,f,f,f,f,f,f,f)'
                
                per=(i*1./n_st)*100 ;progress
                progress,per

        endfor
endif

close,10


end

pro reg_stars
;+
; NAME:
;     reg_stars
; PURPOSE:
;     Creates a region file containing all stars of a cluster
;
; CALLING SEQUENCE:
;      reg_stars
;
; INPUTS:
;      cluster star catalog - catalog that contains all cluster stars
;      cluster id - id of a given cluster (string)
;
; OUTPUTS:
;      region file with all stars of a given cluster 
;
; DEPENDENCIES:
;	   ASTROLIB is required.
;
; HISTORY:
;	   Written by Theo Bitsakis (IRyA/UNAM) - 2016
;-

	name_in=''
	sel=''
	read,name_in,prompt='Give input file: '
	readcol,name_in,clid,ra,dec,dis,u,ue,b,be,v,ve,mi,mie,fl1,mj,mje,h,he,k,ke,fl2,format='(a,f,f,f,f,f,f,f,f,f,f,f,i,f,f,f,f,f,f,i)'

	lala:
	read,sel,prompt='Give cluster id: '

	ii=where(clid eq sel)
	n=n_elements(ii)-1
	print,'Number of stars= ',n
	rac=ra(ii)
	decc=dec(ii)

	nm=''
	nm=sel+'.reg'
	openw,10,nm
        printf,10,'# Region file format: DS9 version 4.1'
        printf,10,'global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1'
        printf,10,'fk5'

	for j=0,n do printf,10,'circle(',rac[j],',',decc[j],',',0.5,'")'

	close,10

	ans=''
	read,ans,prompt='Continue? (y/n) '
	if ans eq 'y' then goto, lala


end
pro sex2dec

	name_in=''
	name_out=''

	read,name_in,prompt='Input file: '
	read,name_out,prompt='Output file: '

	readcol,name_in,hr,mi,se,de,am,as,type,amaj,format='f,f,f,f,f,f,a,f'

	ra=(abs(hr*15.0)+abs(mi*0.25)+abs(se*0.00416666))*(hr/(abs(hr)))
	dec=(abs(de)+abs(am/60.0)+abs(as/3600.0))*(de/(abs(de)))

	rad=amaj/60.0

	num=n_elements(hr)-1

	openw,10,name_out
	printf,10,'# RA     Dec     Type    Rad(deg)'

	for i=0,num do printf,10,ra[i],dec[i],type[i],rad[i],format='(f,f,a,f)'

	close,10

end
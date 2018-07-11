pro nir_phot
;This program was made to perform NIR data reduction and photometry. Insert the 
;darks, flats, and data images and then by clicking always on the same star, 
;you can set the x and y offsets. Then it sums all the images and divides by the 
;total time to give the final in counts/sec. Finally, you can add some imformation 
;to the image headers.
;T. Bitsakis (2011) [e-mail: bitsakis@physics.uoc.gr]

print,""
print,"######################### READING THE DARKS #########################"
print,'====================================================================='
darks=''
read,darks,prompt='Give the DARKS-xx: '
dark_files=FINDFILE(darks+'*.fit')
n_dark=n_elements(dark_files)
sum_d=0.
for i=0,n_dark-1 do begin
    f2=readfits(darks+'_'+strn(i+1)+'.fit')
    sum_d=sum_d+f2
endfor
dark=sum_d/n_dark

print,""
print,"######################### READING THE FLATS #########################"
print,'====================================================================='
flats=''
read,flats,prompt='Give the FLATS-xx: '
f1=readfits(flats+'_1.fit')
f2=readfits(flats+'_2.fit')
f3=readfits(flats+'_3.fit')
flat=MYMEDIAN(f1,f2,f3)
flat1=flat-dark
flat_f=(flat1/median(flat1))

print,""
print,"############### READING DATA - BACKGROUND SUBTRACTION ###############"
print,'====================================================================='
answer=''
read,answer,prompt='ON-OFF or DITHERING (on/d): '
IF answer eq 'on' then begin
    step=2
    ENDIF ELSE BEGIN 
    step=1
ENDELSE

data=''
read,data,prompt='Give the DATA-xx.: '
name=''
datas=findfile(data+'*.fit')
n_data=n_elements(datas)
folder_name='Reduction_'+data
FILE_MKDIR,folder_name

;Reads the header from the telescope and the exptime.
simple=''
date=''
im_hdr=readfits(data+'_1.fit',hdr1)
exptime=FXPAR(hdr1,'INTTIME')
date=FXPAR(hdr1,'DATETIME')
hread=FXPAR(hdr1,'READS')
reps=FXPAR(hdr1,'REPS')

for i=0,n_data-2,step do begin 
    name1=data+'_'+strn(i+1)+'.fit'
    name2=data+'_'+strn(i+2)+'.fit'
    namedd=folder_name+'/'+data+'_'+strn(i+1)+'_BS.fit'
    d1=readfits(name1)
    d2=readfits(name2)
    dd=(d1-dark)/flat_f-(d2-dark)/flat_f
    writefits,namedd,dd
endfor

print,""
print,"####################### FIND DITHER-POSITIONS #######################"
print,'====================================================================='
x=FLTARR(100)
y=FLTARR(100)

for i=0,n_data-2,step do begin 
    namedd=folder_name+'/'+data+'_'+strn(i+1)+'_BS.fit'
    im=readfits(namedd)
    WINDOW, 0, XSIZE = 1024, YSIZE =1024
    tv,im
    cursor,x_i,y_i,/DEVICE
    cntrd,im,x_i,y_i,x_c,y_c,7 ;Gaussian Centroid of the Star
    x[i]=x_c
    y[i]=y_c
    print,'x=',x[i],'   y=',y[i]
endfor

print,""
print,"######################## SHIFTING THE IMAGES ########################"
print,'====================================================================='
for i=1,n_data-2,step do begin
    name_data_bs=folder_name+'/'+data+'_'+strn(i+1)+'_BS.fit'
    name_data_bs_n=folder_name+'/'+data+'_'+strn(i+1)+'_BS_new.fit'
    shift_x=x[0]-x[i]
    shift_y=y[0]-y[i]
    print,shift_x,shift_y
    data_bs=readfits(name_data_bs)
    data_bs_n=fshift(data_bs,shift_x,shift_y)
    writefits,name_data_bs_n,data_bs_n
endfor

print,""
print,"###################### Produce the Final Image ######################"
print,'====================================================================='
name_data_bs1=folder_name+'/'+data+'_1_BS.fit'
fin1=readfits(name_data_bs1)
sum=fin1
for i=1,n_data-2,step do begin
    name_data_bs_n=folder_name+'/'+data+'_'+strn(i+1)+'_BS_new.fit'
    fin=readfits(name_data_bs_n)
    sum=sum+fin
endfor
time=exptime*(n_data-1)
data_final=sum/time
i=where(finite(data_final) eq 0.)
data_final(i)=0.
writefits,folder_name+'/'+data+'_mosaic.fits',data_final,hdr

print,""
print,"########################### Create Header ###########################"
print,'====================================================================='
tel=''
instr=''
filt=''
read,tel,instr,ra,dec,sec,prompt='TELESCOPE(1), INSTRUMENT(2), RA(3), Dec(4), SECPIX(5): '
name_f=folder_name+'/'+data+'_mosaic.fits'
final_im=readfits(name_f,hdr2)
sxaddpar,hdr2,'TELESCOPE',tel,'Telescope facility'
sxaddpar,hdr2,'INSTRUME',instr,'Camera'
sxaddpar,hdr2,'OBJECT',data,'Object name and filter used'
sxaddpar,hdr2,'RA',ra,'[deg] Coordinates of the center for axis 1'
sxaddpar,hdr2,'Dec',dec,'[deg] Coordinates of the center for axis 2'
sxaddpar,hdr2,'EPOCH','J2000'
sxaddpar,hdr2,'DATETIME',date
sxaddpar,hdr2,'SECPIX1',sec,'[arcsec/px] Scale for axis 1'
sxaddpar,hdr2,'SECPIX2',sec,'[arcsec/px] Scale for axis 2'
sxaddpar,hdr2,'UNITS','counts/sec','Image units'
sxaddpar,hdr2,'READS',hread,'Read-outs'
sxaddpar,hdr2,'REPS',reps,'Repetitions'
sxaddpar,hdr2,'COMMENT','Produced using NIR_REDUCTION.pro (Bitsakis T. 2011)'
writefits,name_f,final_im,hdr2

print,'====================================================================='
print,"############################### READY ###############################"
print,'====================================================================='

print,"############################# PHOTOMETRY #############################"
print,'====================================================================='
quest=''
read,quest,prompt='Display on ATV(y/n): '
if quest eq 'y' then atv,data_final,header=hdr2

end


FUNCTION MYMEDIAN, a,b,c

a=a/median(a)
b=b/median(b)
c=c/median(c)

asize=size(a)
d=a

for i=0, 1023 do begin 
   for j=0, 1023 do begin
      d(i,j)=median([a(i,j), b(i,j), c(i,j)])
   endfor
endfor

return,d
end

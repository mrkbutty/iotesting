messagescan=nodisplay

# Host Definitions
#hd=default,vdbench=/bmhome/vdbench50407,user=root,shell=/usr/bin/ssh,jvms=8

#hd=lg1,system=172.23.80.163
#hd=lg2,system=172.23.80.164
#hd=lg3,system=172.23.80.166

#fsd=fsd1,anchor=/vdbtest,depth=2,width=5,files=10,size=(4k,20,512k,20,1m,20,5m,20,10m,15,1g,5),totalsize=3G
fsd=fsd1,anchor=/vdbtest2,depth=1,width=1,files=100,size=(1m),workingsetsize=50m

fwd=fwd_read,fsd=fsd1,operation=read,xfersize=256k,fileio=(sequential),fileselect=random,threads=8
fwd=fwd_read2,fsd=fsd1,operation=read,xfersize=256k,fileio=(sequential),fileselect=random,threads=8
#fwd=fwd_read3,fsd=fsd1,operation=read,xfersize=256k,fileio=(sequential),fileselect=random,threads=8
#fwd=fwd_read4,fsd=fsd1,operation=read,xfersize=256k,fileio=(sequential),fileselect=random,threads=8
#fwd=fwd_read5,fsd=fsd1,operation=read,xfersize=256k,fileio=(sequential),fileselect=random,threads=8
#fwd=fwd_read6,fsd=fsd1,operation=read,xfersize=256k,fileio=(sequential),fileselect=random,threads=8
#fwd=fwd_read7,fsd=fsd1,operation=read,xfersize=256k,fileio=(sequential),fileselect=random,threads=8
fwd=fwd_write,fsd=fsd1,operation=write,xfersize=256k,fileio=(seq,delete),fileselect=random,threads=8
#fwd=fwd_write2,fsd=fsd1,operation=write,xfersize=256k,fileio=(seq,delete),fileselect=random,threads=8
#fwd=fwd_write3,fsd=fsd1,operation=write,xfersize=256k,fileio=(seq,delete),fileselect=random,threads=8
rd=rd1,fwd=fwd*,fwdrate=1000,format=no,elapsed=20,interval=5,forthreads=(2,4,8)


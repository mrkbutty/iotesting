messagescan=nodisplay

# Host Definitions
#hd=default,vdbench=/bmhome/vdbench50407,user=root,shell=/usr/bin/ssh,jvms=8

#hd=lg1,system=172.23.80.163
#hd=lg2,system=172.23.80.164
#hd=lg3,system=172.23.80.166


#fsd=fsd1,anchor=/vdbtest,depth=2,width=5,files=10,size=(4k,20,512k,20,1m,20,5m,20,10m,15,1g,5),totalsize=3G

fsd=fsd1,anchor=/vdbtest2,depth=1,width=1,files=100,size=(1m),workingsetsize=50m
rd=rd1,fsd=fsd1,fwdrate=max,format=only
#rd=rd1,fsd=fsd1,fwdrate=max,format=restart

